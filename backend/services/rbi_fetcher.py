"""Fetch recent RBI circulars / releases from official RSS feeds."""
import re
from dataclasses import dataclass
from html import unescape
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from config import settings

USER_AGENT = "ComplianceAI/1.0 (+regulatory compliance research; contact: local-dev)"

# Compliance-relevant keywords (case-insensitive)
DEFAULT_KEYWORDS = [
    "master direction",
    "circular",
    "notification",
    "guideline",
    "digital lending",
    "kyc",
    "nbfc",
    "lending",
    "compliance",
    "regulation",
    "fair practice",
    "grievance",
    "disclosure",
    "priority sector",
    "cyber",
    "data protection",
]


@dataclass
class RBIItem:
    title: str
    link: str
    published: str
    summary_html: str
    pdf_urls: list[str]
    feed_name: str


class RBIFetcher:
    def __init__(self):
        self.feeds = settings.rbi_rss_feeds
        self.keywords = settings.rbi_sync_keywords or DEFAULT_KEYWORDS
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_recent_items(self, max_items: int = 15) -> list[RBIItem]:
        """Fetch and filter recent items from all configured RSS feeds."""
        seen_links: set[str] = set()
        items: list[RBIItem] = []

        for feed_url in self.feeds:
            for entry in self._parse_feed(feed_url):
                link = self._normalize_link(entry.get("link", ""))
                if not link or link in seen_links:
                    continue
                if not self._is_relevant(entry):
                    continue
                seen_links.add(link)
                summary = entry.get("summary", "") or entry.get("description", "")
                pdf_urls = self._extract_pdf_urls(summary, link)
                published = self._format_published(entry.get("published", ""))
                items.append(
                    RBIItem(
                        title=self._clean_title(entry.get("title", "RBI Release")),
                        link=link,
                        published=published,
                        summary_html=summary,
                        pdf_urls=pdf_urls,
                        feed_name=feed_url,
                    )
                )
                if len(items) >= max_items:
                    return items
        return items

    def _parse_feed(self, feed_url: str) -> list:
        try:
            parsed = feedparser.parse(
                feed_url,
                agent=USER_AGENT,
                request_headers={"User-Agent": USER_AGENT},
            )
            return list(parsed.entries or [])
        except Exception:
            return []

    def _is_relevant(self, entry: dict) -> bool:
        blob = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        return any(kw in blob for kw in self.keywords)

    def _extract_pdf_urls(self, html: str, page_link: str) -> list[str]:
        urls = set()
        for match in re.finditer(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.I):
            urls.add(urljoin(page_link, match.group(1)))
        for match in re.finditer(r"https?://rbidocs\.rbi\.org\.in[^\s\"']+\.pdf", html, re.I):
            urls.add(match.group(0))
        return list(urls)

    def _normalize_link(self, link: str) -> str:
        if not link:
            return ""
        if link.startswith("http://"):
            link = "https://" + link[7:]
        return link.strip()

    def _clean_title(self, title: str) -> str:
        title = re.sub(r"<[^>]+>", "", title)
        return unescape(title).strip() or "RBI Release"

    def _format_published(self, pub: str) -> str:
        if not pub:
            return datetime.utcnow().strftime("%Y-%m-%d")
        try:
            return parsedate_to_datetime(pub).strftime("%Y-%m-%d")
        except Exception:
            return datetime.utcnow().strftime("%Y-%m-%d")

    def download_pdf(self, url: str) -> bytes | None:
        try:
            resp = self.session.get(url, timeout=60)
            resp.raise_for_status()
            if "pdf" in resp.headers.get("content-type", "").lower() or url.lower().endswith(".pdf"):
                return resp.content
        except Exception:
            pass
        return None

    def fetch_page_text(self, url: str) -> str:
        """Fallback: scrape main content from RBI HTML page."""
        try:
            resp = self.session.get(url, timeout=45)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            main = soup.find("td", class_="td") or soup.find("article") or soup.body
            return main.get_text(separator="\n", strip=True) if main else ""
        except Exception:
            return ""

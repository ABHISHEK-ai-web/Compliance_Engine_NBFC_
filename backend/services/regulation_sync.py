"""Orchestrate RBI fetch + ingest + sync state tracking."""
import json
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from services.rbi_fetcher import RBIFetcher, RBIItem
from services.regulation_ingestion import (
    ingest_regulation_pdf,
    ingest_regulation_text,
    save_downloaded_file,
    strip_html,
)


class RegulationSyncService:
    def __init__(self):
        self.fetcher = RBIFetcher()
        self.state_path = Path(settings.rbi_sync_state_file)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "synced_urls": [],
            "last_sync_at": None,
            "history": [],
        }

    def save_state(self, state: dict):
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def get_status(self) -> dict:
        state = self.load_state()
        from services.vector_store import VectorStore

        vs = VectorStore()
        return {
            "last_sync_at": state.get("last_sync_at"),
            "total_synced_urls": len(state.get("synced_urls", [])),
            "regulations_indexed": vs.get_collection_count("regulations"),
            "last_run": state.get("history", [{}])[-1] if state.get("history") else None,
            "feeds": settings.rbi_rss_feeds,
        }

    def sync(self, max_items: int = None, force: bool = False) -> dict:
        max_items = max_items or settings.rbi_sync_max_items
        state = self.load_state()
        synced_urls = set(state.get("synced_urls", []))

        items = self.fetcher.fetch_recent_items(max_items=max_items)
        results = {
            "fetched": len(items),
            "new": 0,
            "skipped": 0,
            "failed": 0,
            "items": [],
        }

        for item in items:
            if item.link in synced_urls and not force:
                results["skipped"] += 1
                continue
            try:
                detail = self._ingest_item(item)
                if detail["status"] in ("success", "already_indexed"):
                    synced_urls.add(item.link)
                    if detail["status"] == "success":
                        results["new"] += 1
                    else:
                        results["skipped"] += 1
                else:
                    results["failed"] += 1
                results["items"].append(detail)
            except Exception as exc:
                results["failed"] += 1
                results["items"].append({
                    "title": item.title,
                    "source_url": item.link,
                    "status": "failed",
                    "error": str(exc),
                })

        now = datetime.now(timezone.utc).isoformat()
        state["synced_urls"] = list(synced_urls)[-500:]
        state["last_sync_at"] = now
        state.setdefault("history", []).append({
            "at": now,
            "new": results["new"],
            "skipped": results["skipped"],
            "failed": results["failed"],
            "fetched": results["fetched"],
        })
        state["history"] = state["history"][-20:]
        self.save_state(state)

        results["last_sync_at"] = now
        results["status"] = "completed"
        return results

    def _ingest_item(self, item: RBIItem) -> dict:
        meta = {
            "source_url": item.link,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "published_date": item.published,
            "title": item.title,
            "filename": f"RBI_{item.published}_{item.title[:60]}.txt",
            "feed_name": item.feed_name,
        }

        # Prefer PDF if linked in RSS/HTML
        for pdf_url in item.pdf_urls:
            content = self.fetcher.download_pdf(pdf_url)
            if content:
                path = save_downloaded_file(content, Path(pdf_url).name or "circular.pdf")
                out = ingest_regulation_pdf(
                    path,
                    filename=Path(path).name,
                    metadata_extra={**meta, "pdf_url": pdf_url},
                )
                if out["chunks_created"] > 0:
                    return {
                        "title": item.title,
                        "source_url": item.link,
                        "status": "success",
                        "format": "pdf",
                        "chunks_created": out["chunks_created"],
                    }

        # HTML from RSS description or page scrape
        text = strip_html(item.summary_html)
        if len(text) < 200:
            text = self.fetcher.fetch_page_text(item.link)
        if len(text) < 100:
            return {
                "title": item.title,
                "source_url": item.link,
                "status": "empty",
                "error": "No extractable text",
            }

        header = f"RBI Release: {item.title}\nPublished: {item.published}\nSource: {item.link}\n\n"
        out = ingest_regulation_text(
            header + text,
            title=item.title,
            metadata_extra=meta,
        )
        return {
            "title": item.title,
            "source_url": item.link,
            "status": "success" if out["chunks_created"] > 0 else "empty",
            "format": "html",
            "chunks_created": out["chunks_created"],
        }

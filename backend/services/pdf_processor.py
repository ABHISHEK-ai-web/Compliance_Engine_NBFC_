import fitz
import re
from config import settings


class PDFProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def extract_text(self, file_path: str) -> list[dict]:
        """Extract text from PDF with page-level metadata."""
        doc = fitz.open(file_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                pages.append({"page_number": page_num + 1, "text": text})
        doc.close()
        return pages

    def clean_text(self, text: str) -> str:
        """Remove excessive whitespace and artifacts from extracted text."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'[^\S\n]+', ' ', text)
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)

    def chunk_text(self, text: str, page_number: int) -> list[dict]:
        """Split text into overlapping chunks preserving context."""
        words = text.split()
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)

            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "word_count": len(chunk_words),
                })
                chunk_index += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks

    def process_pdf(self, file_path: str) -> list[dict]:
        """Full pipeline: extract -> clean -> chunk."""
        pages = self.extract_text(file_path)
        all_chunks = []
        global_chunk_index = 0

        for page_data in pages:
            cleaned_text = self.clean_text(page_data["text"])
            page_chunks = self.chunk_text(cleaned_text, page_data["page_number"])

            for chunk in page_chunks:
                chunk["chunk_index"] = global_chunk_index
                all_chunks.append(chunk)
                global_chunk_index += 1

        return all_chunks

"""
Document processing utilities for text extraction and chunking.
"""
import io
from typing import List, BinaryIO
from pathlib import Path
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class DocumentProcessor:
    """Process documents for ingestion into vector database."""

    def __init__(self):
        """Initialize document processor with text splitter."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """
        Extract text content from various file types.

        Args:
            file_path: Path to the file
            file_type: File extension (pdf, txt, md, doc, docx, xlsx, xls)

        Returns:
            Extracted text content

        Raises:
            ValueError: If file type is not supported
        """
        try:
            if file_type == "pdf":
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                return "\n\n".join([doc.page_content for doc in documents])

            elif file_type in ["txt", "md"]:
                loader = TextLoader(file_path)
                documents = loader.load()
                return documents[0].page_content

            elif file_type in ["doc", "docx"]:
                loader = UnstructuredWordDocumentLoader(file_path)
                documents = loader.load()
                return "\n\n".join([doc.page_content for doc in documents])

            elif file_type in ["xlsx", "xls"]:
                # Extract text from Excel files
                import pandas as pd
                df = pd.read_excel(file_path)

                # Convert DataFrame to text
                # Format: "Column1: value1. Column2: value2. ..."
                all_rows = []
                for idx, row in df.iterrows():
                    row_parts = []
                    for col in df.columns:
                        value = row[col]
                        # Skip empty values
                        if pd.notna(value) and str(value).strip():
                            row_parts.append(f"{col}: {value}")
                    if row_parts:
                        all_rows.append(". ".join(row_parts) + ".")

                return "\n\n".join(all_rows)

            elif file_type == "json":
                # Extract text from JSON files
                import json

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert JSON to readable text
                # Handle array of objects specially (common format)
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    # Array of objects - format each object nicely
                    text_parts = []
                    for idx, item in enumerate(data):
                        item_lines = []
                        for key, value in item.items():
                            if value and str(value).strip():
                                item_lines.append(f"{key}: {value}")
                        if item_lines:
                            text_parts.append("\n".join(item_lines))
                    return "\n\n".join(text_parts)
                else:
                    # Generic JSON - use recursive method
                    return self._json_to_text(data)

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            raise

    def extract_text_from_url(self, url: str) -> str:
        """
        Fetch and extract text from URL.

        Args:
            url: URL to fetch

        Returns:
            Extracted text content

        Raises:
            requests.RequestException: If URL fetch fails
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Simple text extraction - can be enhanced with BeautifulSoup
            content_type = response.headers.get("content-type", "")

            if "text" in content_type or "html" in content_type:
                return response.text
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            raise

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def process_document(self, content: str) -> List[str]:
        """
        Process document content into chunks.

        Args:
            content: Raw document content

        Returns:
            List of text chunks
        """
        # Clean content
        content = content.strip()

        if not content:
            raise ValueError("Document content is empty")

        # Chunk the content
        chunks = self.chunk_text(content)

        return chunks

    def _json_to_text(self, data, prefix="") -> str:
        """
        Convert JSON data to readable text format.

        Args:
            data: JSON data (dict, list, or primitive)
            prefix: Current key prefix for nested objects

        Returns:
            Formatted text string
        """
        lines = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, (dict, list)):
                    lines.append(self._json_to_text(value, current_key))
                else:
                    lines.append(f"{current_key}: {value}")

        elif isinstance(data, list):
            for idx, item in enumerate(data):
                current_key = f"{prefix}[{idx}]" if prefix else f"item[{idx}]"

                if isinstance(item, (dict, list)):
                    lines.append(self._json_to_text(item, current_key))
                else:
                    lines.append(f"{current_key}: {item}")
        else:
            return f"{prefix}: {data}" if prefix else str(data)

        return "\n".join(lines)


# Global processor instance
document_processor = DocumentProcessor()

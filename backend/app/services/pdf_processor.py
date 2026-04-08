"""
PDF text extraction service.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pdfplumber
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for extracting text from PDF documents."""

    def __init__(self):
        """Initialize the PDF processor."""
        pass

    def extract_text_pdfplumber(self, file_path: Path) -> str:
        """
        Extract text using pdfplumber (better for structured tables).

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        text_content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from page
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {page_num} ---\n{page_text}")

                    # Try to extract tables
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            table_text = self._format_table(table)
                            text_content.append(
                                f"[Table {page_num}.{table_idx + 1}]\n{table_text}"
                            )

            return "\n\n".join(text_content)

        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise

    def extract_text_pypdf2(self, file_path: Path) -> str:
        """
        Extract text using PyPDF2 as fallback.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        text_content = []

        try:
            reader = PdfReader(str(file_path))
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text}")

            return "\n\n".join(text_content)

        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            raise

    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from PDF using best available method.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        # Try pdfplumber first (better for complex layouts)
        try:
            text = self.extract_text_pdfplumber(file_path)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")

        # Fallback to PyPDF2
        try:
            text = self.extract_text_pypdf2(file_path)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 also failed: {e}")

        # Last resort: combined approach
        combined = []
        try:
            combined.append(self.extract_text_pdfplumber(file_path))
        except Exception:
            pass

        try:
            combined.append(self.extract_text_pypdf2(file_path))
        except Exception:
            pass

        result = "\n\n".join(combined)
        if not result.strip():
            raise ValueError(f"Could not extract text from PDF: {file_path}")

        return result

    def _format_table(self, table: List[List[str]]) -> str:
        """
        Format table data as readable text.

        Args:
            table: 2D list of table cells

        Returns:
            Formatted table string
        """
        if not table:
            return ""

        # Calculate column widths
        col_widths = []
        for row in table:
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                if col_idx >= len(col_widths):
                    col_widths.append(len(cell_str))
                else:
                    col_widths[col_idx] = max(col_widths[col_idx], len(cell_str))

        # Format each row
        lines = []
        for row in table:
            formatted_row = []
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                width = col_widths[col_idx] if col_idx < len(col_widths) else 20
                formatted_row.append(cell_str.ljust(width))
            lines.append(" | ".join(formatted_row))

        # Add separator after header (assuming first row is header)
        if len(lines) > 1:
            separator = "-+-".join("-" * w for w in col_widths[:len(lines[0].split(" | "))])
            lines.insert(1, separator)

        return "\n".join(lines)

    def get_page_count(self, file_path: Path) -> int:
        """
        Get the number of pages in a PDF.

        Args:
            file_path: Path to the PDF file

        Returns:
            Number of pages
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except Exception:
            try:
                reader = PdfReader(str(file_path))
                return len(reader.pages)
            except Exception as e:
                logger.error(f"Error getting page count: {e}")
                return 0

    def validate_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a PDF file and return metadata.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with validation results and metadata
        """
        result = {
            "valid": False,
            "page_count": 0,
            "file_size": 0,
            "error": None,
        }

        try:
            # Check if file exists
            if not file_path.exists():
                result["error"] = "File does not exist"
                return result

            # Check file size
            result["file_size"] = file_path.stat().st_size

            # Get page count
            result["page_count"] = self.get_page_count(file_path)

            # Try to extract at least some text
            text = self.extract_text(file_path)
            if text and len(text.strip()) > 50:
                result["valid"] = True
            else:
                result["error"] = "No readable text found in PDF"

        except Exception as e:
            result["error"] = str(e)

        return result


# Singleton instance
pdf_processor = PDFProcessor()

"""PDF reading utilities."""

import base64


def read_pdf_as_base64(file_path: str) -> str:
    """Read a PDF file and return it as a base64-encoded string.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Base64-encoded PDF content.
    """
    with open(file_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

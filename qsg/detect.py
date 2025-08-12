from pathlib import Path
from typing import Optional, Tuple


def detect_language_and_provider(src_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Very simple heuristics to guess language and target provider.

    Returns a tuple of (language, provider). If detection fails, both values
    are ``None``. This is a placeholder for more robust static analysis.
    """
    text = Path(src_path).read_text(encoding="utf-8", errors="ignore")
    if "qiskit" in text:
        return "python", "ibm"
    if "cirq" in text:
        return "python", "google"
    if src_path.endswith(".qs"):
        return "qsharp", "azure"
    return None, None

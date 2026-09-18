"""Local-first notes for LLM agents."""

__version__ = "1.0.4"

from .store import Entry, FileNotebookStore, NoteStore

__all__ = ["Entry", "FileNotebookStore", "NoteStore", "__version__"]

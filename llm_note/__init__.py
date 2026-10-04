"""Local-first notes for LLM agents."""

__version__ = "1.0.5"

from .store import Entry, FileNotebookStore, NoteStore

__all__ = ["Entry", "FileNotebookStore", "NoteStore", "__version__"]

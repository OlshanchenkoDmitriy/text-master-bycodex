from dataclasses import dataclass, field
import time
import threading
from typing import Callable, Dict, List

@dataclass
class Document:
    id: int
    text: str
    last_modified: float = field(default_factory=lambda: 0.0)

class DocumentDao:
    """In-memory DAO storing documents."""
    def __init__(self):
        self._docs: Dict[int, Document] = {}
        self._lock = threading.Lock()

    def update_document(self, document: Document) -> None:
        with self._lock:
            document.last_modified = time.time()
            self._docs[document.id] = Document(document.id, document.text, document.last_modified)

    def get_history(self) -> List[Document]:
        with self._lock:
            return sorted(self._docs.values(), key=lambda d: d.last_modified, reverse=True)

class TextWatcher:
    """Debounced text watcher triggering callback after inactivity."""
    def __init__(self, callback: Callable[[str], None], debounce_ms: int = 300):
        self._callback = callback
        self._debounce = debounce_ms / 1000.0
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def on_text_changed(self, new_text: str) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce, self._callback, args=(new_text,))
            self._timer.start()

class DocumentEditor:
    """Editor that autosaves document text with debounce."""
    def __init__(self, document: Document, dao: DocumentDao, debounce_ms: int = 300):
        self.document = document
        self.dao = dao
        self._watcher = TextWatcher(self._on_debounced_change, debounce_ms)

    def _on_debounced_change(self, new_text: str) -> None:
        self.document.text = new_text
        self.dao.update_document(self.document)

    def input_text(self, new_text: str) -> None:
        self._watcher.on_text_changed(new_text)

import time
from autosave import Document, DocumentDao, DocumentEditor

def test_autosave_updates_document_and_last_modified():
    dao = DocumentDao()
    doc = Document(id=1, text="")
    editor = DocumentEditor(doc, dao, debounce_ms=50)
    editor.input_text("hello")
    time.sleep(0.1)
    history = dao.get_history()
    assert len(history) == 1
    saved = history[0]
    assert saved.text == "hello"
    assert saved.last_modified > 0

def test_history_sorted_by_last_modified():
    dao = DocumentDao()
    doc1 = Document(id=1, text="one")
    doc2 = Document(id=2, text="two")
    dao.update_document(doc1)
    time.sleep(0.05)
    dao.update_document(doc2)
    history = dao.get_history()
    assert [d.id for d in history] == [2, 1]

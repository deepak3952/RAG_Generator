import pytest
from app.core.ingestion import parse_and_chunk_file, SUPPORTED_EXTENSIONS

def test_parse_txt_file():
    """Test parsing and chunking of plain text files."""
    sample_text = b"This is a test document for the RAG Generator. " * 50
    filename = "test_document.txt"
    
    chunks = parse_and_chunk_file(sample_text, filename)
    
    assert len(chunks) > 0
    assert chunks[0].metadata["source_filename"] == filename
    assert "test document" in chunks[0].page_content

def test_parse_markdown_file():
    """Test parsing of markdown files."""
    sample_md = b"# Title\n\nThis is markdown content used for testing dynamic RAG ingestion."
    filename = "notes.md"
    
    chunks = parse_and_chunk_file(sample_md, filename)
    
    assert len(chunks) > 0
    assert chunks[0].metadata["source_filename"] == filename

def test_unsupported_file_extension():
    """Test that unsupported file types raise a ValueError."""
    invalid_content = b"Binary or unsupported data"
    filename = "archive.zip"
    
    with pytest.raises(ValueError) as exc_info:
        parse_and_chunk_file(invalid_content, filename)
    
    assert "Unsupported file extension" in str(exc_info.value)

def test_supported_extensions_constant():
    """Verify supported extensions list."""
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".txt" in SUPPORTED_EXTENSIONS
    assert ".docx" in SUPPORTED_EXTENSIONS
    assert ".md" in SUPPORTED_EXTENSIONS

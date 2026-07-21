from rag_bsf.text_processing import clean_markdown, split_by_sections, split_long_text


def test_clean_markdown_keeps_heading_text():
    raw = "# Title\n\nThis is **important** and [linked](https://example.com)."

    cleaned = clean_markdown(raw)

    assert "Title" in cleaned
    assert "important" in cleaned
    assert "linked" in cleaned


def test_split_by_sections_uses_headings():
    sections = split_by_sections("# One\nText\n\n## Two\nMore")

    assert [section[0] for section in sections] == ["One", "Two"]


def test_split_long_text_creates_chunks():
    chunks = split_long_text("A" * 1000, target_chars=300, overlap=50)

    assert len(chunks) > 1
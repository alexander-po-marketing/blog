from divi2gutenberg.html_to_blocks import html_to_blocks


def test_simple_html_to_blocks():
    html = "<h2>Title</h2><p>Hello</p><ul><li>A</li><li>B</li></ul>"
    blocks = html_to_blocks(html, {})
    assert "<!-- wp:heading" in blocks
    assert "<h2>Title</h2>" in blocks
    assert "<!-- wp:paragraph" in blocks
    assert "<p>Hello</p>" in blocks
    assert "<!-- wp:list" in blocks
    assert "<ul><li>A</li><li>B</li></ul>" in blocks


def test_html_to_blocks_divider_and_line_breaks():
    html = "<p>Line1<br/>Line2</p><hr/>"
    blocks = html_to_blocks(html, {})
    assert "<br/>" in blocks
    assert "<!-- wp:separator" in blocks

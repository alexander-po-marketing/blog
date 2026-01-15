from divi2gutenberg.divi_shortcodes import extract_divi_html, parse_shortcodes


def test_nested_shortcodes_parse():
    text = "[et_pb_section][et_pb_row][et_pb_text]<p>Hello</p>[/et_pb_text][/et_pb_row][/et_pb_section]"
    parts = parse_shortcodes(text)
    assert len(parts) == 1
    section = parts[0]
    assert section.name == "et_pb_section"
    assert section.parts[0].name == "et_pb_row"
    assert section.parts[0].parts[0].name == "et_pb_text"


def test_line_break_holder_and_divider():
    text = "[et_pb_text]Line1[et_pb_line_break_holder]Line2[/et_pb_text]"
    html, counts = extract_divi_html(text)
    assert "Line1" in html
    assert "<br/>" in html
    assert "Line2" in html
    assert counts["et_pb_text"] == 1
    assert counts["et_pb_line_break_holder"] == 1

from rich.style import Style
from textual.widgets.text_area import TextAreaTheme
from textual.widgets import TextArea


_NORD = TextAreaTheme(
    name="nord",
    base_style=Style(color="#D8DEE9", bgcolor="#2E3440"),
    gutter_style=Style(color="#4C566A", bgcolor="#2E3440"),
    cursor_style=Style(color="#2E3440", bgcolor="#D8DEE9"),
    cursor_line_style=Style(bgcolor="#3B4252"),
    cursor_line_gutter_style=Style(color="#4C566A", bgcolor="#3B4252"),
    bracket_matching_style=Style(bgcolor="#88C0D0", bold=True),
    selection_style=Style(bgcolor="#434C5E"),
    syntax_styles={
        "string": Style(color="#A3BE8C"),
        "string.documentation": Style(color="#A3BE8C"),
        "comment": Style(color="#616E88"),
        "keyword": Style(color="#81A1C1"),
        "operator": Style(color="#81A1C1"),
        "repeat": Style(color="#81A1C1"),
        "exception": Style(color="#81A1C1"),
        "include": Style(color="#81A1C1"),
        "keyword.function": Style(color="#81A1C1"),
        "keyword.return": Style(color="#81A1C1"),
        "keyword.operator": Style(color="#81A1C1"),
        "conditional": Style(color="#81A1C1"),
        "number": Style(color="#B48EAD"),
        "float": Style(color="#B48EAD"),
        "class": Style(color="#8FBCBB"),
        "type.class": Style(color="#8FBCBB"),
        "function": Style(color="#8FBCBB"),
        "function.call": Style(color="#8FBCBB"),
        "method": Style(color="#8FBCBB"),
        "method.call": Style(color="#8FBCBB"),
        "boolean": Style(color="#81A1C1", italic=True),
        "constant.builtin": Style(color="#81A1C1", italic=True),
        "json.null": Style(color="#81A1C1", italic=True),
        "regex.punctuation.bracket": Style(color="#81A1C1"),
        "regex.operator": Style(color="#81A1C1"),
        "html.end_tag_error": Style(color="#BF616A", underline=True),
        "tag": Style(color="#81A1C1"),
        "yaml.field": Style(color="#81A1C1", bold=True),
        "json.label": Style(color="#81A1C1", bold=True),
        "toml.type": Style(color="#81A1C1"),
        "toml.datetime": Style(color="#B48EAD"),
        "heading": Style(color="#81A1C1", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#81A1C1", underline=True),
        "inline_code": Style(color="#A3BE8C"),
    },
)


def get_text_area(_id: str) -> TextArea:
    w = TextArea.code_editor(text="{}", language="json", id=_id)
    w.register_theme(_NORD)
    w.theme = "nord"
    return w

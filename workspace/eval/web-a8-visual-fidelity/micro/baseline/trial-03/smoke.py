from html.parser import HTMLParser
from pathlib import Path
class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.css = []
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            assert attributes["id"] not in self.ids
            self.ids.add(attributes["id"])
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.css.append(attributes["href"])
doc = Document()
doc.feed(Path("app.html").read_text())
assert "person-name" in doc.ids
assert doc.css == ["tokens.css", "design-system.css", "feature.css"]
for css in doc.css:
    assert Path(css).is_file(), css
print("PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions")

"""
Apply OpenDyslexic font to an HTML file by injecting a <style> tag.

Output: same directory as input, filename: <basename>_dyslexia.html

No BeautifulSoup: uses Python's stdlib html.parser.
"""

from __future__ import annotations

import argparse
import html
import os
import sys
from html.parser import HTMLParser
from typing import List, Tuple
from urllib.parse import urljoin

try:
    import cssutils  # optional: used only for “linked CSS inspection”
except Exception:  # pragma: no cover
    cssutils = None


STYLE_TAG_HTML = """
<style>
/* OpenDyslexic accessibility override */
@font-face {
    font-family: 'OpenDyslexic';
    src: url('https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/woff/OpenDyslexic-Regular.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}

@font-face {
    font-family: 'OpenDyslexic';
    src: url('https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/woff/OpenDyslexic-Bold.woff') format('woff');
    font-weight: bold;
    font-style: normal;
}

/* Apply globally but safely */
body, p, span, li, a, td, th, div {
    font-family: 'OpenDyslexic', Arial, sans-serif !important;
}
</style>
""".strip()


class LinkedCSSExtractor(HTMLParser):
    """Extract hrefs from <link rel="stylesheet" href="..."> tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        if tag.lower() != "link":
            return
        attr_map = {k.lower(): v for k, v in attrs}
        rel = (attr_map.get("rel") or "").lower()
        if "stylesheet" not in rel.split():
            return
        href = attr_map.get("href")
        if href:
            self.hrefs.append(href)


def extract_linked_css(html_text: str, base_dir: str) -> List[str]:
    """Read linked CSS files (local paths only) and return their raw contents."""
    parser = LinkedCSSExtractor()
    parser.feed(html_text)

    css_texts: List[str] = []
    for href in parser.hrefs:
        css_path = urljoin(base_dir + "/", href)
        if not os.path.exists(css_path):
            continue
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_texts.append(f.read())
        except Exception as e:
            print(f"[warn] couldn't read CSS file {css_path}: {e}")
    return css_texts


class HeadStyleInjector(HTMLParser):
    """Rebuild HTML while injecting a style tag before </head> (or at end if no head)."""

    def __init__(self, style_tag_html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.style_tag_html = style_tag_html
        self.parts: List[str] = []
        self.inserted = False

    def _attrs_to_string(self, attrs: List[Tuple[str, str | None]]) -> str:
        out: List[str] = []
        for k, v in attrs:
            k_l = k.lower()
            if v is None:
                out.append(f" {k_l}")
            else:
                out.append(f' {k_l}="{html.escape(v, quote=True)}"')
        return "".join(out)

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        self.parts.append(f"<{tag_l}{self._attrs_to_string(attrs)}>")

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        self.parts.append(f"<{tag_l}{self._attrs_to_string(attrs)} />")

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l == "head" and not self.inserted:
            self.parts.append(self.style_tag_html)
            self.inserted = True
        self.parts.append(f"</{tag_l}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}?>")

    def get_html(self) -> str:
        if not self.inserted:
            self.parts.append(self.style_tag_html)
        return "".join(self.parts)


def parse_args() -> str:
    parser = argparse.ArgumentParser(prog="dyslexia.py", description="Inject OpenDyslexic CSS into an HTML file.")
    parser.add_argument("input_html", help="Input HTML file path")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_html)
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)
    return input_path


def main() -> None:
    input_path = parse_args()
    base_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(base_dir, f"{base_name}.dyslexia.html")

    with open(input_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    # Optional inspection of linked CSS. (We don't currently use the results.)
    if cssutils is not None:
        _css_texts = extract_linked_css(html_text, base_dir)
        for css in _css_texts:
            try:
                sheet = cssutils.parseString(css)
                for rule in sheet:
                    if rule.type == rule.STYLE_RULE and rule.style.getPropertyValue("font-family"):
                        pass
            except Exception:
                # If cssutils can’t parse a stylesheet, we just ignore it.
                pass

    injector = HeadStyleInjector(style_tag_html=STYLE_TAG_HTML)
    injector.feed(html_text)
    out_html = injector.get_html()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    print(f"✔ OpenDyslexic applied. Output: {output_path}")


if __name__ == "__main__":
    main()
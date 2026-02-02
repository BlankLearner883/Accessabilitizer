from bs4 import BeautifulSoup
import cssutils
import sys
import os
from urllib.parse import urljoin

if len(sys.argv) < 2:
    print("Usage: python dyslexia.py [input.html]")
    sys.exit(1)

input_path = sys.argv[1]
base_dir = os.path.dirname(os.path.abspath(input_path))

# ---------------------------
# Load HTML
# ---------------------------
with open(input_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# ---------------------------
# Read linked CSS files
# ---------------------------
css_texts = []

for link in soup.find_all("link", rel="stylesheet"):
    href = link.get("href")
    if not href:
        continue

    css_path = urljoin(base_dir + "/", href)

    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as css_file:
                css_texts.append(css_file.read())
        except Exception as e:
            print(f"Failed to read CSS file {css_path}: {e}")

# ---------------------------
# Parse CSS (optional analysis)
# ---------------------------
for css in css_texts:
    sheet = cssutils.parseString(css)
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            if rule.style.getPropertyValue("font-family"):
                pass  # you can inspect or log existing fonts here

# ---------------------------
# Inject OpenDyslexic override
# ---------------------------
style_tag = soup.new_tag("style")

style_tag.string = """
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
"""

# Ensure it loads LAST
if soup.head:
    soup.head.append(style_tag)
else:
    soup.insert(0, style_tag)

# ---------------------------
# Write output
# ---------------------------
with open("modified.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✔ OpenDyslexic applied with CSS-aware processing")
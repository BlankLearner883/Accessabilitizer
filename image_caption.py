"""
Add BLIP-generated captions to images referenced in an HTML file.
Output: same directory as input, filename with _captioned before extension.
"""

from __future__ import annotations

import argparse
import html
import os
import sys
from html.parser import HTMLParser
from typing import Dict, List, Tuple

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch


def parse_args() -> tuple[str, bool]:
    parser = argparse.ArgumentParser(
        prog="image_caption.py",
        description="Add BLIP-generated captions after each <img src=...> in an HTML file.",
    )
    parser.add_argument("input_html", help="Input HTML file path")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Apply changes without prompting for confirmation.",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_html)
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)
    return input_path, bool(args.yes)


def caption_image(processor, model, image_path: str) -> str:
    """Generate a caption for the image at image_path. Returns caption or error string."""
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        with torch.no_grad():
            ids = model.generate(**inputs)
        return processor.decode(ids[0], skip_special_tokens=True)
    except Exception as e:
        return f"[ERROR: {e}]"


def planned_changes_summary(input_path: str, img_srcs: List[str]) -> str:
    base, ext = os.path.splitext(input_path)
    output_path = base + "_captioned" + (ext or ".html")

    lines: List[str] = []
    lines.append("Planned changes:")
    lines.append(f"- Input: {input_path}")
    lines.append(f"- Output: {output_path}")
    lines.append(f"- Images found: {len(img_srcs)}")
    lines.append('- For each image (<img src="...">), insert a <p class="caption"> right after it.')
    lines.append("- Image src list:")
    if not img_srcs:
        lines.append("  (none)")
    else:
        for s in img_srcs:
            lines.append(f'  - {s}')
    return "\n".join(lines)


def confirm_apply(summary: str) -> bool:
    print(summary)
    resp = input("\nApply these changes? [y/N]: ").strip().lower()
    return resp in {"y", "yes"}


class ImgSrcExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.img_srcs: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr_map = {k.lower(): v for k, v in attrs}
        src = attr_map.get("src")
        if src:
            self.img_srcs.append(src)

    def handle_startendtag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        # e.g. <img ... />
        self.handle_starttag(tag, attrs)


def extract_img_srcs(html_text: str) -> List[str]:
    parser = ImgSrcExtractor()
    parser.feed(html_text)
    return parser.img_srcs


def resolve_image_path(html_file_path: str, img_src: str) -> str:
    html_dir = os.path.dirname(os.path.abspath(html_file_path))
    # Common cases: relative paths ("images/a.jpg") or root-relative paths ("/images/a.jpg")
    if os.path.isabs(img_src):
        return img_src
    if img_src.startswith("/"):
        return os.path.normpath(os.path.join(html_dir, img_src.lstrip("/")))
    return os.path.normpath(os.path.join(html_dir, img_src))


class CaptionInjector(HTMLParser):
    """Rebuilds HTML while inserting captions after each <img> tag."""

    # HTML void elements list (won't have end tags)
    VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, caption_by_src: Dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.caption_by_src = caption_by_src
        self.parts: List[str] = []

    def _attrs_to_string(self, attrs: List[tuple[str, str | None]]) -> str:
        out = []
        for k, v in attrs:
            k_l = k.lower()
            if v is None:
                out.append(f" {k_l}")
            else:
                out.append(f' {k_l}="{html.escape(v, quote=True)}"')
        return "".join(out)

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        attrs_str = self._attrs_to_string(attrs)
        self.parts.append(f"<{tag_l}{attrs_str}>")

        if tag_l == "img":
            attr_map = {k.lower(): v for k, v in attrs}
            src = attr_map.get("src") or ""
            caption = self.caption_by_src.get(src, "")
            self.parts.append(f'<p class="caption">{html.escape(caption)}</p>')

        # For void elements, HTMLParser might still call endtag for some malformed HTML.
        # We don't attempt to suppress end tags; we only ensure we insert caption after <img>.

    def handle_startendtag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        # e.g. <img ... />
        tag_l = tag.lower()
        attrs_str = self._attrs_to_string(attrs)
        self.parts.append(f"<{tag_l}{attrs_str} />")
        if tag_l == "img":
            attr_map = {k.lower(): v for k, v in attrs}
            src = attr_map.get("src") or ""
            caption = self.caption_by_src.get(src, "")
            self.parts.append(f'<p class="caption">{html.escape(caption)}</p>')

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag.lower()}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        # processing instruction: <? ... ?>
        self.parts.append(f"<?{data}?>")

    def get_html(self) -> str:
        return "".join(self.parts)


def main() -> None:
    input_path, apply_without_prompt = parse_args()

    with open(input_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    img_srcs = extract_img_srcs(html_text)
    summary = planned_changes_summary(input_path, img_srcs)
    if not apply_without_prompt:
        if not confirm_apply(summary):
            print("\nCancelled. No output file written.")
            return

    # If there are no images, there's nothing to do.
    if not img_srcs:
        print("\nNo <img src=...> tags found; no output written.")
        return

    # Generate captions (compute once per unique src).
    unique_srcs: List[str] = []
    seen: set[str] = set()
    for s in img_srcs:
        if s not in seen:
            seen.add(s)
            unique_srcs.append(s)

    print("Loading BLIP model...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print("Model loaded.")

    caption_by_src: Dict[str, str] = {}
    for src in unique_srcs:
        image_path = resolve_image_path(input_path, src)
        caption = caption_image(processor, model, image_path)
        caption_by_src[src] = caption
        print(f"{src} → {caption}")

    injector = CaptionInjector(caption_by_src=caption_by_src)
    injector.feed(html_text)
    out_html = injector.get_html()

    base, ext = os.path.splitext(input_path)
    output_path = base + "_captioned" + (ext or ".html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    print(f"\n✔ Done! Updated HTML saved as:\n{output_path}")


if __name__ == "__main__":
    main()

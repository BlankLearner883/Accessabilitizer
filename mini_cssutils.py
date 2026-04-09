"""
mini_cssutils.py — stdlib-only drop-in for the cssutils subset used in dyslexia.py.

Replaces:
    import cssutils
    sheet = cssutils.parseString(css_text)
    for rule in sheet:
        if rule.type == rule.STYLE_RULE and rule.style.getPropertyValue("font-family"):
            ...

Only the API surface actually consumed by the project is implemented:
    parseString(css)  → Stylesheet (iterable of Rule objects)
    Rule.type         → int  (compare with Rule.STYLE_RULE / Rule.AT_RULE)
    Rule.STYLE_RULE   → 1   (class-level constant)
    Rule.AT_RULE      → 4   (class-level constant; covers @font-face, @media, …)
    Rule.selectorText → str  selector(s), e.g. "body, p"
    Rule.style        → Style
    Style.getPropertyValue(name) → str value, or "" if absent
    Style.cssText     → raw declaration block text (for debugging)

Parsing is deliberately lenient: malformed CSS is skipped, not raised.
"""

from __future__ import annotations

import re
from typing import Iterator


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Strip C-style /* … */ block comments (non-greedy, DOTALL).
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# Match one CSS rule: <anything-that-isn't-{> { <content> }
# Handles nested braces one level deep (e.g. @media { .x { … } }).
_RULE_RE = re.compile(
    r"""
    (?P<prelude>[^{]*?)   # selector or at-rule prelude (text before {)
    \{
    (?P<body>
        (?:[^{}]          # ordinary chars
        |\{[^{}]*}       # one level of nested braces (e.g. @font-face src)
        )*
    )
    }
    """,
    re.VERBOSE | re.DOTALL,
)

# Split a declaration block into individual "property: value" pairs.
# Handles values that contain parentheses (e.g. url(...), format(...)).
_DECL_RE = re.compile(
    r"""
    (?P<prop>[\w-]+)      # property name
    \s*:\s*
    (?P<value>
        (?:[^;()\n]       # plain chars
        |\([^)]*\)        # parenthesised segment: url(...) format(...)
        )+
    )
    """,
    re.VERBOSE,
)

# Detect at-rules: prelude starts with "@keyword"
_AT_RULE_RE = re.compile(r"^\s*@([\w-]+)", re.ASCII)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class Style:
    """Ordered mapping of CSS property → value for one rule's declaration block."""

    def __init__(self, declarations: dict[str, str], raw: str) -> None:
        self._decls = declarations  # lower-cased property names
        self.cssText = raw.strip()

    def getPropertyValue(self, name: str) -> str:
        """Return the value for *name*, or '' if the property is absent."""
        return self._decls.get(name.lower().strip(), "")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Style({self._decls!r})"


class Rule:
    """One parsed CSS rule (style rule or at-rule)."""

    # Mirror the cssutils integer constants used in the project.
    STYLE_RULE: int = 1
    CHARSET_RULE: int = 2
    IMPORT_RULE: int = 3
    MEDIA_RULE: int = 4
    FONT_FACE_RULE: int = 5
    PAGE_RULE: int = 6
    NAMESPACE_RULE: int = 10
    AT_RULE: int = 4  # generic alias used when the exact @-keyword doesn't matter

    def __init__(self, rule_type: int, selector: str, style: Style) -> None:
        self.type = rule_type
        self.selectorText = selector.strip()
        self.style = style

    def __repr__(self) -> str:  # pragma: no cover
        kind = "STYLE" if self.type == self.STYLE_RULE else f"AT({self.type})"
        return f"Rule({kind}, {self.selectorText!r})"


class Stylesheet:
    """Iterable collection of Rule objects produced by parseString()."""

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    def __iter__(self) -> Iterator[Rule]:
        return iter(self._rules)

    def __len__(self) -> int:
        return len(self._rules)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Stylesheet({len(self._rules)} rules)"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_declarations(block: str) -> dict[str, str]:
    """Parse a CSS declaration block into {property: value} (last-write wins)."""
    decls: dict[str, str] = {}
    for m in _DECL_RE.finditer(block):
        prop = m.group("prop").lower().strip()
        value = m.group("value").strip().rstrip(";").strip()
        decls[prop] = value
    return decls


_AT_TYPE_MAP: dict[str, int] = {
    "charset":   Rule.CHARSET_RULE,
    "import":    Rule.IMPORT_RULE,
    "media":     Rule.MEDIA_RULE,
    "font-face": Rule.FONT_FACE_RULE,
    "page":      Rule.PAGE_RULE,
    "namespace": Rule.NAMESPACE_RULE,
}


def _classify_rule(prelude: str, body: str) -> Rule:
    """Build a Rule from a matched prelude + body pair."""
    at_match = _AT_RULE_RE.match(prelude)
    if at_match:
        keyword = at_match.group(1).lower()
        rule_type = _AT_TYPE_MAP.get(keyword, Rule.AT_RULE)
        style = Style(_parse_declarations(body), body)
        return Rule(rule_type, prelude.strip(), style)

    # Ordinary selector { declarations }
    style = Style(_parse_declarations(body), body)
    return Rule(Rule.STYLE_RULE, prelude.strip(), style)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parseString(css: str) -> Stylesheet:
    """
    Parse a CSS string and return a Stylesheet (iterable of Rule objects).

    Mirrors ``cssutils.parseString(css)``.  Never raises; malformed input
    is silently skipped.
    """
    if not isinstance(css, str):
        try:
            css = css.decode("utf-8", errors="replace")
        except Exception:
            return Stylesheet([])

    # Strip comments so they don't confuse the block-finder.
    cleaned = _COMMENT_RE.sub(" ", css)

    rules: list[Rule] = []
    for m in _RULE_RE.finditer(cleaned):
        prelude = m.group("prelude")
        body = m.group("body")
        # Skip empty / whitespace-only preludes (can happen at file start).
        if not prelude.strip():
            continue
        try:
            rules.append(_classify_rule(prelude, body))
        except Exception:
            pass  # be lenient; skip unparseable rules

    return Stylesheet(rules)

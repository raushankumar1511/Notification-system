"""Safe ``{{variable}}`` substitution.

Deliberately avoids ``str.format`` (throws on stray braces, exposes attribute/index
access) and full template engines. Only whitelisted keys from the provided context are
substituted; unknown placeholders are left as a visible ``[key]`` marker so a missing
value never crashes a send and is obvious in testing.
"""

import html
import re

_PLACEHOLDER = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def render(text: str, context: dict, *, escape_html: bool = False) -> str:
    if not text:
        return ""

    def repl(match: "re.Match[str]") -> str:
        key = match.group(1)
        if key in context:
            value = context[key]
            value = "" if value is None else str(value)
            return html.escape(value) if escape_html else value
        return f"[{key}]"

    return _PLACEHOLDER.sub(repl, text)


def extract_variables(text: str) -> list[str]:
    """Return the distinct placeholder names used in ``text`` (in first-seen order)."""
    seen: list[str] = []
    for match in _PLACEHOLDER.finditer(text or ""):
        key = match.group(1)
        if key not in seen:
            seen.append(key)
    return seen

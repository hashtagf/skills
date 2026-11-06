"""Shared sRGB color helpers for the token scripts (export_tokens, design_md, design_md_check, code_extract).

hex_rgb accepts #rgb, #rgba, #rrggbb and #rrggbbaa (alpha is ignored). WCAG 2.x luminance and contrast.
Standard library only.
"""
import re

_HEX = re.compile(r"^#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def is_hex(h):
    return isinstance(h, str) and bool(_HEX.match(h.strip()))


def hex_rgb(h):
    """'#abc' / '#abcd' / '#aabbcc' / '#aabbccdd' -> [r, g, b] in 0..1 (alpha dropped). ValueError otherwise."""
    m = _HEX.match(str(h).strip())
    if not m:
        raise ValueError("not a hex color: %r" % (h,))
    s = m.group(1)
    if len(s) in (3, 4):
        s = "".join(c * 2 for c in s[:3])
    return [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def norm_hex(h):
    """Any hex form -> '#rrggbb' lower case."""
    return "#" + "".join("%02x" % round(c * 255) for c in hex_rgb(h))


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    r, g, b = [lin(x) for x in hex_rgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def best_ink(bg, candidates=("#ffffff", "#111111")):
    """The candidate with the highest contrast on bg (ties keep the first)."""
    return max(candidates, key=lambda c: ratio(c, bg))

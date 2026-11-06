"""Shared sRGB colour maths for the skill's scripts (export_tokens, design_md, design_md_check, code_extract,
icons, tweaks_panel, contrast, direction_recipe). One place for luminance, contrast and OKLCH; standard library only.

Stable API (other scripts import these names; keep them, add aliases when renaming):
  is_hex(h)            True for #rgb, #rgba, #rrggbb, #rrggbbaa (the # is optional)
  hex_rgb(h)           [r, g, b] in 0..1, alpha dropped; ValueError when not a hex colour
  hex_rgba(h)          [r, g, b, a] in 0..1 (a = 1 when the hex has no alpha)
  has_alpha(h)         True when a 4/8-digit hex carries alpha below 1
  norm_hex(h)          '#rrggbb' lower case
  lin(c)               sRGB channel -> linear light
  lum(h)               WCAG 2.x relative luminance (alias: luminance)
  ratio(a, b)          WCAG 2.x contrast ratio, 1..21 (alias: contrast)
  best_ink(bg, cands)  the candidate with the highest contrast on bg
  to_oklch / from_oklch / mix / reach   OKLCH helpers used to derive passing colours
"""
import math
import re

_HEX = re.compile(r"^#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def is_hex(h):
    """True when h is a 3/4/6/8-digit hex colour, with or without '#'."""
    return isinstance(h, str) and bool(_HEX.match(h.strip()))


def hex_rgba(h):
    """'#abc' / '#abcd' / '#aabbcc' / '#aabbccdd' (with or without #) -> [r, g, b, a] in 0..1. ValueError otherwise."""
    m = _HEX.match(str(h).strip())
    if not m:
        raise ValueError("not a hex color: %r" % (h,))
    s = m.group(1)
    if len(s) in (3, 4):
        s = "".join(c * 2 for c in s)
    a = int(s[6:8], 16) / 255 if len(s) == 8 else 1.0
    return [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [a]


def hex_rgb(h):
    """'#abc' / '#abcd' / '#aabbcc' / '#aabbccdd' -> [r, g, b] in 0..1 (alpha dropped). ValueError otherwise."""
    return hex_rgba(h)[:3]


def has_alpha(h):
    """True when the hex carries an alpha channel below 1 (#rgba / #rrggbbaa); False for opaque or invalid input."""
    try:
        return hex_rgba(h)[3] < 1
    except ValueError:
        return False


def norm_hex(h):
    """Any hex form -> '#rrggbb' lower case (alpha dropped)."""
    return "#" + "".join("%02x" % round(c * 255) for c in hex_rgb(h))


def lin(c):
    """sRGB channel (0..1) -> linear light."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delin(c):
    """Linear light -> sRGB channel (0..1), clamped."""
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lum(h):
    """WCAG 2.x relative luminance of a hex colour (0 black .. 1 white); alpha ignored."""
    r, g, b = [lin(x) for x in hex_rgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    """WCAG 2.x contrast ratio between two hex colours (order does not matter), 1..21."""
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


luminance = lum
contrast = ratio


def best_ink(bg, candidates=("#ffffff", "#111111")):
    """The candidate with the highest contrast on bg (ties keep the first)."""
    return max(candidates, key=lambda c: ratio(c, bg))


# ---------- OKLCH ----------
def to_oklch(h):
    """hex -> (L 0..1, C, H degrees)."""
    r, g, b = [lin(x) for x in hex_rgb(h)]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def from_oklch(L, C, H):
    """(L 0..1, C, H degrees) -> '#rrggbb' (clipped to sRGB)."""
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return "#" + "".join("%02x" % round(delin(x) * 255) for x in (r, g, bl))


def mix(a, b, t):
    """t of b over a, in linear light -> '#rrggbb'."""
    ra, rb = [lin(x) for x in hex_rgb(a)], [lin(x) for x in hex_rgb(b)]
    return "#" + "".join("%02x" % round(delin(x * (1 - t) + y * t) * 255) for x, y in zip(ra, rb))


def reach(color, bg, need, direction):
    """Move the OKLCH lightness of color (+1 lighter, -1 darker) until it has `need` contrast on bg
    (one hex or a list of hexes). Returns the first passing colour, or the end of the walk."""
    bgs = [bg] if isinstance(bg, str) else list(bg)
    L, C, H = to_oklch(color)
    for _ in range(60):
        c = from_oklch(L, C, H)
        if all(ratio(c, b) >= need for b in bgs):
            return c
        L = max(0.0, min(1.0, L + 0.01 * direction))
    return from_oklch(L, C, H)


def readable(color, bg, need=4.5):
    """color itself when it reaches `need` on bg (one hex or a list), else the lightness step toward the
    side with more room (darker on a light ground, lighter on a dark one)."""
    bgs = [bg] if isinstance(bg, str) else list(bg)
    if all(ratio(color, b) >= need for b in bgs):
        return norm_hex(color)
    return reach(color, bgs, need, -1 if sum(lum(b) for b in bgs) / len(bgs) > 0.18 else +1)

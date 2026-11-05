#!/usr/bin/env python3
"""Real one-ink halftone (AM dot screen) from a photograph, for print-led directions
(Halftone, Riso, Paste-up, Newsprint). Dot size follows the picture's darkness, so the
image reads as printed; a CSS dot pattern laid over a photo does not.

  python3 scripts/halftone.py in.jpg out.jpg --size 900 --ink "#2a1410" --paper "#f8f1d9"
  python3 scripts/halftone.py in.jpg out.jpg --size 1200x800 --cell 8 --angle 15 --bright 2.2 --crop-x 0.6 --eq

--size     output WxH or one number for a square (cover crop)
--cell     screen pitch in px (7-10 reads as print at 1x; smaller looks like noise)
--angle    screen angle; 45 for black, 15 or 75 for a colour ink
--bright   gamma lift (>1 opens the midtones; most photos need 1.5-2.2)
--crop-x   horizontal crop centre 0-1, to keep the subject in a square crop
--eq       equalize the histogram first (rescues flat or dark photos)

Pick photos with clear shapes on a light-to-mid ground (beans in a scoop, a cup, hands).
A dark, busy photo turns to mud in one ink: use it as a one-colour duotone band instead.
Standard library + Pillow.
"""
import argparse, math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--size', default='900'); ap.add_argument('--cell', type=float, default=8)
    ap.add_argument('--ink', default='#2a1410'); ap.add_argument('--paper', default='#f8f1d9')
    ap.add_argument('--angle', type=float, default=45); ap.add_argument('--bright', type=float, default=1.6)
    ap.add_argument('--crop-x', type=float, default=0.5); ap.add_argument('--eq', action='store_true')
    ap.add_argument('--quality', type=int, default=80)
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.split('x')) if 'x' in a.size else (int(a.size),) * 2
    im = ImageOps.fit(Image.open(a.src).convert('L'), (w, h), centering=(a.crop_x, 0.5))
    if a.eq:
        im = ImageOps.equalize(im)
    im = im.point(lambda v: int(255 * ((v / 255) ** (1 / a.bright))))
    im = ImageEnhance.Contrast(im).enhance(1.35).filter(ImageFilter.GaussianBlur(a.cell / 4))
    S = 3  # supersample, then downscale for clean dot edges
    W, H = w * S, h * S
    canvas = Image.new('RGB', (W, H), hex_rgb(a.paper))
    d = ImageDraw.Draw(canvas)
    ink = hex_rgb(a.ink)
    t = math.radians(a.angle); ct, st = math.cos(t), math.sin(t)
    c = a.cell * S; n = int(max(W, H) * 1.5 / c) + 2
    px = im.tobytes()  # one byte per pixel (mode L)
    for i in range(-n, n):
        for j in range(-n, n):
            x = i * c * ct - j * c * st + W / 2
            y = i * c * st + j * c * ct + H / 2
            if not (-c < x < W + c and -c < y < H + c):
                continue
            dark = 1 - px[min(h - 1, max(0, int(y / S))) * w + min(w - 1, max(0, int(x / S)))] / 255
            r = c * 0.72 * math.sqrt(dark)
            if r > 0.4:
                d.ellipse((x - r, y - r, x + r, y + r), fill=ink)
    canvas.resize((w, h), Image.Resampling.LANCZOS).save(a.out, quality=a.quality, optimize=True, progressive=True)
    print('wrote %s (%dx%d, cell %g, ink %s on %s)' % (a.out, w, h, a.cell, a.ink, a.paper))


if __name__ == '__main__':
    main()

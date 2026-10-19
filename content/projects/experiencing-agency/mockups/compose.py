"""Step 2 of 2: places each screen from ./screens into the iPhone frame exported from the Figma
mockup kit (phone-frame.png, Space Black with Dynamic Island) and writes the site images:
../images/mockup-<screen>.png (single phones) and ../images/mockup-cover.png (three phones).
Run from this folder: python3 compose.py
"""
from PIL import Image, ImageDraw
import numpy as np

SCREENS = ['welcome', 'meetings', 'discussion', 'new-comment', 'topic-thanks']
COVER = ['welcome', 'meetings', 'discussion']

frame = Image.open('phone-frame.png').convert('RGBA')
W, H = frame.size

# Screen opening of the frame (measured from the Figma export), with the Dynamic Island cut out.
k = 4
m = Image.new('L', (W * k, H * k), 0)
d = ImageDraw.Draw(m)
d.rounded_rectangle([43.5 * k, 36.5 * k, 790.5 * k, 1659.5 * k], radius=105 * k, fill=255)
d.rounded_rectangle([299 * k, 59 * k, 536 * k, 128 * k], radius=34.5 * k, fill=0)
mask = np.array(m.resize((W, H), Image.LANCZOS))


def phone(name):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.paste(Image.open(f'screens/{name}.png').convert('RGBA'), (41, 34))
    a = np.array(layer)
    a[..., 3] = np.minimum(a[..., 3], mask)
    return Image.alpha_composite(Image.fromarray(a), frame)


def save(im, path, width):
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    im.save(path, optimize=True)


phones = {n: phone(n) for n in SCREENS}
for n, im in phones.items():
    save(im, f'../images/mockup-{n}.png', 600)

# Cover: three phones side by side, the middle one raised (after the kit's three-phone layout).
gap, lift = 88, 140
cover = Image.new('RGBA', (W * 3 + gap * 2, H + lift), (0, 0, 0, 0))
for i, n in enumerate(COVER):
    cover.alpha_composite(phones[n], (i * (W + gap), 0 if i == 1 else lift))
save(cover, '../images/mockup-cover.png', 1400)
print('done')

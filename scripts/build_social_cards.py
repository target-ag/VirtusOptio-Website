"""Generate committed social cards. Run with Pillow after a MkDocs build.

Development-only: these JPEGs are committed; production needs no image library.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = '/System/Library/Fonts/Helvetica.ttc'

def make_card(title, filename, lang="en"):
    canvas = Image.new('RGB', (1200, 627), '#f9f9f9')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 20, 627), fill='#2D57C7')
    draw.text((72, 54), 'VIRTUS OPTIO', font=ImageFont.truetype(FONT, 28), fill='#2D57C7')
    draw.line((72, 113, 1128, 113), fill='#e1e5ec', width=2)
    label = title.removesuffix(' — Virtus Optio').removesuffix(' | Virtus Optio')
    if label.startswith('Virtus Optio — '):
        label = 'Ethisch verkopen.\nPraktische verkoopsystemen.' if lang == 'nl' else 'Ethical selling.\nPractical sales systems.'
    for size in range(66, 33, -2):
        font = ImageFont.truetype(FONT, size)
        lines = []
        for paragraph in label.split('\n'):
            line = ''
            for word in paragraph.split():
                candidate = (line + ' ' + word).strip()
                if draw.textlength(candidate, font=font) > 1030 and line:
                    lines.append(line); line = word
                else:
                    line = candidate
            lines.append(line)
        if len(lines) * (size + 14) <= 285:
            break
    y = 164
    for line in lines:
        draw.text((72, y), line, font=font, fill='#171b24')
        y += size + 14
    draw.text((72, 518), ('Betere gesprekken. Sterkere relaties.' if lang == 'nl' else 'Better conversations. Stronger relationships.'), font=ImageFont.truetype(FONT, 26), fill='#606773')
    draw.text((72, 563), 'virtusoptio.com', font=ImageFont.truetype(FONT, 23), fill='#2D57C7')
    canvas.save(filename, 'JPEG', quality=90, optimize=True)

if __name__ == '__main__':
    output = ROOT / 'docs/assets/social'
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / '.cache/social-cards.json').read_text())
    for item in manifest:
        make_card(item['title'], output / (item['key'] + '.jpg'), item.get('lang', 'en'))
    make_card('Virtus Optio — Ethical Selling & Sales Systems', output / 'default.jpg')
    make_card('Virtus Optio — Ethisch verkopen & verkoopsystemen', output / 'nl-default.jpg', 'nl')
    print(f'Generated {len(manifest) + 2} social cards.')

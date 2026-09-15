"""Rebuild the two CSC prop AO pages from registered, non-overlapping source cells.

Run with Python + Pillow, passing the CSC_Props/Current directory. This operates on
an explicitly selected working snapshot; it does not promote or rewrite UVs.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image


def pack(root):
    root = Path(root)
    path = root / 'atlas/quarter-ao-manifest.json'
    manifest = json.loads(path.read_text())
    prepared = []
    for page in manifest['pages']:
        size = page['size']
        image = Image.new('RGB', (size, size), 'white')
        used = []
        for quarter in page['quarters']:
            for family in quarter['families']:
                if family.get('states'):
                    raise ValueError('Migrate legacy state bakes explicitly before using this cell packer')
                fx, fy, fx1, fy1 = family['bounds']
                qx, qy, qx1, qy1 = quarter['bounds']
                if not 0 <= qx <= fx < fx1 <= qx1 <= size or not 0 <= qy <= fy < fy1 <= qy1 <= size:
                    raise ValueError('Family lies outside its Quarter or page')
                for cell in family.get('allocations', []):
                    x, y, x1, y1 = cell['cell']
                    if not fx <= x < x1 <= fx1 or not fy <= y < y1 <= fy1:
                        raise ValueError(f'{cell["id"]}: outside family budget')
                    if any(x < r[2] and x1 > r[0] and y < r[3] and y1 > r[1] for r in used):
                        raise ValueError(f'{cell["id"]}: overlapping AO allocation')
                    used.append((x,y,x1,y1))
                    src = root / cell['source']
                    patch = Image.open(src).convert('RGB')
                    if patch.size != (x1-x, y1-y):
                        raise ValueError(f'{cell["id"]}: source size differs from registered cell')
                    image.paste(patch, (x,y))
                    cell['source_sha256'] = hashlib.sha256(src.read_bytes()).hexdigest()
        prepared.append((page,image))
    # Validate all sources/pages before replacing anything.
    for page,image in prepared:
        dest = root / 'textures' / (page['id'] + '.png')
        # Preserve identical files byte for byte (including untouched Sheet 02).
        if not dest.exists() or Image.open(dest).convert('RGB').tobytes() != image.tobytes():
            image.save(dest)
        page['sha256'] = hashlib.sha256(dest.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    pack(parser.parse_args().library)

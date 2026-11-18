"""Convert an explicit native UI.Screenshot TGA; no desktop capture or retouching."""
import argparse
from pathlib import Path
from PIL import Image

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('number',type=int)
    parser.add_argument('name')
    args=parser.parse_args()
    source=next((Path.home()/'Documents/My Games').glob(
        f'Sid Meier*/Screenshots/Civ6Screen{args.number:04d}.tga'))
    output=Path.home()/'Desktop/Codex/discworld-prototype-20261110/screenshots'
    output.mkdir(parents=True,exist_ok=True)
    im=Image.open(source)
    im.save(output/(args.name+'-full.png'))
    im.thumbnail((1600,900))
    im.save(output/(args.name+'.png'))
    print(source, '->', output/(args.name+'.png'))

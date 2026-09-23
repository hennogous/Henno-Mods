"""Trial SAM 2.1 prompted masks for selected building-icon masses.

Loads the image once, prompts each selected object with a box and positive /
negative points, and saves every candidate mask for review. Does not paint
outlines, alter the tuned img2img pipeline, or update any atlas.
"""
import argparse
import json
import re
import warnings
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


def slug(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('prompts', type=Path)
    ap.add_argument('--checkpoint', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--model-config', default='configs/sam2.1/sam2.1_hiera_b+.yaml')
    args = ap.parse_args()
    config = json.loads(args.prompts.read_text(encoding='utf-8-sig'))
    source = Image.open(args.source).convert('RGBA')
    if list(source.size) != config['canvas']:
        raise ValueError('Prompt canvas does not match source render')
    rgba = np.asarray(source)
    rgb = rgba[:, :, :3].copy()
    rgb[rgba[:, :, 3] < 128] = 255
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    if not torch.cuda.is_available():
        raise RuntimeError('This prototype expects the local CUDA GPU')
    model = build_sam2(args.model_config, str(args.checkpoint), device='cuda',
                       apply_postprocessing=False)
    predictor = SAM2ImagePredictor(model)
    candidates = {}
    meta = {'source': str(args.source), 'checkpoint': str(args.checkpoint),
            'model_config': args.model_config, 'objects': []}
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
    with torch.inference_mode(), torch.autocast('cuda', dtype=torch.bfloat16):
        predictor.set_image(rgb)
        for spec in config['objects']:
            name = spec['name']
            key = slug(name)
            positive = np.asarray(spec.get('positive', []), dtype=np.float32).reshape(-1, 2)
            negative = np.asarray(spec.get('negative', []), dtype=np.float32).reshape(-1, 2)
            coords = np.concatenate([positive, negative], axis=0)
            labels = np.asarray([1]*len(positive) + [0]*len(negative), np.int32)
            box = np.asarray(spec['box'], dtype=np.float32)
            masks, scores, _ = predictor.predict(
                point_coords=coords if len(coords) else None,
                point_labels=labels if len(labels) else None,
                box=box, multimask_output=True)
            masks = np.asarray(masks, dtype=bool)
            scores = np.asarray(scores, dtype=float)
            ranked = []
            for idx, mask in enumerate(masks):
                clipped = mask & (rgba[:, :, 3] >= 128)
                candidates[f'{key}_{idx}'] = clipped.astype(np.uint8)
                pos_hit = float(clipped[positive[:, 1].astype(int), positive[:, 0].astype(int)].mean()) if len(positive) else 1.0
                neg_hit = float(clipped[negative[:, 1].astype(int), negative[:, 0].astype(int)].mean()) if len(negative) else 0.0
                ranked.append({'index': idx, 'score': round(float(scores[idx]), 4),
                               'area': int(clipped.sum()), 'positive_hit': round(pos_hit, 3),
                               'negative_hit': round(neg_hit, 3),
                               'review_score': round(float(scores[idx]) + .10*pos_hit - .10*neg_hit, 4)})
            chosen = max(ranked, key=lambda item: item['review_score'])['index']
            x1, y1, x2, y2 = [int(v) for v in box]
            margin = 18
            crop = (max(0, x1-margin), max(0, y1-margin),
                    min(source.width, x2+margin), min(source.height, y2+margin))
            panels = []
            for idx in range(len(masks)):
                m = candidates[f'{key}_{idx}'][crop[1]:crop[3], crop[0]:crop[2]].astype(bool)
                panel = Image.fromarray(rgb[crop[1]:crop[3], crop[0]:crop[2]]).convert('RGBA')
                tint = Image.new('RGBA', panel.size, (0, 190, 230, 0))
                tint.putalpha(Image.fromarray((m.astype(np.uint8)*105), 'L'))
                panel.alpha_composite(tint)
                panel.thumbnail((470, 430), Image.Resampling.LANCZOS)
                card = Image.new('RGBA', (490, 490), (55, 58, 61, 255))
                card.alpha_composite(panel, ((490-panel.width)//2, 35+(430-panel.height)//2))
                draw = ImageDraw.Draw(card)
                info = ranked[idx]
                label = f'{name}  #{idx}  score {info["score"]:.2f}  area {info["area"]}'
                if idx == chosen:
                    label += '  *'
                draw.text((10, 8), label, font=font, fill='white')
                panels.append(card)
            sheet = Image.new('RGBA', (490*len(panels), 490), (55, 58, 61, 255))
            for idx, panel in enumerate(panels):
                sheet.alpha_composite(panel, (490*idx, 0))
            sheet.save(out / f'{key}_candidates.png')
            meta['objects'].append({'name': name, 'key': key, 'box': spec['box'],
                                    'positive': spec.get('positive', []),
                                    'negative': spec.get('negative', []),
                                    'chosen_index': int(chosen), 'candidates': ranked})
            print(json.dumps({'object': name, 'chosen': int(chosen), 'candidates': ranked}))
    np.savez_compressed(out / 'candidate_masks.npz', **candidates)
    (out / 'sam2_prediction_report.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print(json.dumps({'saved_masks': len(candidates), 'report': str(out / 'sam2_prediction_report.json')}))


if __name__ == '__main__':
    main()

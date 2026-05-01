"""
Post-process pipeline for Civ 6 SV sprites.
Tuned 2026-03-27 by Henno + Bill.

Steps:
  1. Remove black background (threshold=15)
  2. Brighten image 35%
  3. Add outlines: 10px outer silhouette + 4px inner edge, charcoal #3A3A3A
  4. Resize to 110px and composite onto 256x256 transparent canvas
  5. Add shadow: rotated ellipse, long axis UL->LR at 32°, clipped to lower-right half
     - Size: 110% x 45% of building size
     - Offset: +18px right, +22px down from building center
     - Opacity: 35% (alpha 89)
     - No feathering (hard edge)

ComfyUI generation settings (tuned):
  - Model: sd_xl_base_1.0.safetensors
  - LoRA: civ6_strategic_view.safetensors, strength 0.6
  - Prompt: "classical period industrial utility building, civ 6 strategic view sprite,
             simplified illustration, muted earth tones, hand-painted style"
  - Negative: "realistic, photo, blurry, text, watermark, ugly, deformed,
               photorealistic, oversaturated, added details, invented features"
  - Denoise: 0.55 (img2img from Blender render)
  - CFG: 8.0
  - Steps: 25, sampler: dpmpp_2m karras
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# --- Background removal ---
def remove_black_background(img: Image.Image, threshold: int = 15) -> Image.Image:
    img = img.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = (r < threshold) & (g < threshold) & (b < threshold)
    data[mask, 3] = 0
    return Image.fromarray(data, "RGBA")


# --- Outline: outer silhouette only ---
def add_outlines(img: Image.Image) -> Image.Image:
    from scipy.ndimage import binary_dilation
    rgba = np.array(img.convert("RGBA"))
    alpha = rgba[:,:,3]

    # Boolean mask of building pixels
    building = alpha > 10

    # Outer silhouette: 10px thick ring outside building
    dilated_outer = binary_dilation(building, iterations=10)
    outline_outer = dilated_outer & ~building

    # Inner detail lines: 4px ring inside silhouette
    from scipy.ndimage import binary_erosion
    eroded = binary_erosion(building, iterations=4)
    inner_edge = building & ~eroded

    # Charcoal: #3A3A3A
    result = rgba.copy()
    result[outline_outer] = [58, 58, 58, 255]   # outer silhouette
    result[inner_edge]    = [58, 58, 58, 200]   # inner edge, slightly softer

    return Image.fromarray(result, "RGBA")





def brighten(img: Image.Image, factor: float = 1.35) -> Image.Image:
    """Boost brightness of non-transparent pixels."""
    from PIL import ImageEnhance
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance(factor)
    rgba = img.convert("RGBA")
    r, g, b = rgb.split()
    rgba.paste(Image.merge("RGB", (r, g, b)), mask=None)
    # Re-apply original alpha
    alpha = img.split()[3]
    rgba.putalpha(alpha)
    return rgba


def process(input_path: str, output_path: str = None, threshold: int = 15):
    if output_path is None:
        output_path = input_path.replace(".png", "_sv.png")
    img = Image.open(input_path).convert("RGBA")
    img = remove_black_background(img, threshold)
    img = brighten(img)
    img = add_outlines(img)
    # Compose onto 256x256 canvas
    canvas_size = 256
    building_size = 110
    img = img.resize((building_size, building_size), Image.LANCZOS)

    # Build canvas with shadow then building on top
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = (canvas_size - building_size) // 2

    # Draw shadow on canvas — positioned relative to where building will sit
    shadow_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow_layer)
    # Shadow center: building center + offset to bottom-right
    bx = offset + building_size // 2
    by = offset + building_size // 2
    # Shadow: long axis upper-left to lower-right, ~32deg from horizontal
    # Draw a wide flat ellipse then rotate it
    sw = int(building_size * 1.1)   # long axis
    sh = int(building_size * 0.45)  # short axis — wider
    # Center shadow just to the lower-right of building center
    sx = bx + 18
    sy = by + 22
    temp = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(temp)
    tdraw.ellipse([sx - sw//2, sy - sh//2, sx + sw//2, sy + sh//2],
                  fill=(0, 0, 0, 89))
    # Rotate so long axis goes from upper-left to lower-right (+32 degrees)
    temp = temp.rotate(32, resample=Image.BICUBIC, center=(sx, sy))
    # Clip: hide the upper-left half of the ellipse
    # Clip line runs top-left to bottom-right through the shadow center, at 32°
    import math
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    # The clip line passes through (sx, sy) at angle 32° from horizontal
    # Normal to this line points upper-left (hide that side)
    # Draw a filled polygon covering the lower-right half
    angle_rad = math.radians(32)
    nx = -math.sin(angle_rad)  # normal pointing upper-left
    ny =  math.cos(angle_rad)
    # Build a large polygon on the lower-right side of the line
    far = canvas_size * 3
    p1 = (sx + far * math.cos(angle_rad), sy + far * math.sin(angle_rad))
    p2 = (sx - far * math.cos(angle_rad), sy - far * math.sin(angle_rad))
    # Offset both points in the lower-right normal direction
    p3 = (p2[0] - far * nx, p2[1] - far * ny)
    p4 = (p1[0] - far * nx, p1[1] - far * ny)
    mask_draw.polygon([p1, p2, p3, p4], fill=255)
    temp_arr = __import__('numpy').array(temp)
    mask_arr = __import__('numpy').array(mask)
    temp_arr[:,:,3] = (temp_arr[:,:,3].astype('float') * mask_arr / 255).astype('uint8')
    temp = Image.fromarray(temp_arr, "RGBA")
    shadow_layer = Image.alpha_composite(shadow_layer, temp)

    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.paste(img, (offset, offset), img)

    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/Shadow/ComfyUI/output/sv_img2img_classical_cfg6_00004_.png"
    out = process(inp)
    print(f"Saved: {out}")

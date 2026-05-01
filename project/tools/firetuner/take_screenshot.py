"""Take a compressed screenshot using Python PIL"""
import sys
try:
    from PIL import ImageGrab
    img = ImageGrab.grab()
    img = img.resize((1280, 720))
    name = sys.argv[1] if len(sys.argv) > 1 else "civ_screen"
    path = f"C:\\Users\\Shadow\\Desktop\\Working Files\\Dropzone\\{name}.jpg"
    img.save(path, "JPEG", quality=60)
    print(f"Saved: {path}")
except ImportError:
    print("PIL not available, trying mss...")
    import mss
    with mss.mss() as sct:
        sct.shot(output=f"C:\\Users\\Shadow\\Desktop\\Working Files\\Dropzone\\{name}.png")
        print("Saved with mss")

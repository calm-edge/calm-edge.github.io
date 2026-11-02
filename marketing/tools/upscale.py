"""AI upscaling (Real-ESRGAN, anime/illustration model) for artwork such as the presenter character.
Runs on GitHub Actions (CPU): python marketing/tools/upscale.py <model.pth> <in.png> <out.png>"""
import sys
import numpy as np, torch
from PIL import Image
import spandrel

model = spandrel.ModelLoader().load_from_file(sys.argv[1]).eval()
img = Image.open(sys.argv[2]).convert("RGB")
x = torch.from_numpy(np.asarray(img).astype(np.float32) / 255).permute(2, 0, 1)[None]
with torch.no_grad():
    y = model(x).clamp(0, 1)[0].permute(1, 2, 0).numpy()
Image.fromarray((y * 255 + 0.5).astype(np.uint8)).save(sys.argv[3])
print(img.size, "->", Image.open(sys.argv[3]).size)

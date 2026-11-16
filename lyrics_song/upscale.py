"""AI-upscale (Real-ESRGAN x4plus) the small screenshot photos after cropping off their burned-in text."""
import subprocess, numpy as np, torch
from PIL import Image
from spandrel import ModelLoader
U = "/root/.claude/uploads/31472ba1-8ea5-51fc-a7e6-64ea60291e16/"
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/song/"
CROP = {"f_lachimi": ("934550dc-image.jpg", 486), "f_yellow": ("9bea7c04-image.jpg", 470),
        "f_white": ("2da72a6f-image.jpg", 500), "tamarind": ("45d3fdf4-image.jpg", 452)}   # keep rows above the burned-in text
m = ModelLoader().load_from_file(S + "model/x4plus.pth").eval(); torch.set_num_threads(4)
for name, (f, h) in CROP.items():
    im = Image.open(U + f).convert("RGB"); im = im.crop((0, 0, im.width, h))
    x = torch.from_numpy(np.asarray(im)).permute(2, 0, 1).float().unsqueeze(0) / 255
    with torch.no_grad(): y = m(x).clamp(0, 1)[0].permute(1, 2, 0).numpy()
    Image.fromarray((y * 255).round().astype(np.uint8)).save(S + f"hq/{name}.png")
    print(name, im.size, "->", (im.width * 4, h * 4), flush=True)

from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import requests
import torch
import numpy as np
import matplotlib.pyplot as plt
import time

processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined").cpu()

prompt = "human"
image = "https://videogamebunny.github.io/static/images/sample-A.jpeg"
threshold = 0.9
alpha_value = 0.5

image = Image.open(requests.get(image, stream=True).raw)
image.thumbnail((128, 128))
time0 = time.time()
inputs = processor(text=prompt, images=image, return_tensors="pt")
inputs = {k: v.cpu() for k, v in inputs.items()}

with torch.no_grad():
    outputs = model(**inputs)
    preds = outputs.logits
pred = torch.sigmoid(preds)
mat = pred.squeeze().cpu().numpy()
mask = Image.fromarray(np.uint8(mat * 255), "L")
mask = mask.convert("RGB")
mask = mask.resize(image.size)
mask = np.array(mask)[:, :, 0]

# normalize the mask
mask_min = mask.min()
mask_max = mask.max()
mask = (mask - mask_min) / (mask_max - mask_min)

# threshold the mask
bmask = mask > threshold
# zero out values below the threshold
mask[mask < threshold] = 0
print("time_taken", time.time() - time0)

fig, ax = plt.subplots()
ax.imshow(image)
ax.imshow(mask, alpha=alpha_value, cmap="jet")

plt.savefig("test.png")

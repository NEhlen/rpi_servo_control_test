import cv2
from PIL import Image
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import torch
import numpy as np
import matplotlib.pyplot as plt
import time


def get_image_from_webcam():
    cap = cv2.VideoCapture(0)

    # ret, frame = cap.read()
    # time.sleep(0.5)
    ret, frame = cap.read()
    cap.release()

    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        return image
    else:
        print("Error: Could not capture image from webcam.")
        return None


def get_look_direction(obect_to_look_at: str):
    image = get_image_from_webcam()
    if image is None:
        return None

    # Use the image to determine the look direction
    processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
    model = CLIPSegForImageSegmentation.from_pretrained(
        "CIDAS/clipseg-rd64-refined"
    ).cpu()

    prompt = obect_to_look_at
    threshold = 0.9

    image.thumbnail((128, 128))
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
    mask[~bmask] = 0

    # determine from which function to choose in order to look at the object:
    # look right, look left, look up, look down, look center
    # look right and up, look right and down
    # look left and up, look left and down
    py, px = np.where(bmask)

    fig, ax = plt.subplots()
    ax.imshow(image)
    mask[~bmask] = np.nan
    ax.imshow(mask, alpha=0.5, cmap="jet")

    ax.scatter(np.mean(px), np.mean(py), c="r", s=100)

    fig.savefig("test.png")
    plt.close()
    hor = ""
    ver = ""
    if len(px) == 0:
        hor = "center"
        ver = "center"
    elif np.mean(px) < image.size[0] / 3:
        hor = "left"
    elif np.mean(px) > 2 * image.size[0] / 3:
        hor = "right"
    else:
        hor = "center"

    if np.mean(py) < image.size[1] / 3:
        ver = "up"
    elif np.mean(py) > 2 * image.size[1] / 3:
        ver = "down"
    else:
        ver = "center"

    return hor, ver


if __name__ == "__main__":
    get_look_direction("human")

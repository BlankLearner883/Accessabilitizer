from transformers import BlipProcessor, BlipForConditionalGeneration
from bs4 import BeautifulSoup
from PIL import Image
import torch
import sys
import os

# ---- argument check ----
if len(sys.argv) < 2:
    print("Usage: python script.py input.html")
    sys.exit(1)

input_path = sys.argv[1]

# ---- read HTML ----
with open(input_path, "r", encoding="utf-8") as f:
    text = f.read()

soup = BeautifulSoup(text, "html.parser")

# ---- load BLIP ----
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
print("Model loaded")

# ---- caption each image ----
html_dir = os.path.dirname(input_path)

for img in soup.find_all("img", src=True):
    img_src = img["src"]
    image_path = os.path.join(html_dir, img_src)

    try:
        image = Image.open(image_path).convert("RGB")

        inputs = processor(image, return_tensors="pt")
        with torch.no_grad():
            ids = model.generate(**inputs)
        caption = processor.decode(ids[0], skip_special_tokens=True)
    except Exception as e:
        caption = "[ERROR: {e}]"

    print("{img_src} → {caption}")

    # ---- add caption under the image ----
    caption_tag = soup.new_tag("p", attrs={"class": "caption"})
    caption_tag.string = caption

    img.insert_after(caption_tag)

# ---- save updated HTML ----
output_path = input_path.replace(".html", "_captioned.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("\n✔ Done! Updated HTML saved as:\n{output_path}")

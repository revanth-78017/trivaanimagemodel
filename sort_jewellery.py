import os
import shutil
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm
import uuid

# Paths
input_folder = "dataset_raw"
output_folder = "dataset_sorted"

categories = ["ring", "necklace", "bracelet", "earring"]

# Prompts designed to minimize confusion and improve semantic separation
prompts = [
    "a close up photo of a ring, finger jewellery",
    "a photo of a necklace, chain or neck jewellery",
    "a photo of a bracelet, wrist jewellery",
    "a close up photo of an earring, ear jewellery"
]

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available(): # Optimized for Apple Silicon Macs
        return "mps"
    return "cpu"

def main():
    # Create output folders
    for cat in categories:
        os.makedirs(os.path.join(output_folder, cat), exist_ok=True)

    print("Loading CLIP model...")
    device = get_device()
    
    try:
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    except Exception as e:
        print(f"Failed to load CLIP model: {e}")
        return
    
    # Pre-compute text features for the prompts
    text_inputs = processor(text=prompts, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        text_features = model.get_text_features(**text_inputs)
        if not isinstance(text_features, torch.Tensor):
            text_features = model.text_projection(text_features.pooler_output)
        # Normalize features
        text_features /= text_features.norm(dim=-1, keepdim=True)

    if not os.path.exists(input_folder):
        print(f"Error: '{input_folder}' directory not found in the current path.")
        return

    images = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    print(f"Found {len(images)} files. Starting sorting on device: {device}...")

    # Process images with a progress bar
    for img_name in tqdm(images, desc="Sorting Jewellery"):
        img_path = os.path.join(input_folder, img_name)

        try:
            # Load and process image
            image = Image.open(img_path).convert("RGB")
            image_inputs = processor(images=image, return_tensors="pt").to(device)

            with torch.no_grad():
                image_features = model.get_image_features(**image_inputs)
                if not isinstance(image_features, torch.Tensor):
                    image_features = model.visual_projection(image_features.pooler_output)
                image_features /= image_features.norm(dim=-1, keepdim=True)

            # Calculate cosine similarity and find best match
            similarity = (image_features @ text_features.T).squeeze(0)
            best_match_idx = similarity.argmax().item()
            best_category = categories[best_match_idx]

        except Exception as e:
            # Skip corrupted or unreadable images completely
            continue

        # Copy image out
        dest_folder = os.path.join(output_folder, best_category)
        dest_path = os.path.join(dest_folder, img_name)
        
        # UUID-based collision handling if duplicate names exist
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(img_name)
            unique_id = uuid.uuid4().hex
            dest_path = os.path.join(dest_folder, f"{base}_{unique_id}{ext}")

        try:
            shutil.copy2(img_path, dest_path)
        except:
            pass # In case copy fails

    print("\nSorting Done ✅")

if __name__ == "__main__":
    main()
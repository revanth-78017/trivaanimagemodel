import os
import json
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm

# Paths
input_folder = "dataset_sorted"
output_metadata_file = os.path.join(input_folder, "metadata.jsonl")

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def main():
    if not os.path.exists(input_folder):
        print(f"Error: '{input_folder}' directory not found.")
        return

    device = get_device()
    print(f"Loading BLIP captioning model on {device}...")
    
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    except Exception as e:
        print(f"Failed to load BLIP model: {e}")
        return
        
    categories = ["ring", "necklace", "bracelet", "earring"]
    
    # Collect all image paths
    image_paths = []
    for cat in categories:
        cat_dir = os.path.join(input_folder, cat)
        if os.path.isdir(cat_dir):
            for file in os.listdir(cat_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    rel_path = f"{cat}/{file}"
                    abs_path = os.path.join(cat_dir, file)
                    image_paths.append((abs_path, rel_path, cat))
                    
    print(f"Found {len(image_paths)} structured images to caption.")

    if not image_paths:
        print("No images found! Make sure 'sort_jewellery.py' has successfully completed first.")
        return

    # Open the JSONL file in write mode
    with open(output_metadata_file, "w", encoding="utf-8") as f:
        # Process images with progress bar
        for abs_path, rel_path, category in tqdm(image_paths, desc="Generating Captions"):
            try:
                raw_image = Image.open(abs_path).convert('RGB')
                
                inputs = processor(images=raw_image, return_tensors="pt").to(device)
                
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=50)
                
                caption = processor.decode(out[0], skip_special_tokens=True)
                
                # Inject the category explicitly to enforce the conditioning mapping
                final_caption = f"{caption}, indian god style jewellery, {category}"
                
                entry = {
                    "file_name": rel_path,
                    "text": final_caption
                }
                
                f.write(json.dumps(entry) + "\n")
                f.flush()
                
            except Exception as e:
                # Skip unreadable images
                continue
                
    print(f"\nCaptioning Done ✅. LoRA Metadata saved to {output_metadata_file}")

if __name__ == "__main__":
    main()

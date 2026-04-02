import os
import shutil
from PIL import Image
import imagehash
import csv

class ImageProcessor:
    def __init__(self, output_dir, metadata_file="metadata.csv"):
        self.output_dir = output_dir
        self.metadata_file = metadata_file
        self.seen_hashes = set()
        self.min_resolution = 512
        
        # Ensure output dir exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize metadata CSV
        self.metadata_path = os.path.join(self.output_dir, self.metadata_file)
        if not os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Filename", "Category", "Subcategory", "Tags", "Source"])

    def process_and_move_image(self, filepath, category, subcategory, tags, source):
        if not os.path.exists(filepath):
            return False

        try:
            with Image.open(filepath) as img:
                # Optional: convert to RGB to handle alpha channels and greyscale predictably
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Check resolution
                width, height = img.size
                if width < self.min_resolution or height < self.min_resolution:
                    os.remove(filepath)
                    return False
                
                # Check for duplicates using perceptual hash
                img_hash = imagehash.phash(img)
                if img_hash in self.seen_hashes:
                    os.remove(filepath)
                    return False
                
                self.seen_hashes.add(img_hash)
            
            # Subcategory folder inside Category folder
            cat_dir = os.path.join(self.output_dir, category)
            subcat_dir = os.path.join(cat_dir, subcategory)
            os.makedirs(subcat_dir, exist_ok=True)
            
            filename = os.path.basename(filepath)
            
            # Ensure safe extension mapping
            name, ext = os.path.splitext(filename)
            if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png']:
                ext = '.jpg'
                
            new_path = os.path.join(subcat_dir, f"{name}{ext}")
            
            # Handle filename collisions
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(subcat_dir, f"{name}_{counter}{ext}")
                counter += 1
                
            shutil.copy2(filepath, new_path)
            os.remove(filepath)
            
            # Save metadata
            # We save the relative path from output_dir to ensure the CSV points to the right file
            rel_path = os.path.join(category, subcategory, os.path.basename(new_path))
            with open(self.metadata_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([rel_path, category, subcategory, tags, source])
                
            return True
            
        except Exception as e:
            # If the image is corrupted or cannot be opened, remove it
            try:
                os.remove(filepath)
            except:
                pass
            return False

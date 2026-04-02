import os
import shutil
import zipfile
from icrawler.builtin import BingImageCrawler
from image_processor import ImageProcessor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOD_JEWELLERY_DIR = os.path.join(BASE_DIR, "god_jewellery_dataset")
MAX_IMAGES_PER_QUERY = 10 # Getting a sample dataset

DEITIES = {
    "Shiva": ["shiva"],
    "Vishnu": ["krishna", "venkateshwara"],
    "Goddesses": ["lakshmi", "durga"],
    "Ganesha": ["ganesha"]
}

JEWELLERY_TYPES = [
    "ring",
    "earrings",
    "jhumkas"
]

STYLES = [
    "temple jewellery",
    "antique gold design"
]

def generate_queries():
    queries = []
    for category, subcategories in DEITIES.items():
        for subcat in subcategories:
            for j_type in JEWELLERY_TYPES:
                for style in STYLES:
                    keyword = f"indian god {subcat} {j_type} {style} high quality"
                    tags = f"{category.lower()}, {subcat.lower()}, {j_type}, {style}"
                    queries.append({
                        "keyword": keyword,
                        "category": category, # e.g. Shiva
                        "subcategory": j_type, # e.g. rings
                        "tags": tags
                    })
    unique_queries = {q['keyword']: q for q in queries}.values()
    return list(unique_queries)

def zip_dataset(output_dir, zip_filename):
    print(f"Zipping dataset to {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, output_dir)
                zipf.write(filepath, arcname)
    print("Zipping complete.")

def main():
    queries = generate_queries()
    processor = ImageProcessor(output_dir=GOD_JEWELLERY_DIR, metadata_file="god_jewellery_metadata.csv")
    
    temp_dir = os.path.join(BASE_DIR, "gj_temp_downloads")
    os.makedirs(temp_dir, exist_ok=True)
    
    crawler = BingImageCrawler(storage={'root_dir': temp_dir})
    print(f"Total Keyword Combinations Generated: {len(queries)}")

    for i, q in enumerate(queries):
        keyword = q["keyword"]
        category = q["category"]
        subcategory = q["subcategory"]
        tags = q["tags"]
        
        print(f"[{i+1}/{len(queries)}] Scraping for: {keyword}...")
        try:
            crawler.crawl(keyword=keyword, max_num=MAX_IMAGES_PER_QUERY)
        except Exception as e:
            print(f"Error crawling {keyword}: {e}")
        
        saved_count = 0
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                success = processor.process_and_move_image(filepath, category, subcategory, tags, "Bing Images")
                if success:
                    saved_count += 1
                    
        for remaining in os.listdir(temp_dir):
            if os.path.isfile(os.path.join(temp_dir, remaining)):
                try:
                    os.remove(os.path.join(temp_dir, remaining))
                except:
                    pass
                    
        print(f"Saved {saved_count} valid images for {keyword}.")

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"God Jewellery Dataset compiled at {GOD_JEWELLERY_DIR}.")
    
    zip_path = os.path.join(BASE_DIR, "god_jewellery_sample.zip")
    zip_dataset(GOD_JEWELLERY_DIR, zip_path)

if __name__ == "__main__":
    main()

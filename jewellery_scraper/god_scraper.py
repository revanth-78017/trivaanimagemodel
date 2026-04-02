import os
import shutil
from icrawler.builtin import BingImageCrawler
from god_scraper_config import generate_god_queries, MAX_IMAGES_PER_QUERY, GODS_DATASET_DIR
from image_processor import ImageProcessor
import zipfile

def zip_dataset(output_dir, zip_filename="gods_dataset.zip"):
    print(f"Zipping dataset to {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, output_dir)
                zipf.write(filepath, arcname)
    print("Zipping complete.")

def main():
    queries = generate_god_queries()
    # We reuse the logic but point the processor to output into the new directory
    # Also write to gods_metadata.csv
    processor = ImageProcessor(output_dir=GODS_DATASET_DIR, metadata_file="gods_metadata.csv")
    
    # Temporary directory for raw downloads
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gods_temp_downloads")
    os.makedirs(temp_dir, exist_ok=True)
    
    crawler = BingImageCrawler(storage={'root_dir': temp_dir})

    print(f"Total Keyword Combinations Generated for Gods Dataset: {len(queries)}")

    for i, q in enumerate(queries):
        keyword = q["keyword"]
        category = q["category"]
        subcategory = q["subcategory"]
        tags = q["tags"]
        
        print(f"[{i+1}/{len(queries)}] Scraping for: {keyword}...")
        
        # Buffer for drops
        fetch_count = int(MAX_IMAGES_PER_QUERY * 1.5)
        crawler.crawl(keyword=keyword, max_num=fetch_count)
        
        saved_count = 0
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                success = processor.process_and_move_image(filepath, category, subcategory, tags, "Bing Images")
                if success:
                    saved_count += 1
                    
        # Clear out remaining invalid temp files
        for remaining in os.listdir(temp_dir):
            if os.path.isfile(os.path.join(temp_dir, remaining)):
                try:
                    os.remove(os.path.join(temp_dir, remaining))
                except:
                    pass
                    
        print(f"Saved {saved_count} valid images for {keyword}.")

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"Gods Dataset compiled at {GODS_DATASET_DIR}.")
    
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gods_dataset.zip")
    zip_dataset(GODS_DATASET_DIR, zip_path)

if __name__ == "__main__":
    main()

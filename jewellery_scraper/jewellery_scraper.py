import os
import shutil
from icrawler.builtin import BingImageCrawler
from scraper_config import generate_queries, MAX_IMAGES_PER_QUERY, DATASET_DIR
from image_processor import ImageProcessor
import zipfile

def zip_dataset(output_dir, zip_filename="dataset.zip"):
    print(f"Zipping dataset to {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # We might have over 150k items, Python's zipfile can handle it but it can be slow
        for root, _, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, output_dir)
                zipf.write(filepath, arcname)
    print("Zipping complete.")

def main():
    queries = generate_queries()
    processor = ImageProcessor(output_dir=DATASET_DIR)
    
    # Temporary directory for raw downloads
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_downloads")
    os.makedirs(temp_dir, exist_ok=True)
    
    # We use Bing as before, but since we are scraping a massive amount, 
    # the thread will sleep inherently during network calls.
    crawler = BingImageCrawler(storage={'root_dir': temp_dir})

    print(f"Total Keyword Combinations Generated: {len(queries)}")

    for i, q in enumerate(queries):
        keyword = q["keyword"]
        category = q["category"]
        subcategory = q["subcategory"]
        tags = q["tags"]
        
        print(f"[{i+1}/{len(queries)}] Scraping for: {keyword}...")
        
        # Fetch multiplier due to drops
        fetch_count = int(MAX_IMAGES_PER_QUERY * 1.5)
        crawler.crawl(keyword=keyword, max_num=fetch_count)
        
        # Process downloaded images
        saved_count = 0
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                success = processor.process_and_move_image(filepath, category, subcategory, tags, "Bing Images")
                if success:
                    saved_count += 1
                    
        # Clear remaining temporary downloads that didn't pass process_and_move_image
        for remaining in os.listdir(temp_dir):
            if os.path.isfile(os.path.join(temp_dir, remaining)):
                try:
                    os.remove(os.path.join(temp_dir, remaining))
                except:
                    pass
                    
        print(f"Saved {saved_count} valid images for {keyword}.")

    # Once scraping is done, clean up temp dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"Dataset compiled at {DATASET_DIR}.")
    
    # Zip it up (This will be huge!)
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.zip")
    zip_dataset(DATASET_DIR, zip_path)

if __name__ == "__main__":
    main()

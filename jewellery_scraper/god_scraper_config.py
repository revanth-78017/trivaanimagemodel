import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GODS_DATASET_DIR = os.path.join(BASE_DIR, "gods_dataset")

# Detailed categories for Gods
DEITIES = {
    "Shiva": ["shiva_lingam", "nataraja", "shiva_parvati", "dakshinamurthy", "bhairava"],
    "Vishnu": ["vishnu_avatar", "venkateshwara_balaji", "krishna", "rama", "narasimha", "jagannath"],
    "Goddesses": ["lakshmi", "saraswati", "durga", "kali", "parvati", "mariamman", "meenakshi"],
    "Ganesha": ["dagdusheth_ganpati", "lalbaugcha_raja", "dancing_ganesha", "sitting_ganesha", "ganesha_idol"],
    "Other_Deities": ["kartikeya_murugan", "hanuman", "surya", "navagraha", "ayyappan"]
}

ART_STYLES = [
    "tanjore painting", 
    "raja ravi varma style", 
    "mysore painting", 
    "modern 3d wallpaper", 
    "traditional wall art", 
    "temple architecture sculpture",
    "kerala mural"
]

MATERIALS = [
    "antique bronze idol", 
    "brass statue", 
    "marble moorti", 
    "black stone idol", 
    "panchaloha idol",
    "wooden carving",
    "gold plated idol"
]

def generate_god_queries():
    queries = []
    
    for category, subcategories in DEITIES.items():
        for subcat in subcategories:
            base_term = subcat.replace("_", " ")
            
            # Combine with Art Styles
            for style in ART_STYLES:
                keyword = f"indian god {base_term} {style} high quality"
                tags = f"{category.lower()}, {subcat.lower()}, {style}, painting/art"
                queries.append({
                    "keyword": keyword,
                    "category": category,
                    "subcategory": subcat,
                    "tags": tags
                })
                
            # Combine with Materials (Idols)
            for mat in MATERIALS:
                keyword = f"indian god {base_term} {mat} temple high quality"
                tags = f"{category.lower()}, {subcat.lower()}, {mat}, sculpture/idol"
                queries.append({
                    "keyword": keyword,
                    "category": category,
                    "subcategory": subcat,
                    "tags": tags
                })
                
    unique_queries = {q['keyword']: q for q in queries}.values()
    return list(unique_queries)

# Target massive image pull
MAX_IMAGES_PER_QUERY = 1500

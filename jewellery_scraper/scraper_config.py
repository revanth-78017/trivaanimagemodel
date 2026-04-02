import os
import itertools

# Base directory for all downloaded items
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Hierarchical Categories and Subcategories
CATEGORIES = {
    "Rings": ["antique_rings", "temple_rings", "modern_rings", "stone_rings", "wedding_bands", "adjustable_rings", "meenakari_rings", "filigree_rings"],
    "Necklaces": ["temple_necklaces", "antique_necklaces", "bridal_necklaces", "choker_necklaces", "haram_long_necklaces", "kundan_necklaces", "diamond_necklaces", "lightweight_necklaces"],
    "Earrings": ["jhumkas", "studs", "chandbali", "long_earrings", "temple_earrings", "stone_earrings", "daily_wear_earrings"],
    "Bangles_and_Bracelets": ["antique_bangles", "temple_bangles", "kada_bangles", "stone_bangles", "daily_wear_bangles", "bridal_bangles"],
    "Pendants": ["god_pendants", "name_pendants", "antique_pendants", "modern_pendants", "stone_pendants"],
    "Anklets": ["traditional_anklets", "modern_anklets", "bridal_anklets"],
    "Special": ["temple_jewellery", "bridal_sets", "customized_jewellery", "south_indian_traditional"]
}

STYLE_KEYWORDS = ["antique gold", "temple jewellery", "nakshi", "kundan", "meenakari", "filigree", "modern", "vintage", "royal", "lightweight", "heavy bridal"]
MOTIFS = ["lakshmi", "ganesha", "peacock", "floral", "mango", "coin kasu", "elephant", "lotus", None]
REGIONS = ["south indian", "traditional indian", None]
USE_CASES = ["bridal", "wedding", "daily wear", "festive", None]

def generate_queries():
    queries = []
    
    # We will procedurally generate keywords to cover a massive spread.
    for category, subcategories in CATEGORIES.items():
        for subcat in subcategories:
            base_term = subcat.replace('_', ' ')
            
            # Combine with a style
            for style in STYLE_KEYWORDS:
                # To keep combinations somewhat constrained but large (>200), we randomly sample or iterate selectively.
                # Here we generate a fixed set of robust combinations per subcategory+style pairing.
                
                # Motifs
                for motif in ["lakshmi", "peacock", "floral", None]:
                    query_parts = [style, base_term]
                    tags_parts = [category.lower(), subcat.lower(), style]
                    
                    if motif:
                        query_parts.append(f"{motif} design")
                        tags_parts.append(f"{motif} motif")
                        
                    # Add regional/usecase randomly or systematically
                    query_parts.append("jewellery")
                    tags_parts.append("indian jewellery")
                    
                    keyword = " ".join(query_parts)
                    tags = ", ".join(tags_parts)
                    
                    queries.append({
                        "keyword": keyword,
                        "category": category,
                        "subcategory": subcat,
                        "tags": tags
                    })
                    
    # The above generates ~1000+ combinations. 
    # Example: "antique gold temple_rings lakshmi design jewellery"
    
    # Deduplicate queries just in case
    unique_queries = {q['keyword']: q for q in queries}.values()
    return list(unique_queries)

# Target number of images per query.
# Total queries = ~1500
# 150,000 / 1500 = 100 images per query. We set to 500-1000 for safety against drops.
MAX_IMAGES_PER_QUERY = 1500

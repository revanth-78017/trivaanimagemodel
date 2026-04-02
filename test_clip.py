import torch
from transformers import CLIPProcessor, CLIPModel

device = "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

text_inputs = processor(text=["a photo"], return_tensors="pt", padding=True).to(device)

# Method 1
text_features_1 = model.get_text_features(**text_inputs)
if not isinstance(text_features_1, torch.Tensor):
    print("Method 1 returned object. Trying pooler_output...")
    pooler = text_features_1.pooler_output
    proj = model.text_projection(pooler)
    print("Shape after proj:", proj.shape)
else:
    print("Method 1 shape:", text_features_1.shape)
    
# Method 2
outputs = model(**text_inputs, pixel_values=torch.randn(1, 3, 224, 224))
print("Method 2 shape:", outputs.text_embeds.shape)

import torch
import os
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

def generate_custom_jewellery(prompt, output_filename="custom_jewellery_output.png"):
    model_base = "runwayml/stable-diffusion-v1-5"
    lora_dir = "./jewellery-model-lora"
    
    if not os.path.exists(lora_dir):
        print(f"Error: LoRA weights not found at {lora_dir}. Have you finished training?")
        return

    print("Loading base Stable Diffusion model...")
    pipe = StableDiffusionPipeline.from_pretrained(model_base, torch_dtype=torch.float32)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    print("Injecting custom Jewellery LoRA weights...")
    pipe.load_lora_weights(lora_dir)

    # Note: float16 is partially supported on MPS, float32 is safer for diffusers on mac, 
    # but we will move to MPS device
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    pipe.to(device)

    print(f"\nGenerating image on {device}...")
    print(f"Prompt: '{prompt}'")

    # Generate the image
    image = pipe(
        prompt, 
        num_inference_steps=25, 
        guidance_scale=7.5,
        generator=torch.manual_seed(42)
    ).images[0]
    
    image.save(output_filename)
    print(f"\nImage successfully saved as {output_filename}! ✅")

if __name__ == "__main__":
    # Feel free to change this prompt to test different inputs!
    test_prompt = "A photo of an antique temple jewellery ring with rubies, indian god style jewellery, ring"
    generate_custom_jewellery(test_prompt)

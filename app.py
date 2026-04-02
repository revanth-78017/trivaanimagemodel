import gradio as gr
import torch
import os
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

# Initialization variables
model_base = "runwayml/stable-diffusion-v1-5"
lora_dir = "./jewellery-model-lora"
pipe = None
device = "mps" if torch.backends.mps.is_available() else "cpu"

def load_pipeline():
    global pipe
    if pipe is None:
        print("Loading base Stable Diffusion model...")
        pipe = StableDiffusionPipeline.from_pretrained(model_base, torch_dtype=torch.float32)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

        if os.path.exists(lora_dir):
            print("Injecting custom Jewellery LoRA weights...")
            pipe.load_lora_weights(lora_dir)
        else:
            print(f"Warning: LoRA weights not found at {lora_dir}. The base model will be used since training is not finished yet.")

        pipe.to(device)
    return pipe

def generate_image(prompt, guidance_scale, num_inference_steps):
    pipeline = load_pipeline()
    print(f"Generating image on {device}...")
    print(f"Prompt: '{prompt}'")
    
    # Generate the image
    image = pipeline(
        prompt, 
        num_inference_steps=int(num_inference_steps), 
        guidance_scale=float(guidance_scale),
        generator=torch.manual_seed(42)  # Optional: remove for random seeds every time
    ).images[0]
    
    return image

# Build the Gradio interface
with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("<h1 style='text-align: center;'>💍 Custom Jewellery Image Generator</h1>")
        gr.Markdown("<p style='text-align: center; color: gray;'>Type a description of your dream jewellery piece, and your custom AI model will generate it!</p>")
        
        with gr.Row():
            with gr.Column(scale=1):
                prompt = gr.Textbox(
                    label="Jewellery Description (Prompt)", 
                    placeholder="A photo of an antique temple jewellery ring with rubies, indian god style jewellery, ring",
                    lines=4
                )
                
                with gr.Accordion("Advanced Settings", open=False):
                    guidance_scale = gr.Slider(label="Guidance Scale", minimum=1.0, maximum=20.0, value=7.5, step=0.5, info="How strictly the AI follows your prompt.")
                    inference_steps = gr.Slider(label="Inference Steps", minimum=10, maximum=50, value=25, step=1, info="Quality vs Speed.")
                    
                generate_btn = gr.Button("✨ Generate Jewellery", variant="primary")
                
            with gr.Column(scale=1):
                output_image = gr.Image(label="Generated Result", type="pil", height=400)
                
        generate_btn.click(
            fn=generate_image,
            inputs=[prompt, guidance_scale, inference_steps],
            outputs=output_image
        )

if __name__ == "__main__":
    print("Launching Jewellery AI Web Interface...")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=True)

#!/bin/bash

# Configuration
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export DATASET_DIR="./dataset_sorted"
export OUTPUT_DIR="./jewellery-model-lora"

echo "Starting LoRA training on the Jewellery Dataset..."
echo "This will utilize MPS acceleration natively via Hugging Face accelerate."

# If you haven't configured accelerate yet, this will use default settings
accelerate launch train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --train_data_dir=$DATASET_DIR \
  --resolution=512 --random_flip \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=2000 \
  --learning_rate=1e-04 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --seed=42 \
  --output_dir=$OUTPUT_DIR \
  --validation_prompt="A photo of an intricate gold temple necklace, indian god style jewellery, necklace" \
  --checkpointing_steps=500

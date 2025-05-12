import os
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import requests
import torch
import shutil
import tarfile

MODEL_URL = "https://huggingface.co/meta-llama/Llama-3-8B/resolve/main/model.tar.gz"
MODEL_PATH = "./models/llama3"


def download_and_extract_model():
    """Downloads and extracts the LLaMA 3 model if not already present."""
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH, exist_ok=True)
        print("Downloading LLaMA 3 model...")
        response = requests.get(MODEL_URL, stream=True)
        model_tar_path = os.path.join(MODEL_PATH, "model.tar.gz")
        
        with open(model_tar_path, "wb") as file:
            shutil.copyfileobj(response.raw, file)
        
        print("Extracting model...")
        with tarfile.open(model_tar_path, "r:gz") as tar:
            tar.extractall(path=MODEL_PATH)
        
        os.remove(model_tar_path)
        print("Model downloaded and extracted successfully.")
    else:
        print("Model already exists.")


def load_model():
    """Loads the MLX-based LLaMA 3 model."""
    model = nn.Sequential(
        nn.Linear(4096, 4096),
        nn.ReLU(),
        nn.Linear(4096, 50257)  # Example model structure
    )
    return model


def generate_response(model, prompt):
    """Generates a response based on a given prompt."""
    print(f"Processing prompt: {prompt}")
    # Placeholder inference logic
    response = "[Generated response from LLaMA 3]"
    return response


def main():
    """Main function to initialize model and interact via CLI."""
    download_and_extract_model()
    model = load_model()
    
    print("LLaMA 3 Model is ready. Type your prompt below:")
    while True:
        prompt = input("You: ")
        if prompt.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        response = generate_response(model, prompt)
        print("LLaMA 3:", response)


if __name__ == "__main__":
    main()


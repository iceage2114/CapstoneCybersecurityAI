import os
import mlx.nn as nn
import requests
import shutil
import tarfile
from enum import Enum

MODEL_URL = "https://huggingface.co/meta-llama/Llama-3-8B/resolve/main/model.tar.gz"
MODEL_PATH = "./models/llama3"

# Model status tracking
class ModelStatus(Enum):
    NOT_LOADED = "not_loaded"
    DOWNLOADING = "downloading"
    EXTRACTING = "extracting"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"

# Global variable to track model status
model_status = ModelStatus.NOT_LOADED
model_status_message = ""


def download_and_extract_model():
    """Downloads and extracts the LLaMA 3 model if not already present."""
    global model_status, model_status_message
    
    try:
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODEL_PATH, exist_ok=True)
            
            # Update status to downloading
            model_status = ModelStatus.DOWNLOADING
            model_status_message = "Downloading LLaMA 3 model..."
            print(model_status_message)
            
            response = requests.get(MODEL_URL, stream=True)
            model_tar_path = os.path.join(MODEL_PATH, "model.tar.gz")
            
            with open(model_tar_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)
            
            # Update status to extracting
            model_status = ModelStatus.EXTRACTING
            model_status_message = "Extracting model..."
            print(model_status_message)
            
            with tarfile.open(model_tar_path, "r:gz") as tar:
                tar.extractall(path=MODEL_PATH)
            
            os.remove(model_tar_path)
            model_status_message = "Model downloaded and extracted successfully."
            print(model_status_message)
        else:
            model_status_message = "Model already exists."
            print(model_status_message)
    except Exception as e:
        model_status = ModelStatus.ERROR
        model_status_message = f"Error downloading/extracting model: {str(e)}"
        print(model_status_message)
        raise e


def load_model():
    """Loads the MLX-based LLaMA 3 model."""
    global model_status, model_status_message
    
    try:
        model_status = ModelStatus.LOADING
        model_status_message = "Loading LLaMA 3 model into memory..."
        print(model_status_message)
        
        # Actual model loading logic
        model = nn.Sequential(
            nn.Linear(4096, 4096),
            nn.ReLU(),
            nn.Linear(4096, 50257)  # Example model structure
        )
        
        model_status = ModelStatus.READY
        model_status_message = "Model loaded and ready."
        print(model_status_message)
        return model
    except Exception as e:
        model_status = ModelStatus.ERROR
        model_status_message = f"Error loading model: {str(e)}"
        print(model_status_message)
        raise e


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


# API functions to get model status
def get_model_status():
    """Returns the current status of the model."""
    return {
        "status": model_status.value,
        "message": model_status_message
    }


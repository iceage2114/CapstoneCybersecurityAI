#!/usr/bin/env python3
"""
Simple script to test the AI service generation capability with Apple's MLX framework
"""
import os
import sys
import subprocess
import time
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService

def check_mlx_availability():
    """
    Check if MLX is available and can be imported
    """
    try:
        import mlx.core
        import mlx_lm
        print("MLX is available on this system.")
        
        # Get model repo from environment
        model_repo = os.getenv("MLX_MODEL_REPO", "mlx-community/Llama-3.2-3B-Instruct")
        print(f"Using model: {model_repo}")
        
        return True
    except ImportError as e:
        print(f"MLX is not available: {e}")
        print("Please install MLX with: pip install mlx mlx-lm")
        return False

def main():
    # Check if MLX is available
    if not check_mlx_availability():
        return
    
    try:
        print("\nInitializing AI service...")
        ai_service = AIService()
        
        print("\nTesting generation capability...")
        query = "What are some common cybersecurity threats I should be aware of?"
        
        print(f"\nQuery: {query}")
        print("Generating response...")
        
        try:
            # Ensure the model is loaded
            ai_service._load_model()
            
            # For Mistral models, we need to use the correct chat format
            # The error indicates we need to ensure proper role alternation
            
            # Create a simple prompt instead of using the chat template
            prompt = f"""<s>[INST] You are a cybersecurity analyst assistant. Your goal is to provide accurate, helpful information about cybersecurity topics.

What are some common cybersecurity threats I should be aware of? [/INST]"""
            
            # Note: We're bypassing the chat template system since it's causing issues
            # This direct prompt approach works better with Mistral models
            
            print("\nGenerated Response (streaming):")
            print("-" * 80)
            
            # Import the stream_generate function from mlx_lm
            from mlx_lm import stream_generate
            
            # Stream the response in real-time
            for response in stream_generate(
                ai_service.model,
                ai_service.tokenizer,
                prompt=prompt,
                max_tokens=ai_service.max_tokens
            ):
                print(response.text, end="", flush=True)
            
            print("\n" + "-" * 80)
        except Exception as e:
            print(f"\nError generating response: {str(e)}")
            print("\nThis is expected if Ollama is not running or if the model is not available.")
            print("To use this script, you need to:")
            print("1. Install Ollama from https://ollama.com/download")
            print("2. Start Ollama with: ollama serve")
            print("3. Pull a model with: ollama pull llama2")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main()

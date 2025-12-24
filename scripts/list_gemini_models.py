#!/usr/bin/env python3
"""
Diagnostic script to list available Gemini models for your API key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
print("\n🔍 Listing available Gemini models...\n")

genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    
    print("=" * 80)
    print("AVAILABLE MODELS:")
    print("=" * 80)
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Input Token Limit: {model.input_token_limit:,}")
            print(f"   Output Token Limit: {model.output_token_limit:,}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED MODEL FOR RILEY:")
    print("=" * 80)
    
    # Find the best model
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            name = model.name.replace('models/', '')
            if 'flash' in name.lower() and '2.0' in name:
                print(f"\n🎯 Use: {name}")
                print(f"   (Fastest, newest model)")
                break
            elif 'pro' in name.lower() and '1.5' in name:
                print(f"\n🎯 Use: {name}")
                print(f"   (Balanced performance)")
                break
    
except Exception as e:
    print(f"\n❌ Error listing models: {e}")
    print("\nThis might mean:")
    print("1. Your API key is invalid")
    print("2. Your API key doesn't have Gemini API access")
    print("3. You need to enable Gemini API in Google Cloud Console")

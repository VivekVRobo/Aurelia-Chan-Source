#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Test Script for Aurelia-chan
===================================
Tests if Ollama is installed and working correctly
"""

import requests
import json
import time

def test_ollama_connection():
    """Test if Ollama server is running"""
    print("=" * 70)
    print("    OLLAMA CONNECTION TEST")
    print("=" * 70)
    print()
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Ollama server is running on http://localhost:11434")
            print()
            models = response.json().get('models', [])
            if models:
                print("Available models:")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("No models installed yet. You need to pull a model first.")
                print("Run: ollama pull llama3.2")
            return True
        else:
            print(f"ERROR: Ollama server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama server")
        print()
        print("Make sure Ollama is installed and running:")
        print("1. Install Ollama from https://ollama.ai/download")
        print("2. Run: ollama serve")
        print("3. Try this test again")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_ollama_generation(model="llama3.2"):
    """Test if Ollama can generate text"""
    print()
    print("=" * 70)
    print("    OLLAMA TEXT GENERATION TEST")
    print("=" * 70)
    print()
    
    try:
        print(f"Testing model: {model}")
        print("Prompt: 'Hello, how are you?'")
        print()
        
        start_time = time.time()
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': model,
            'prompt': 'Hello, how are you?',
            'stream': False
        }, timeout=30)
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"Response: {generated_text}")
            print()
            print(f"Generation time: {elapsed:.2f} seconds")
            print("SUCCESS: Ollama is working correctly")
            return True
        else:
            print(f"ERROR: Generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out (30 seconds)")
        print("This might indicate your model is too large for your computer")
        print("Try a smaller model: ollama pull llama3.2:3b")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_aurelia_context():
    """Test Ollama with Aurelia-chan context"""
    print()
    print("=" * 70)
    print("    AURELIA-CHAN CONTEXT TEST")
    print("=" * 70)
    print()
    
    aurelia_prompt = """You are Aurelia-chan, a 33-year-old executive career mentor with an anime/editorial character interface. You are calm, precise, mature, and authoritative without hostility. You provide strategic career advice with a professional executive tone.

User asks: "I need leadership development advice"

Provide a helpful, professional response as Aurelia-chan:"""
    
    try:
        print("Testing with Aurelia-chan character context...")
        print()
        
        start_time = time.time()
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'llama3.2',
            'prompt': aurelia_prompt,
            'stream': False
        }, timeout=30)
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"Aurelia-chan Response: {generated_text}")
            print()
            print(f"Generation time: {elapsed:.2f} seconds")
            print("SUCCESS: Ollama can maintain character context")
            return True
        else:
            print(f"ERROR: Generation failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print()
    print("=" * 70)
    print("           AURELIA-CHAN OLLAMA INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Test 1: Connection
    connection_ok = test_ollama_connection()
    
    if not connection_ok:
        print()
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print()
        print("Please follow these steps:")
        print("1. Install Ollama from https://ollama.ai/download")
        print("2. Run: ollama serve")
        print("3. Run: ollama pull llama3.2")
        print("4. Run this test script again")
        return
    
    # Test 2: Text generation
    generation_ok = test_ollama_generation()
    
    if not generation_ok:
        print()
        print("=" * 70)
        print("MODEL SETUP REQUIRED")
        print("=" * 70)
        print()
        print("Please pull a model:")
        print("Run: ollama pull llama3.2")
        print("Or for older computers: ollama pull llama3.2:3b")
        return
    
    # Test 3: Aurelia context
    context_ok = test_aurelia_context()
    
    print()
    print("=" * 70)
    print("    FINAL RESULTS")
    print("=" * 70)
    print(f"Connection Test: {'PASS' if connection_ok else 'FAIL'}")
    print(f"Generation Test: {'PASS' if generation_ok else 'FAIL'}")
    print(f"Context Test: {'PASS' if context_ok else 'FAIL'}")
    print()
    
    if connection_ok and generation_ok and context_ok:
        print("✅ ALL TESTS PASSED - Ollama is ready for integration!")
        print()
        print("Next step: Integrate Ollama with Aurelia-chan chat system")
    else:
        print("❌ SOME TESTS FAILED - Please fix the issues above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Aurelia-chan Free & Owned Voice Generator Script
------------------------------------------------
This script uses edge-tts (free neural voice API) to batch-generate 
Aurelia's owned audio files for offline use in the web application.

Usage:
    pip install edge-tts
    python generate_voice.py
"""

import os
import asyncio

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "audio_pack")

VOICE_LINES = [
    {
        "filename": "welcome_en.mp3",
        "text": "Good day. I am Aurelia, your executive career mentor. How may I assist your professional trajectory today?",
        "voice": "en-US-AvaNeural",
        "pitch": "-5Hz",
        "rate": "-8%"
    },
    {
        "filename": "greeting_ja.mp3",
        "text": "ごきげんよう。私はオーレリア、あなたのエグゼクティブ・キャリアメンターです。どのような戦略的課題に取り組みましょうか？",
        "voice": "ja-JP-NanamiNeural",
        "pitch": "-4Hz",
        "rate": "-6%"
    },
    {
        "filename": "approval_en.mp3",
        "text": "Impressive achievement. Your strategic execution aligns perfectly with high-level leadership standards.",
        "voice": "en-US-AvaNeural",
        "pitch": "-5Hz",
        "rate": "-8%"
    },
    {
        "filename": "warning_en.mp3",
        "text": "Caution. Proceeding without quantifiable metrics or clear alignment will compromise your strategic posture.",
        "voice": "en-US-AvaNeural",
        "pitch": "-5Hz",
        "rate": "-8%"
    }
]

async def generate_voices():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating Aurelia-chan owned audio pack in: {OUTPUT_DIR}")
    
    if not HAS_EDGE_TTS:
        print("[WARNING] edge-tts python package is not installed.")
        print("To generate offline audio clips, run: pip install edge-tts")
        return

    success_count = 0
    failure_count = 0
    
    for line in VOICE_LINES:
        filepath = os.path.join(OUTPUT_DIR, line["filename"])
        print(f"Synthesizing {line['filename']} ({line['voice']})...")
        
        try:
            communicate = edge_tts.Communicate(
                text=line["text"],
                voice=line["voice"],
                rate=line["rate"],
                pitch=line["pitch"]
            )
            await communicate.save(filepath)
            print(f"  ✓ Saved -> {filepath}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed to generate {line['filename']}: {str(e)}")
            failure_count += 1
            # Continue with next file instead of stopping

    print(f"\n[SUMMARY] Audio pack generation complete!")
    print(f"  Successful: {success_count}/{len(VOICE_LINES)}")
    if failure_count > 0:
        print(f"  Failed: {failure_count}/{len(VOICE_LINES)}")
    print("  All audio files are 100% free and owned by you.")

if __name__ == "__main__":
    asyncio.run(generate_voices())

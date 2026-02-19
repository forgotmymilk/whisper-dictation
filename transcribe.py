#!/usr/bin/env python3
"""
Faster-Whisper File Transcription
Optimized for RTX 4070 Ti Super

Usage:
    python transcribe.py <audio_file.wav>
    python transcribe.py (will prompt for file)
"""

import sys
import os
from faster_whisper import WhisperModel

def main():
    # Get audio file path
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("Drag and drop an audio file onto start-transcribe.bat")
        print("Or run: python transcribe.py <audio_file.wav>")
        audio_file = input("\nEnter audio file path: ").strip().strip('"')
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        return

    print("=" * 60)
    print("🎙️ Faster-Whisper Transcription")
    print("=" * 60)
    print(f"\nLoading Large-v3 model (first run will download ~3GB)...")
    print("This may take a few minutes...")
    
    try:
        # Initialize model with GPU and float16 for best performance
        model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16"
        )
        
        print("✓ Model loaded successfully!")
        print(f"\nTranscribing: {audio_file}")
        print("-" * 60)
        
        # Transcribe with optimized settings
        segments, info = model.transcribe(
            audio_file,
            beam_size=5,
            best_of=5,
            condition_on_previous_text=True,
            language=None  # Auto-detect
        )
        
        print(f"\n📝 Detected language: {info.language} (probability: {info.language_probability:.2f})")
        print("\nTranscription:")
        print("=" * 60)
        
        full_text = []
        for segment in segments:
            print(segment.text)
            full_text.append(segment.text)
        
        print("=" * 60)
        
        # Save to file
        output_file = audio_file.rsplit('.', 1)[0] + "_transcription.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(full_text))
        
        print(f"\n✓ Saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check CUDA is installed: python -c \"import torch; print(torch.cuda.is_available())\"")
        print("2. For CPU mode, change device='cuda' to device='cpu'")
        print("3. Reduce compute_type to 'int8' if VRAM issues")

if __name__ == "__main__":
    main()

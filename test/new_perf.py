# load_and_register.py
import pyrootutils
ROOT = pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import os
import argparse
import json
import time
import soundfile as sf
import asyncio
from indextts.infer_vllm import IndexTTS
from pathlib import Path

async def main():
    gpu_memory_utilization=0.7
    model_dir=ROOT / "checkpoints/IndexTeam/IndexTTS-1___5"
    cfg_path = model_dir / "config.yaml"
    print("Loading TTS model...")
    tts = IndexTTS(
        model_dir=model_dir, 
        cfg_path=cfg_path, 
        gpu_memory_utilization=gpu_memory_utilization
    )
    speaker_path =ROOT /"assets/speaker.json"
    voices=[]
    if speaker_path.exists():
        print("Registering speakers...")
        speaker_dict = json.load(open(speaker_path, 'r'))
        print(speaker_dict)
        for speaker, audio_paths in speaker_dict.items():
            audio_paths_ = []
            for audio_path in audio_paths:
                full_audio_path = ROOT / audio_path
                if full_audio_path.exists():
                    audio_paths_.append(full_audio_path)
                else:
                    print(f"Warning: Audio file not found: {full_audio_path}")
            if audio_paths_:
                voices.append(speaker)
                tts.registry_speaker(speaker, audio_paths_)
                print(f"Registered speaker: {speaker}")
            else:
                print(f"Warning: No valid audio files for speaker: {speaker}")
            print(f"Registering speaker: {speaker},audio paths: {audio_paths_}")
    
    print("Model loaded successfully!")
    
    # 如果有可用说话人，进行试运行TTS
    if voices:
        test_text = "你好，这是一个TTS模型加载和说话人注册的测试。"
        test_speaker = voices[0]  # 使用第一个说话人
        
        print(f"Running test TTS with speaker '{test_speaker}' and text: {test_text}")
        
        try:
            start_time = time.time()
            # 使用 await 调用异步函数
            sr, wav = await tts.infer_with_ref_audio_embed(test_speaker, test_text)
            end_time = time.time()
            
            print(f"TTS inference completed in {end_time - start_time:.2f} seconds")
            print(f"Generated audio sample rate: {sr}Hz")
            print(f"Generated audio shape: {wav.shape}")
            
            # 保存测试音频
            # 确保output目录存在
            output_dir = ROOT / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_output.wav"
            sf.write(output_path, wav, sr, format='WAV')
            print(f"Test audio saved to: {output_path}")
            
        except Exception as e:
            print(f"Error during TTS inference: {e}")
    else:
        print("No voices available for testing")

if __name__ == "__main__":
    # 使用 asyncio.run() 来运行异步主函数
    asyncio.run(main())
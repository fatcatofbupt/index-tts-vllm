
import os
import pyrootutils
ROOT = pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import asyncio
import io
import traceback
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse
import json
import asyncio
import time
from pathlib import Path
import numpy as np
import soundfile as sf

from indextts.infer_vllm import IndexTTS

model_path=Path("/home/tts/.cache/modelscope/hub/models/IndexTeam/IndexTTS-1___5/")
model_path=Path("/home/tts/.cache/modelscope/hub/IndexTeam/IndexTTS-1.5/")
tts = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts
    gpu_memory_utilization=0.85
    #model_dir=ROOT / "checkpoints/IndexTeam/IndexTTS-1___5"
    model_dir=model_path
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
    yield
    # Clean up the ML models and release the resources
    # ml_models.clear()

app = FastAPI(lifespan=lifespan)

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        global tts
        if tts is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "TTS model not initialized"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "Service is running",
                "timestamp": time.time()
            }
        )
    except Exception as ex:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(ex)
            }
        )


@app.post("/tts_url", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api_url(request: Request):
    try:
        data = await request.json()
        text = data.get('text',"")
        audio_paths = data.get("audio_paths", [])
        seed = data.get("seed", 8)

        global tts
        sr, wav = await tts.infer(audio_paths, text, seed=seed)
        
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, wav, sr, format='WAV')
            wav_bytes = wav_buffer.getvalue()

        return Response(content=wav_bytes, media_type="audio/wav")
    
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )


@app.post("/tts", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        character = data["character"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)
        
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, wav, sr, format='WAV')
            wav_bytes = wav_buffer.getvalue()

        return Response(content=wav_bytes, media_type="audio/wav")
    
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )



@app.get("/audio/voices")
async def tts_voices():
    """ additional function to provide the list of available voices, in the form of JSON """
    current_file_path = os.path.abspath(__file__)
    cur_dir = os.path.dirname(current_file_path)
    speaker_path = os.path.join(cur_dir, "assets/speaker.json")
    if os.path.exists(speaker_path):
        speaker_dict = json.load(open(speaker_path, 'r'))
        return speaker_dict
    else:
        return []



@app.post("/audio/speech", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api_openai(request: Request):
    """ OpenAI competible API, see: https://api.openai.com/v1/audio/speech """
    try:
        data = await request.json()
        text = data["input"]
        character = data["voice"]
        #model param is omitted
        _model = data["model"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)
        
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, wav, sr, format='WAV')
            wav_bytes = wav_buffer.getvalue()

        return Response(content=wav_bytes, media_type="audio/wav")
    
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=11996)
    #parser.add_argument("--model_dir", type=str, default="/path/to/IndexTeam/Index-TTS")
    parser.add_argument("--model_dir", type=str, default=model_path)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.25)
    args = parser.parse_args()

    uvicorn.run(app=app, host=args.host, port=args.port)

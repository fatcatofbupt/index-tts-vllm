#!/bin/bash
VLLM_USE_V1=0 python indextts/cli.py   --model_dir ./checkpoints/IndexTeam/IndexTTS-1___5/ --config ./checkpoints/IndexTeam/IndexTTS-1___5/config.yaml  --voice ./assets/67a0410a81974dbb94a51c211aee2499/0.16kclean.wav   "逾期本金是32545元，之前你还过1900元，剩下的今天结清就能免掉所有利息和罚息"

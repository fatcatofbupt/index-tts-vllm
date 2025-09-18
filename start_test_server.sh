#!/bin/bash
VLLM_USE_V1=0 uvicorn  test_server:app --host 0.0.0.0 --port 11996 --workers 1

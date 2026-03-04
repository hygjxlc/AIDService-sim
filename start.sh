#!/bin/bash
# AID-Service Startup Script (Linux/macOS)
cd "$(dirname "$0")"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

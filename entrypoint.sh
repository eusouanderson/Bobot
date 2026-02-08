#!/usr/bin/env bash
set -e

# Start Ollama server
ollama serve > /var/log/ollama.log 2>&1 &

# Optional: preload model if configured
if [ -n "${LLM_MODEL:-}" ]; then
  ollama pull "$LLM_MODEL" || true
fi

exec python -m bobot

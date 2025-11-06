import os
import requests
from typing import Union

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL_NAME", "mistral:7b"))

def generate_with_ollama(
    prompt: str,
    max_tokens: int = 512,
    stream: bool = False,
    timeout: int = 120
) -> Union[str, None]:
    """
    Compatible avec Ollama <= 0.13.x (utilise /api/generate)
    Gère le mode streaming et non-streaming.
    """
    url = OLLAMA_URL.rstrip("/") + "/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": stream
    }

    resp = requests.post(url, json=payload, timeout=timeout, stream=stream)
    resp.raise_for_status()

    # Si le streaming est activé, on concatène les morceaux de texte
    if stream:
        output = ""
        for line in resp.iter_lines():
            if line:
                try:
                    j = line.decode("utf-8")
                    if '"response":' in j:
                        part = j.split('"response":')[-1].split(',"done":')[0]
                        part = part.strip().lstrip(':').lstrip('"').rstrip('"').replace('\\n', '\n')
                        output += part
                except Exception:
                    continue
        return output.strip()

    # Sinon, lecture directe du JSON complet
    try:
        j = resp.json()
        if isinstance(j, dict):
            if "response" in j:
                return j["response"]
            if "output" in j:
                o = j["output"]
                if isinstance(o, list):
                    return "".join(o)
                return str(o)
        return resp.text
    except Exception:
        return resp.text

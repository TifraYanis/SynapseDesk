from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer, CrossEncoder
models = [
    "intfloat/multilingual-e5-base",
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "mistralai/Mistral-7B-Instruct-v0.2"
]
for m in models:
    print("Downloading", m)
    try:
        if "cross-encoder" in m:
            CrossEncoder(m)
        elif "mistralai" in m:
            AutoTokenizer.from_pretrained(m, use_fast=True)
            AutoModelForCausalLM.from_pretrained(m, trust_remote_code=True)
        else:
            SentenceTransformer(m)
    except Exception as e:
        print("Warning: couldn't download model", m, e)

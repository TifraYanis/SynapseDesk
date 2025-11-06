import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from docx import Document

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def read_file_content(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    try:
        if ext in [".md", ".txt", ".py", ".log"]:
            return file_path.read_text(encoding="utf-8")

        elif ext in [".html", ".htm"]:
            soup = BeautifulSoup(file_path.read_text(encoding="utf-8"), "html.parser")
            return soup.get_text(separator="\n")

        elif ext in [".json", ".jsonl"]:
            try:
                data = json.load(open(file_path, encoding="utf-8"))
                if isinstance(data, dict):
                    return json.dumps(data, indent=2, ensure_ascii=False)
                elif isinstance(data, list):
                    return "\n".join(json.dumps(d, ensure_ascii=False) for d in data)
            except Exception:
                return file_path.read_text(encoding="utf-8")

        elif ext in [".docx"]:
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        else:
            return ""  # Fichiers non textuels ignorés (PDF, images, etc.)

    except Exception as e:
        print(f"[WARN] Erreur lecture {file_path.name} : {e}")
        return ""

def build_corpus():
    corpus = []
    for file_path in DATA_DIR.glob("**/*"):
        if file_path.is_file():
            text = read_file_content(file_path)
            if len(text.strip()) > 20:
                corpus.append({
                    "path": str(file_path.relative_to(BASE_DIR)),
                    "text": text.strip()
                })

    output_path = OUTPUT_DIR / "corpus.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in corpus:
            json.dump(doc, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Corpus généré ({len(corpus)} documents) → {output_path}")

if __name__ == "__main__":
    print(f"📂 Ingestion des données depuis {DATA_DIR}")
    build_corpus()

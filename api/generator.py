import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, GenerationConfig

MODEL_NAME = os.getenv("MISTRAL_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
DEVICE = os.getenv("CUDA_DEVICE", "")  # vide = CPU

class Generator:
    """
    Générateur de réponses contextuelles basé sur Hugging Face.
    Objectif : privilégier les informations issues du contexte RAG (docs internes)
    avant d'utiliser les connaissances génériques du modèle.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        print(f"[Generator] Initialisation du modèle : {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto" if DEVICE != "" else None
        )

    def synthesize(self, question: str, contexts: list, max_new_tokens: int = 256) -> str:
        """
        Génère une réponse à partir d'une question et d'un ensemble de contextes.
        Les contextes sont fournis par le moteur RAG (documents internes les plus pertinents).
        """
        prompt = self.build_prompt(question, contexts)
        gencfg = GenerationConfig(max_new_tokens=max_new_tokens, temperature=0.2, top_p=0.9)
        outputs = self.pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False, generation_config=gencfg)
        return outputs[0]["generated_text"]

    def build_prompt(self, question: str, contexts: list) -> str:
        """
        Construit le prompt en combinant les documents internes et la question utilisateur.
        Objectif : guider le modèle à prioriser les informations d’entreprise.
        """
        # Concatène les extraits contextuels du RAG
        if contexts:
            ctx_block = "\n\n---\n\n".join(
                [f"📄 Source ({c['path']}):\n{c['text']}" for c in contexts]
            )
        else:
            ctx_block = "(Aucun document interne trouvé, réponse basée sur la connaissance générale du modèle.)"

        # Prompt clair et hiérarchisé
        prompt = f"""
Tu es un assistant virtuel d'entreprise fiable et professionnel.
Ta mission est d'aider les collaborateurs (data, RH, support, produit, etc.) à trouver
des réponses claires en utilisant d'abord les informations internes disponibles.

Question posée :
{question}

Contexte interne récupéré :
{ctx_block}

Consignes :
1. Si les documents internes contiennent des éléments pertinents, fonde ta réponse dessus.
2. Sinon, réponds de manière neutre et professionnelle à partir de tes connaissances générales.
3. Structure la réponse avec ces sections :
   - **Résumé clair**
   - **Détails ou explications**
   - **Actions / Prochaines étapes**
   - **Sources internes citées (si disponibles)**

Réponse :
"""
        return prompt.strip()

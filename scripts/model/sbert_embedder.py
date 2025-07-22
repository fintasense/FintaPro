# scripts/model/sbert_embedder.py

from sentence_transformers import SentenceTransformer, util
import torch
from pathlib import Path

class SBERTEmbedder:
    """
    A simple SBERT wrapper to encode terms and perform semantic matching.

    - model_dir: directory containing a fine-tuned SBERT model,
                 or None to attempt loading a local ./models/sbert_trained folder,
                 or fallback to a pretrained HuggingFace checkpoint.
    """
    def __init__(self, model_dir: str = None):
        # Determine default local path: project_root/models/sbert_trained
        default_dir = Path(__file__).resolve().parents[1].parent / 'models' / 'sbert_trained'
        chosen_dir = Path(model_dir) if model_dir else default_dir
        print(f"[SBERTEmbedder] Project root: {default_dir.parent}")
        print(f"[SBERTEmbedder] Trying to load from: {chosen_dir}")

        # Attempt to load local model
        if chosen_dir.exists() and (chosen_dir / 'config.json').exists():
            try:
                self.model = SentenceTransformer(str(chosen_dir))
                print(f"[SBERTEmbedder] Loaded local model from {chosen_dir}")
            except Exception as e:
                print(f"[SBERTEmbedder] Failed to load local model: {e}")
                print("[SBERTEmbedder] Falling back to default HF model")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            print("[SBERTEmbedder] Local model not found or missing config.json. Using default HF model")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Move to GPU if available
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')

    def encode_terms(self, terms: list[str]):
        """
        Encode a list of standard terms into embeddings tensor.

        returns: Tensor shape (len(terms), dim)
        """
        return self.model.encode(
            terms,
            convert_to_tensor=True,
            show_progress_bar=False
        )

    def semantic_match(
        self,
        label: str,
        std_embeds,
        terms_list: list[str]
    ) -> tuple[str, float]:
        """
        Given a cleaned label, compute its embedding and cosine-similarity
        against standard term embeddings. Return the best-matching term and score.

        returns: (best_term, cosine_score)
        """
        cand_embed = self.model.encode(label, convert_to_tensor=True)
        cos_scores = util.cos_sim(cand_embed, std_embeds)[0]
        best_idx = int(torch.argmax(cos_scores))
        best_score = float(cos_scores[best_idx])
        return terms_list[best_idx], best_score

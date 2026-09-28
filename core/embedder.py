"""
embedder.py - The AI Brain of Cache-Craft

This module loads a pre-trained sentence transformer model and converts
natural language text into dense vector embeddings (arrays of 384 numbers).
These vectors capture the MEANING of a sentence, not just the words.

Example:
    "What is Q3 revenue?" -> [0.12, -0.45, 0.89, ... 384 numbers]
    "Third quarter earnings?" -> [0.11, -0.44, 0.88, ... 384 numbers]
    These two vectors will be very close in vector space (high cosine similarity)
    because they MEAN the same thing, even though the words are different.
"""

from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
import time


class Embedder:
    """Handles loading the AI model and converting text to vectors."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Load the AI model into memory.

        Args:
            model_name: Which pre-trained model to use.
                        'all-MiniLM-L6-v2' is small (80MB), fast, and accurate.
        """
        print(f"[Embedder] Loading model '{model_name}'...")
        start = time.time()
        self.model = SentenceTransformer(model_name)
        elapsed = time.time() - start
        print(f"[Embedder] Model loaded in {elapsed:.2f} seconds.")

    def encode(self, text: str) -> list[float]:
        """
        Convert a sentence into a vector (list of 384 numbers).

        Args:
            text: Any natural language string.

        Returns:
            A list of 384 floating-point numbers representing the meaning.
        """
        vector = self.model.encode(text)
        return vector.tolist()

    def encode_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """
        Convert a batch of sentences into vectors efficiently.
        """
        vectors = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """
        Calculate how similar two vectors are using Cosine Similarity.

        The formula is:
            similarity = (A . B) / (||A|| * ||B||)

        Returns a score between 0.0 (completely different) and 1.0 (identical).

        Args:
            vec_a: First vector (list of 384 floats).
            vec_b: Second vector (list of 384 floats).

        Returns:
            A float between 0.0 and 1.0.
        """
        score = dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b))
        return float(score)

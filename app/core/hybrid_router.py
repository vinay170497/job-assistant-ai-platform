from app.core.intent_registry import IntentRegistry
from app.core.bm25_index import BM25Index
import numpy as np
import torch
from sentence_transformers import util


class HybridRouter:

    def __init__(self):
        self.semantic_registry = IntentRegistry()
        self.bm25 = BM25Index(self.semantic_registry.intent_definitions)

        # Fusion weights
        self.embedding_weight = 0.65
        self.bm25_weight = 0.5

        # Decision threshold
        self.oos_threshold = 0.45

    # --------------------------------------------------
    # Normalize scores (ONLY for fusion ranking)
    # --------------------------------------------------
    def normalize(self, scores: dict):
        values = np.array(list(scores.values()))

        if len(values) == 0:
            return scores

        min_val = values.min()
        max_val = values.max()

        if max_val - min_val == 0:
            return {k: 0.0 for k in scores}

        return {
            k: (v - min_val) / (max_val - min_val)
            for k, v in scores.items()
        }

    # --------------------------------------------------
    # Confidence Banding
    # --------------------------------------------------
    def get_confidence_band(self, score: float) -> str:
        if score >= 0.75:
            return "HIGH"
        elif score >= 0.60:
            return "MEDIUM"
        elif score >= self.oos_threshold:
            return "LOW"
        else:
            return "OOS"

    # --------------------------------------------------
    # Main Classification Logic
    # --------------------------------------------------
    def classify(self, text: str):

        if not text or not text.strip():
            return None, 0.0, "OOS", []

        # -------- SEMANTIC SCORING (RAW COSINE) --------
        semantic_scores = {}

        text_embedding = self.semantic_registry.model.encode(
            text,
            convert_to_tensor=True
        )

        for intent, embeddings in self.semantic_registry.intent_embeddings.items():
            similarities = util.cos_sim(text_embedding, embeddings)
            semantic_scores[intent] = torch.max(similarities).item()

        # Raw top intent
        raw_top_intent = max(semantic_scores, key=semantic_scores.get)
        raw_top_score = semantic_scores[raw_top_intent]

        # -------- OUT OF SCOPE CHECK --------
        if raw_top_score < self.oos_threshold:
            return None, raw_top_score, "OOS", []

        # -------- BM25 SCORING --------
        bm25_scores = self.bm25.score(text)

        # -------- NORMALIZATION (FOR FUSION ONLY) --------
        semantic_scores_norm = self.normalize(semantic_scores)
        bm25_scores_norm = self.normalize(bm25_scores)

        # -------- FUSION --------
        fused_scores = {}

        for intent in semantic_scores_norm.keys():
            fused_scores[intent] = (
                self.embedding_weight * semantic_scores_norm.get(intent, 0)
                + self.bm25_weight * bm25_scores_norm.get(intent, 0)
            )

        sorted_scores = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_intent, top_fused_score = sorted_scores[0]

        # -------- AMBIGUITY DETECTION --------
        if len(sorted_scores) > 1:
            second_score = sorted_scores[1][1]

            # If fusion scores are too close → ambiguous
            if abs(top_fused_score - second_score) < 0.05:
                return None, raw_top_score, "AMBIGUOUS", [
                    sorted_scores[0][0],
                    sorted_scores[1][0]
                ]

        # -------- CONFIDENCE BAND --------
        confidence_band = self.get_confidence_band(raw_top_score)

        return top_intent, raw_top_score, confidence_band, []

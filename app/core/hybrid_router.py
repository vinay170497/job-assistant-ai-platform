from app.core.intent_registry import IntentRegistry
from app.core.bm25_index import BM25Index
from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
from app.core.telemetry import RoutingTelemetry

class HybridRouter:

    def __init__(self):

        # -------- Intent Registry --------
        self.registry = IntentRegistry()
        self.telemetry = RoutingTelemetry()

        # -------- Embedding Model --------
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # -------- Build Enriched Intent Documents --------
        self.intent_documents = {}
        self.intent_embeddings = {}

        self._build_intent_representations()

        # -------- BM25 Index (unchanged logic) --------
        self.bm25 = BM25Index(self.intent_documents)

        # -------- Fusion Weights --------
        self.embedding_weight = 0.65
        self.bm25_weight = 0.50

        # -------- Decision Thresholds --------
        self.oos_threshold = 0.3
        self.high_threshold = 0.7
        self.medium_threshold = 0.55

    # --------------------------------------------------
    # Build Semantic Representations
    # --------------------------------------------------
    def _build_intent_representations(self):
        """
        Create enriched text per intent:
        description + examples
        Then compute embedding once.
        """

        for intent_name in self.registry.get_all_intent_names():

            description = self.registry.get_description(intent_name)
            examples = self.registry.get_examples(intent_name)

            enriched_text = description + " " + " ".join(examples)

            self.intent_documents[intent_name] = enriched_text

            embedding = self.model.encode(
                enriched_text,
                convert_to_tensor=True
            )

            self.intent_embeddings[intent_name] = embedding

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
        if score >= self.high_threshold:
            return "HIGH"
        elif score >= self.medium_threshold:
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

        text_embedding = self.model.encode(
            text,
            convert_to_tensor=True
        )

        for intent, embedding in self.intent_embeddings.items():
            similarity = util.cos_sim(text_embedding, embedding).item()
            semantic_scores[intent] = similarity

        raw_top_intent = max(semantic_scores, key=semantic_scores.get)
        raw_top_score = semantic_scores[raw_top_intent]

        # -------- OUT OF SCOPE CHECK --------
        if raw_top_score < self.oos_threshold:
            self.telemetry.log({
                "input": text,
                "top_intent": raw_top_intent,
                "raw_score": raw_top_score,
                "confidence_band": "OOS",
                "decision": "OUT_OF_SCOPE"
            })
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

            # Only mark ambiguous if TWO DISTINCT INTENTS are close
            if (
                abs(top_fused_score - second_score) < 0.015
                and sorted_scores[0][0] != sorted_scores[1][0]
            ):
                self.telemetry.log({
                    "input": text,
                    "top_intent": sorted_scores[0][0],
                    "second_intent": sorted_scores[1][0],
                    "fusion_gap": abs(top_fused_score - second_score),
                    "raw_score": raw_top_score,
                    "decision": "AMBIGUOUS"
                })
                return None, raw_top_score, "AMBIGUOUS", [
                    sorted_scores[0][0],
                    sorted_scores[1][0]
                ]

        # -------- CONFIDENCE BAND --------
        confidence_band = self.get_confidence_band(raw_top_score)

        # -------- TELEMETRY LOG --------
        self.telemetry.log({
            "input": text,
            "top_intent": top_intent,
            "raw_score": raw_top_score,
            "confidence_band": confidence_band,
            "fusion_score": top_fused_score,
            "all_semantic_scores": semantic_scores,
            "all_fused_scores": fused_scores,
            "decision": "RESOLVED"
        })

        return top_intent, raw_top_score, confidence_band, []
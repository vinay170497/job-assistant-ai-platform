from sentence_transformers import CrossEncoder
from app.core.intent_registry import IntentRegistry


class CrossEncoderArbitrator:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
        self.registry = IntentRegistry()
        self.arbitration_threshold = 0.55  # Slightly stricter

    def arbitrate(self, query: str, candidate_intents: list):

        if not candidate_intents:
            return None, 0.0

        pairs = []

        for intent in candidate_intents:
            description = self.registry.get_description(intent)
            pairs.append((query, description))

        scores = self.model.predict(pairs)

        best_index = scores.argmax()
        best_score = float(scores[best_index])
        best_intent = candidate_intents[best_index]

        # Reject weak matches
        if best_score < self.arbitration_threshold:
            return None, best_score

        return best_intent, best_score
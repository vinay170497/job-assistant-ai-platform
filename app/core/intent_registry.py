from sentence_transformers import SentenceTransformer, util
import torch


class IntentRegistry:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.intent_definitions = {
            "job_search": [
                "find jobs",
                "python developer openings",
                "current job vacancies",
                "hiring in data science",
                "software engineer roles",
                "job opportunities near me",
                "backend developer job",
                "IT company hiring",
                "search for employment",
                "open positions in tech"
            ],
            "resume_help": [
                "improve my resume",
                "resume review",
                "CV writing help",
                "optimize my CV",
                "resume formatting advice",
                "how to write resume",
                "resume feedback"
            ],
            "knowledge_query": [
                "how does machine learning work",
                "explain neural networks",
                "what is data science",
                "describe artificial intelligence",
                "how to learn python",
                "tell me about deep learning"
            ]
        }

        self.intent_embeddings = self._encode_intents()

    def _encode_intents(self):
        encoded = {}
        for intent, phrases in self.intent_definitions.items():
            embeddings = self.model.encode(phrases, convert_to_tensor=True)
            encoded[intent] = embeddings
        return encoded

    def classify(self, text: str):
        text_embedding = self.model.encode(text, convert_to_tensor=True)

        scores = {}

        for intent, embeddings in self.intent_embeddings.items():
            similarities = util.cos_sim(text_embedding, embeddings)
            max_score = torch.max(similarities).item()
            scores[intent] = max_score

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        top_intent, top_score = sorted_scores[0]

        # Disambiguation if very close
        if len(sorted_scores) > 1:
            second_score = sorted_scores[1][1]
            if abs(top_score - second_score) < 0.015:
                return None, 0.0, [i[0] for i in sorted_scores[:2]]

        if top_score < 0.55:
            return None, top_score, []

        return top_intent, top_score, []

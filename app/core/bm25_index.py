from rank_bm25 import BM25Okapi


class BM25Index:

    def __init__(self, intent_definitions: dict):
        """
        intent_definitions:
        {
            "intent_name": [list of prototype phrases]
        }
        """
        self.intent_labels = []
        self.corpus = []

        for intent, phrases in intent_definitions.items():
            for phrase in phrases:
                self.intent_labels.append(intent)
                self.corpus.append(phrase.lower().split())

        self.bm25 = BM25Okapi(self.corpus)

    def score(self, query: str):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        intent_scores = {}

        for idx, score in enumerate(scores):
            intent = self.intent_labels[idx]
            intent_scores[intent] = max(
                score,
                intent_scores.get(intent, float("-inf"))
            )

        return intent_scores

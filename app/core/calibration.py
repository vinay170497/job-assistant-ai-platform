import json
from pathlib import Path
import numpy as np


class ConfidenceCalibrationAnalyzer:

    def __init__(self, log_path="logs/routing_logs.jsonl"):
        self.log_path = Path(log_path)

    def load_logs(self):

        if not self.log_path.exists():
            return []

        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))

        return records

    def analyze(self):

        records = self.load_logs()

        if not records:
            print("No logs available for analysis.")
            return

        raw_scores = [
            r["raw_score"]
            for r in records
            if "raw_score" in r
        ]

        if not raw_scores:
            print("No raw_score values found.")
            return

        raw_scores = np.array(raw_scores)

        print("\n--- Confidence Distribution ---")
        print(f"Total samples: {len(raw_scores)}")
        print(f"Mean score: {raw_scores.mean():.4f}")
        print(f"Std deviation: {raw_scores.std():.4f}")
        print(f"Min score: {raw_scores.min():.4f}")
        print(f"Max score: {raw_scores.max():.4f}")

        print("\nSuggested Threshold Insights:")
        print(f"25th percentile: {np.percentile(raw_scores, 25):.4f}")
        print(f"50th percentile (median): {np.percentile(raw_scores, 50):.4f}")
        print(f"75th percentile: {np.percentile(raw_scores, 75):.4f}")

        print("\nRecommendation:")
        print("- Set OOS threshold slightly below 25th percentile of correct cases.")
        print("- Set HIGH confidence near 75th percentile.")
import yaml
from pathlib import Path


class IntentRegistry:

    def __init__(self, config_path: str = "app/config/intents.yaml"):
        self.config_path = Path(config_path)
        self.intent_definitions = self._load_intents()

    # --------------------------------------------------
    # Load YAML
    # --------------------------------------------------
    def _load_intents(self):

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        intents = {}

        for intent in data.get("intents", []):
            intents[intent["name"]] = {
                "description": intent.get("description", ""),
                "examples": intent.get("examples", [])
            }

        return intents

    # --------------------------------------------------
    # Public API (USED BY ROUTER)
    # --------------------------------------------------
    def get_all_intent_names(self):
        return list(self.intent_definitions.keys())

    def get_description(self, intent_name: str):
        return self.intent_definitions[intent_name]["description"]

    def get_examples(self, intent_name: str):
        return self.intent_definitions[intent_name]["examples"]

    def get_intent_document(self, intent_name: str):
        """
        Returns enriched text used for embedding
        """
        data = self.intent_definitions[intent_name]
        return data["description"] + " " + " ".join(data["examples"])
# import pandas as pd

# def load_and_prepare_data(path):
#     df = pd.read_csv(path)

#     df["full_text"] = (
#         df["title"].fillna("") + " " +
#         df["description"].fillna("") + " " +
#         df["qualifications"].fillna("") + " " +
#         df["job_highlights"].fillna("")
#     )

#     df["full_text"] = df["full_text"].str.strip().str.lower()

#     return df
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler


# ---------------------------------------------------
# 1️⃣ Load & Prepare Data
# ---------------------------------------------------

def load_and_prepare_data(path):
    df = pd.read_csv(path)

    df["full_text"] = (
        df["title"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["qualifications"].fillna("") + " " +
        df["job_highlights"].fillna("")
    )

    df["full_text"] = df["full_text"].str.strip().str.lower()
    df["title"] = df["title"].fillna("").str.lower()

    return df


# ---------------------------------------------------
# 2️⃣ Skill Extraction with EntityRuler
# ---------------------------------------------------

class SkillExtractor:

    def __init__(self, skills_dict):
        """
        skills_dict example:
        {
            "python": 3,
            "machine learning": 3,
            "sql": 2
        }
        """

        self.skills_dict = skills_dict

        self.nlp = spacy.load("fr_core_news_sm")

        # Add EntityRuler before NER
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")

        patterns = []

        for skill in skills_dict.keys():
            pattern = {
                "label": "SKILL",
                "pattern": [{"LOWER": token} for token in skill.lower().split()]
            }
            patterns.append(pattern)

        ruler.add_patterns(patterns)

    def extract(self, text):
        """
        Returns:
        {
            "python": 2,
            "sql": 1
        }
        """

        doc = self.nlp(text)
        extracted = {}

        for ent in doc.ents:
            if ent.label_ == "SKILL":
                skill = ent.text.lower()
                extracted[skill] = extracted.get(skill, 0) + 1

        return extracted

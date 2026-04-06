# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity

# model = SentenceTransformer("all-MiniLM-L6-v2")

# def compute_semantic_scores(df, cv_text):
    
#     cv_embedding = model.encode([cv_text])
#     job_embeddings = model.encode(df["full_text"].tolist())
    
#     similarities = cosine_similarity(cv_embedding, job_embeddings)[0]
    
#     return similarities

# def pre_filter(row, required_source="indeed"):
    
#     if required_source not in str(row["source"]).lower():
#         return 0
    
#     return 1
# def skill_priority_score(text, skill_weights):
    
#     total_weight = sum(skill_weights.values())
#     score = 0
    
#     for skill, weight in skill_weights.items():
#         if skill in text:
#             score += weight
    
#     return score / total_weight
# def compute_final_score(row):
#     return (
#         0.4 * row["skill_score"] +
#         0.6 * row["semantic_score"]
#     )
# import re
# from sentence_transformers import SentenceTransformer, CrossEncoder
# from sklearn.metrics.pairwise import cosine_similarity

# def pre_filter(row, required_source="indeed"):
#     if required_source not in str(row["source"]).lower():
#         return 0
#     return 1
# class JobScorer:

#     def __init__(self, cv_skills, bi_encoder_model="sentence-transformers/all-MiniLM-L6-v2",
#                 cross_encoder_model="cross-encoder/ms-marco-MiniLM-L-6-v2"):

#         self.cv_skills = cv_skills

#         print("🔹 Loading Bi-Encoder model...")
#         self.bi_encoder = SentenceTransformer(bi_encoder_model)

#         print("🔹 Loading Cross-Encoder model...")
#         self.cross_encoder = CrossEncoder(cross_encoder_model)

#         self.cv_text = " ".join(cv_skills.keys())
#         self.cv_embedding = self.bi_encoder.encode(self.cv_text, convert_to_tensor=True)

#     # ---------------------------------------------------
#     # 1️⃣ Regex Skill Matching
#     # ---------------------------------------------------

#     def skill_match(self, skill, text):
#         pattern = r"\b" + re.escape(skill) + r"\b"
#         return re.search(pattern, text, re.IGNORECASE) is not None

#     def compute_skill_score(self, job_text):

#         score = 0
#         max_possible = sum(self.cv_skills.values())

#         for skill, weight in self.cv_skills.items():
#             if self.skill_match(skill, job_text):
#                 score += weight

#         if max_possible == 0:
#             return 0

#         return score / max_possible  # normalized 0–1

#     # ---------------------------------------------------
#     # 2️⃣ Semantic Retrieval (Bi-Encoder)
#     # ---------------------------------------------------

#     def compute_semantic_score(self, job_text):

#         job_embedding = self.bi_encoder.encode(job_text, convert_to_tensor=True)

#         cosine_score = cosine_similarity(
#             self.cv_embedding.cpu().reshape(1, -1),
#             job_embedding.cpu().reshape(1, -1)
#         )[0][0]

#         return float(cosine_score)

#     # ---------------------------------------------------
#     # 3️⃣ Cross Encoder Re-ranking
#     # ---------------------------------------------------

#     def compute_cross_score(self, job_text):

#         pair = [[self.cv_text, job_text]]
#         score = self.cross_encoder.predict(pair)[0]

#         return float(score)

#     # ---------------------------------------------------
#     # 4️⃣ Full Ranking Pipeline
#     # ---------------------------------------------------

#     def rank_jobs(self, jobs_df, top_k=20):

#         print("🔹 Computing skill scores...")
#         jobs_df["skill_score"] = jobs_df["full_text"].apply(self.compute_skill_score)

#         print("🔹 Computing semantic scores...")
#         jobs_df["semantic_score"] = jobs_df["full_text"].apply(self.compute_semantic_score)

#         # First stage ranking (retrieval)
#         jobs_df = jobs_df.sort_values(
#             by=["semantic_score", "skill_score"],
#             ascending=False
#         )

#         top_jobs = jobs_df.head(top_k).copy()

#         print("🔹 Cross-encoder reranking...")
#         top_jobs["cross_score"] = top_jobs["full_text"].apply(self.compute_cross_score)

#         # Normalize cross score
#         min_cross = top_jobs["cross_score"].min()
#         max_cross = top_jobs["cross_score"].max()

#         if max_cross - min_cross != 0:
#             top_jobs["cross_score"] = (
#                 (top_jobs["cross_score"] - min_cross) /
#                 (max_cross - min_cross)
#             )
#         else:
#             top_jobs["cross_score"] = 0

#         # Final score combination
#         top_jobs["final_score"] = (
#             0.4 * top_jobs["skill_score"] +
#             0.3 * top_jobs["semantic_score"] +
#             0.3 * top_jobs["cross_score"]
#         )

#         top_jobs = top_jobs.sort_values(by="final_score", ascending=False)

#         return top_jobs
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import SkillExtractor


# ---------------------------------------------------
# Optional Pre-filter
# ---------------------------------------------------

def pre_filter(row, required_source="indeed"):
    if required_source not in str(row["source"]).lower():
        return 0
    return 1


# ---------------------------------------------------
# Job Scorer
# ---------------------------------------------------

class JobScorer:

    def __init__(
        self,
        cv_skills,
        bi_encoder_model="sentence-transformers/all-MiniLM-L6-v2",
        cross_encoder_model="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.cv_skills = cv_skills

        # Skill extractor
        self.skill_extractor = SkillExtractor(cv_skills)

        print("🔹 Loading Bi-Encoder model...")
        self.bi_encoder = SentenceTransformer(bi_encoder_model)

        print("🔹 Loading Cross-Encoder model...")
        self.cross_encoder = CrossEncoder(cross_encoder_model)

        # Represent Olive Soft skill base as text
        self.cv_text = " ".join(cv_skills.keys())
        self.cv_embedding = self.bi_encoder.encode(
            self.cv_text,
            convert_to_tensor=True
        )

    # ---------------------------------------------------
    # 1️⃣ Structured Feature Engineering Layer
    # ---------------------------------------------------

    def compute_structured_features(self, job_text, job_title=""):

        extracted_skills = self.skill_extractor.extract(job_text)

        total_weight = sum(self.cv_skills.values())
        weighted_match = 0
        frequency_score = 0
        title_boost = 0

        for skill, weight in self.cv_skills.items():

            if skill in extracted_skills:

                # Weighted coverage
                weighted_match += weight

                # Frequency importance
                frequency_score += weight * extracted_skills[skill]

                # Title strategic boost
                if skill in job_title:
                    title_boost += weight * 0.5

        # Normalized coverage
        coverage = weighted_match / total_weight if total_weight != 0 else 0

        # Frequency normalization (smooth)
        frequency_score = frequency_score / (1 + frequency_score)

        structured_score = (
            0.6 * coverage +
            0.3 * frequency_score +
            0.1 * title_boost
        )

        return structured_score

    # ---------------------------------------------------
    # 2️⃣ Semantic Retrieval (Bi-Encoder)
    # ---------------------------------------------------

    def compute_semantic_score(self, job_text):

        job_embedding = self.bi_encoder.encode(
            job_text,
            convert_to_tensor=True
        )

        cosine_score = cosine_similarity(
            self.cv_embedding.cpu().reshape(1, -1),
            job_embedding.cpu().reshape(1, -1)
        )[0][0]

        return float(cosine_score)

    # ---------------------------------------------------
    # 3️⃣ Cross Encoder Re-ranking
    # ---------------------------------------------------

    def compute_cross_score(self, job_text):

        pair = [[self.cv_text, job_text]]
        score = self.cross_encoder.predict(pair)[0]

        return float(score)

        # ---------------------------------------------------
    # 4️⃣ Full Ranking Pipeline
    # ---------------------------------------------------

    def rank_jobs(self, jobs_df, top_k=20):

        print("🔹 Computing structured skill features...")

        jobs_df["skill_score"] = jobs_df.apply(
            lambda row: self.compute_structured_features(
                row["full_text"],
                row.get("title", "")
            ),
            axis=1
        )

        print("🔹 Computing semantic scores (batch)...")

        # Batch embedding (beaucoup plus rapide)
        job_embeddings = self.bi_encoder.encode(
            jobs_df["full_text"].tolist(),
            convert_to_tensor=True
        )

        cosine_scores = cosine_similarity(
            self.cv_embedding.cpu().reshape(1, -1),
            job_embeddings.cpu()
        )[0]

        jobs_df["semantic_score"] = cosine_scores

        # First-stage ranking
        jobs_df = jobs_df.sort_values(
            by=["semantic_score", "skill_score"],
            ascending=False
        )

        top_jobs = jobs_df.head(top_k).copy()

        print("🔹 Cross-encoder reranking...")

        pairs = [
            [self.cv_text, text]
            for text in top_jobs["full_text"]
        ]

        cross_scores = self.cross_encoder.predict(pairs)
        top_jobs["cross_score"] = cross_scores

        # Normalize cross score
        min_cross = top_jobs["cross_score"].min()
        max_cross = top_jobs["cross_score"].max()

        if max_cross - min_cross != 0:
            top_jobs["cross_score"] = (
                (top_jobs["cross_score"] - min_cross) /
                (max_cross - min_cross)
            )
        else:
            top_jobs["cross_score"] = 0

        # Final Strategic Score
        top_jobs["final_score"] = (
            0.4 * top_jobs["skill_score"] +
            0.3 * top_jobs["semantic_score"] +
            0.3 * top_jobs["cross_score"]
        )

        top_jobs = top_jobs.sort_values(
            by="final_score",
            ascending=False
        )

        return top_jobs


# import pandas as pd

from preprocessing import load_and_prepare_data
from scoring import JobScorer
from scoring import pre_filter   # On garde le prefilter
from config import cv_skills


def main():

    # ==============================
    # 1️⃣ LOAD & PREPROCESS DATA
    # ==============================
    print("🔹 Loading data...")
    df = load_and_prepare_data("job-scrapping - Jobs.csv")

    print(f"Total jobs loaded: {len(df)}")

    # ==============================
    # 2️⃣ PRE-SCORING (ELIMINATION)
    # ==============================
    print("🔹 Applying elimination criteria...")

    df["pre_score"] = df.apply(pre_filter, axis=1)
    df_filtered = df[df["pre_score"] == 1].copy()

    print(f"Jobs after pre-filtering: {len(df_filtered)}")

    if df_filtered.empty:
        print("❌ No jobs passed elimination criteria.")
        return

    # ==============================
    # 3️⃣ RANKING PIPELINE (NEW SYSTEM)
    # ==============================
    print("🔹 Initializing scoring engine...")

    scorer = JobScorer(cv_skills)

    print("🔹 Running ranking pipeline (Skill + Semantic + Cross-Encoder)...")

    df_ranked = scorer.rank_jobs(df_filtered, top_k=20)

    # ==============================
    # 4️⃣ DISPLAY TOP RESULTS
    # ==============================
    print("\n🏆 TOP 10 RECOMMENDED JOBS\n")

    top_jobs = df_ranked.head(10)

    for i, row in top_jobs.iterrows():
        print("--------------------------------------------------")
        print(f"Title           : {row['title']}")
        print(f"Company         : {row['company_name']}")
        print(f"Location        : {row['location']}")
        print(f"Skill Score     : {round(row['skill_score'], 4)}")
        print(f"Semantic Score  : {round(row['semantic_score'], 4)}")
        print(f"Cross Score     : {round(row['cross_score'], 4)}")
        print(f"Final Score     : {round(row['final_score'], 4)}")
        print("--------------------------------------------------")

    # ==============================
    # 5️⃣ SAVE OUTPUT FILE
    # ==============================
    df_ranked.to_csv("ranked_jobs_output.csv", index=False)

    print("\n✅ Ranking saved to ranked_jobs_output.csv")


if __name__ == "__main__":
    main()

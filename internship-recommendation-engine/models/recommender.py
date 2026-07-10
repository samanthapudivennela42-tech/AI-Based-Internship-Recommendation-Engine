"""
recommender.py
----------------
Core AI/ML recommendation logic for the Internship Recommendation Engine.

Approach (Content-Based Filtering):
1. Each internship posting is represented as a text "profile" combining
   its required skills, domain, education requirement, and description.
2. Each student is represented the same way, using their skills,
   education, experience level, and preferred domain/interests.
3. Both sets of text profiles are vectorized using TF-IDF.
4. Cosine similarity between the student vector and every internship
   vector produces a relevance score.
5. Internships are ranked by score and filtered/boosted using simple
   rule-based factors (education match, experience level match).
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class InternshipRecommender:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = self._load_data()
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._build_corpus()

    def _load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_path)
        df["required_skills"] = df["required_skills"].fillna("")
        df["description"] = df["description"].fillna("")
        return df

    def _build_corpus(self):
        """Combine relevant internship fields into a single text field
        and fit the TF-IDF vectorizer on the whole internship corpus."""
        self.df["combined_text"] = (
            self.df["required_skills"] + " " +
            self.df["domain"] + " " +
            self.df["min_education"] + " " +
            self.df["description"]
        ).str.lower()

        self.internship_matrix = self.vectorizer.fit_transform(
            self.df["combined_text"]
        )

    def _build_student_profile_text(self, skills, education, experience,
                                     preferred_domain, interests) -> str:
        parts = [
            skills or "",
            education or "",
            experience or "",
            preferred_domain or "",
            interests or "",
        ]
        return " ".join(parts).lower()

    def _education_rank(self, level: str) -> int:
        order = {"any degree": 0, "b.tech": 1, "m.tech": 2}
        return order.get(str(level).strip().lower(), 0)

    def _experience_rank(self, level: str) -> int:
        order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        return order.get(str(level).strip().lower(), 0)

    def recommend(self, skills: str, education: str, experience: str,
                   preferred_domain: str = "", interests: str = "",
                   location: str = "", top_n: int = 5):
        """
        Generate ranked internship recommendations for a student profile.

        Returns a list of dicts, each an internship row plus a
        'match_score' (0-100) field, sorted by relevance.
        """
        student_text = self._build_student_profile_text(
            skills, education, experience, preferred_domain, interests
        )
        student_vector = self.vectorizer.transform([student_text])

        similarity_scores = cosine_similarity(
            student_vector, self.internship_matrix
        ).flatten()

        results = self.df.copy()
        results["similarity"] = similarity_scores

        # Rule-based boosts / penalties on top of the ML similarity score
        student_edu_rank = self._education_rank(education)
        student_exp_rank = self._experience_rank(experience)

        def adjust_score(row):
            score = row["similarity"]

            # Boost if education requirement is met or exceeded
            req_edu_rank = self._education_rank(row["min_education"])
            if student_edu_rank >= req_edu_rank:
                score += 0.05

            # Boost if experience level is an exact match
            req_exp_rank = self._experience_rank(row["experience_level"])
            if student_exp_rank == req_exp_rank:
                score += 0.05
            elif abs(student_exp_rank - req_exp_rank) == 1:
                score += 0.02

            # Boost if domain preference matches
            if preferred_domain and preferred_domain.strip().lower() in row["domain"].lower():
                score += 0.1

            # Boost if location preference matches (Remote always counts)
            if location:
                loc = location.strip().lower()
                if loc in row["location"].lower() or row["location"].lower() == "remote":
                    score += 0.05

            return score

        results["final_score"] = results.apply(adjust_score, axis=1)

        # Normalize final score to a 0-100 "match percentage" for display
        max_score = results["final_score"].max() or 1
        results["match_score"] = (
            (results["final_score"] / max_score) * 100
        ).round(1)

        results = results.sort_values("match_score", ascending=False)
        top_results = results.head(top_n)

        columns = [
            "internship_id", "title", "company", "domain",
            "required_skills", "min_education", "experience_level",
            "location", "duration_months", "description", "match_score",
        ]
        return top_results[columns].to_dict(orient="records")


if __name__ == "__main__":
    # Quick manual test
    engine = InternshipRecommender("data/internships.csv")
    recs = engine.recommend(
        skills="python, machine learning, pandas",
        education="B.Tech",
        experience="Beginner",
        preferred_domain="Data Science",
        interests="AI and analytics",
        location="Remote",
        top_n=5,
    )
    for r in recs:
        print(f"{r['match_score']}% - {r['title']} at {r['company']}")
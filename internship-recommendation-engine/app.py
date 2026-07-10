
import os
from flask import Flask, request, jsonify, render_template
from models.recommender import InternshipRecommender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "internships.csv")

app = Flask(__name__)

# Load the recommendation engine once at startup
recommender = InternshipRecommender(DATA_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/internships", methods=["GET"])
def get_internships():
    return jsonify(recommender.df.drop(columns=["combined_text"]).to_dict(orient="records"))


@app.route("/api/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(silent=True) or {}

    skills = payload.get("skills", "")
    education = payload.get("education", "")
    experience = payload.get("experience", "")
    preferred_domain = payload.get("preferred_domain", "")
    interests = payload.get("interests", "")
    location = payload.get("location", "")
    top_n = int(payload.get("top_n", 5))

    if not skills.strip():
        return jsonify({"error": "Skills field is required."}), 400

    recommendations = recommender.recommend(
        skills=skills,
        education=education,
        experience=experience,
        preferred_domain=preferred_domain,
        interests=interests,
        location=location,
        top_n=top_n,
    )

    return jsonify({"count": len(recommendations), "results": recommendations})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
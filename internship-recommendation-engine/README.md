# AI-Based Internship Recommendation Engine

A smart recommendation system that helps students and job seekers find
internship opportunities matching their skills, education, experience,
and career interests — built using **content-based filtering** with
**TF-IDF vectorization** and **cosine similarity**.

## How It Works

1. Every internship posting (skills required, domain, education level,
   description) is converted into a text profile.
2. The student's profile (skills, education, experience, preferred
   domain, interests) is converted into a text profile the same way.
3. **TF-IDF** turns both sets of text into numeric vectors that reflect
   which terms matter most.
4. **Cosine similarity** measures how close the student's vector is to
   each internship's vector — this is the core ML relevance score.
5. Rule-based boosts fine-tune the ranking: education-level fit,
   experience-level fit, domain preference, and location preference.
6. Results are sorted and returned as a ranked, percentage-scored list.

## Project Structure
document.getElementById("profileForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const payload = {
    skills: document.getElementById("skills").value.trim(),
    education: document.getElementById("education").value,
    experience: document.getElementById("experience").value,
    preferred_domain: document.getElementById("preferred_domain").value.trim(),
    interests: document.getElementById("interests").value.trim(),
    location: document.getElementById("location").value.trim(),
    top_n: 6,
  };

  const resultsContainer = document.getElementById("resultsContainer");
  resultsContainer.innerHTML = "<p class='placeholder'>Finding the best matches for you...</p>";

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      resultsContainer.innerHTML = `<p class="placeholder">${data.error || "Something went wrong."}</p>`;
      return;
    }

    renderResults(data.results);
  } catch (err) {
    resultsContainer.innerHTML = "<p class='placeholder'>Could not reach the server. Please try again.</p>";
    console.error(err);
  }
});

function renderResults(results) {
  const container = document.getElementById("resultsContainer");

  if (!results || results.length === 0) {
    container.innerHTML = "<p class='placeholder'>No matching internships found. Try adjusting your skills or interests.</p>";
    return;
  }

  container.innerHTML = results
    .map((r) => {
      const skillTags = r.required_skills
        .split(",")
        .map((s) => `<span class="tag">${s.trim()}</span>`)
        .join("");

      return `
        <div class="result-item">
          <span class="match-badge">${r.match_score}% match</span>
          <h3>${r.title}</h3>
          <div class="company">${r.company} • ${r.location} • ${r.duration_months} months</div>
          <div class="tags">${skillTags}</div>
          <div class="desc">${r.description}</div>
        </div>
      `;
    })
    .join("");
}
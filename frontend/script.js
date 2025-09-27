// frontend/script.js
const apiBase = (window.API_BASE) ? window.API_BASE : ("/api"); // set by deploy if needed
const analyzeBtn = document.getElementById("analyze");
const textEl = document.getElementById("text");
const resultEl = document.getElementById("result");
const modeEl = document.getElementById("mode");

analyzeBtn.addEventListener("click", async () => {
  resultEl.textContent = "Analyzing...";
  const mode = modeEl.value;
  const text = textEl.value.trim();
  if (!text) {
    resultEl.textContent = "Please enter text.";
    return;
  }
  try {
    let res;
    if (mode === "single") {
      res = await fetch(`${apiBase}/sentiment`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text })
      });
    } else {
      // split lines for batch
      const lines = text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
      res = await fetch(`${apiBase}/sentiment`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ texts: lines })
      });
    }
    const data = await res.json();
    if (!res.ok) {
      resultEl.textContent = `Error: ${data.detail || JSON.stringify(data)}`;
      return;
    }
    // pretty print
    if (Array.isArray(data)) {
      resultEl.innerHTML = data.map((d,i) => `<div><strong>Line ${i+1}:</strong> ${d.label} (${(d.score*100).toFixed(1)}%)</div>`).join("");
    } else {
      resultEl.innerHTML = `<div><strong>${data.label}</strong> — ${(data.score*100).toFixed(1)}%</div>`;
    }
  } catch (err) {
    resultEl.textContent = `Request failed: ${err}`;
  }
});

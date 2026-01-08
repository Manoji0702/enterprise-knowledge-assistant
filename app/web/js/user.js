async function ask() {
  const questionBox = document.getElementById("question");
  const askBtn = document.getElementById("askBtn");
  const status = document.getElementById("status");
  const answerCard = document.getElementById("answerCard");
  const answerEl = document.getElementById("answer");
  const sourcesEl = document.getElementById("sources");

  const question = questionBox.value.trim();
  if (!question) return;

  askBtn.disabled = true;
  status.innerText = "Thinking...";
  answerCard.classList.add("hidden");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await res.json();

    answerEl.innerText = data.answer || "No answer found.";

    if (data.sources && data.sources.length > 0) {
      sourcesEl.innerHTML =
        "<strong>Sources:</strong> " + data.sources.join(", ");
    } else {
      sourcesEl.innerHTML = "";
    }

    answerCard.classList.remove("hidden");
    status.innerText = "";

  } catch (err) {
    status.innerText = "Something went wrong. Please try again.";
  } finally {
    askBtn.disabled = false;
  }
}

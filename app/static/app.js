const $ = (id) => document.getElementById(id);

async function runIntake() {
  const message = $("message").value.trim();
  if (!message) return;
  $("status").textContent = "Processing...";
  $("send").disabled = true;
  try {
    const response = await fetch("/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain: $("domain").value, message })
    });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    $("result").classList.remove("hidden");
    $("reply").textContent = data.reply;
    $("risk").textContent = data.risk_level.toUpperCase();
    $("risk").className = `risk-${data.risk_level}`;
    $("escalation").textContent = data.escalation_required ? "Escalation required" : "Routine intake";
    $("summary").textContent = data.summary;
    $("fields").textContent = JSON.stringify(data.collected_fields, null, 2);
    $("questions").innerHTML = data.next_questions.map(q => `<li>${q}</li>`).join("") || "<li>No more questions needed.</li>";
    $("disclaimer").textContent = data.disclaimer;
    $("status").textContent = data.ai_used ? "AI + rules" : "Rules fallback";
  } catch (error) {
    $("status").textContent = "Error";
    alert("Request failed: " + error.message);
  } finally {
    $("send").disabled = false;
  }
}

$("send").addEventListener("click", runIntake);
$("clear").addEventListener("click", () => {
  $("message").value = "";
  $("result").classList.add("hidden");
  $("status").textContent = "Ready";
});

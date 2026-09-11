const state = {
  mode: 'clinic',
  currentIntakeId: null,
  lastResultText: '',
  listening: false,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const recognitionApi = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = recognitionApi ? new recognitionApi() : null;

const copy = {
  clinic: {
    label: 'Clinic assistant',
    title: 'Patient intake',
    greeting: 'Hello, I am ready to capture the patient intake. Tell me what is happening and I will route it for human review.',
    placeholder: 'Describe symptoms, timeline, medication, allergies, or appointment needs...',
  },
  legal: {
    label: 'Legal assistant',
    title: 'Client intake',
    greeting: 'Hello, I am ready to capture the legal matter. Share the issue, dates, notices, and deadline details.',
    placeholder: 'Describe the matter, deadline, opposing party, documents, or consultation need...',
  },
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  })[char]);
}

function setMode(nextMode) {
  state.mode = nextMode;
  $$('.mode button').forEach((button) => button.classList.toggle('active', button.dataset.mode === nextMode));
  $('#modeLabel').textContent = copy[nextMode].label;
  $('#assistantTitle').textContent = copy[nextMode].title;
  $('#message').placeholder = copy[nextMode].placeholder;
  $('#assistantChat').innerHTML = '';
  addBubble('assistant', copy[nextMode].greeting);
}

function addBubble(type, text) {
  const chat = $('#assistantChat');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${type}`;
  bubble.textContent = text;
  chat.append(bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

function setLoading(isLoading) {
  $('#submitIntake').disabled = isLoading;
  $('#submitIntake').textContent = isLoading ? 'Sending' : 'Send';
}

function formatRiskLabel(result) {
  const risk = String(result.risk || 'low');
  const urgency = String(result.urgency || 'routine').replaceAll('_', ' ');
  return `${risk.toUpperCase()} / ${urgency}`;
}

function assistantReplyFrom(summary) {
  return String(summary || '').split(' | Intake: ')[0].trim() || 'Your intake has been captured for review.';
}

function updateTriage(result) {
  const risk = String(result.risk || 'low');
  $('#priorityCard').className = `card priority-card risk-${risk}`;
  $('#riskValue').textContent = risk === 'critical' ? 'Critical' : risk.charAt(0).toUpperCase() + risk.slice(1);
  $('#riskReason').textContent = `${String(result.category || 'general').replaceAll('_', ' ')} route, ${String(result.urgency || 'routine').replaceAll('_', ' ')} urgency.`;
}

function renderResult(result) {
  const handoff = result.handoff_requested ? 'Human handoff requested' : 'Standard review queue';
  const html = `
    <div class="output-grid">
      <div><span>Case</span><strong>#${escapeHtml(result.id)}</strong></div>
      <div><span>Mode</span><strong>${escapeHtml(result.mode)}</strong></div>
      <div><span>Risk</span><strong>${escapeHtml(formatRiskLabel(result))}</strong></div>
      <div><span>Status</span><strong>${escapeHtml(result.status)}</strong></div>
    </div>
    <p>${escapeHtml(result.summary)}</p>
    <div class="handoff-note">${escapeHtml(handoff)}</div>
  `;
  $('#result').className = 'result-body';
  $('#result').innerHTML = html;
  state.lastResultText = `${formatRiskLabel(result)}\n${result.summary}\n${handoff}`;
}

function syncAppointment(result) {
  $('#aname').value = $('#name').value;
  $('#acontact').value = $('#contact').value;
  $('#notes').value = `Intake #${result.id}: ${result.message}`;
  state.currentIntakeId = result.id;
}

function speak(text) {
  if (!$('#speakToggle').checked || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-IN';
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

async function checkHealth() {
  try {
    const response = await fetch('/health');
    $('#apiStatus').textContent = response.ok ? 'Online' : 'Issue';
  } catch {
    $('#apiStatus').textContent = 'Offline';
  }
  $('#voiceStatus').textContent = recognition ? 'Ready' : 'Text only';
}

async function submitIntake(event) {
  event.preventDefault();
  const payload = {
    mode: state.mode,
    name: $('#name').value.trim(),
    contact: $('#contact').value.trim(),
    message: $('#message').value.trim(),
  };
  if (!payload.name || !payload.contact || !payload.message) return;

  addBubble('user', payload.message);
  const pending = addBubble('assistant', 'Reviewing the intake and checking triage signals...');
  setLoading(true);

  try {
    const response = await fetch('/api/intake', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to submit intake');

    const reply = assistantReplyFrom(data.summary);
    pending.textContent = reply;
    updateTriage(data);
    renderResult(data);
    syncAppointment(data);
    speak(reply);
    $('#message').value = '';
  } catch (error) {
    pending.textContent = error.message;
  } finally {
    setLoading(false);
  }
}

async function submitAppointment(event) {
  event.preventDefault();
  const payload = {
    intake_id: state.currentIntakeId,
    mode: state.mode,
    name: $('#aname').value.trim(),
    contact: $('#acontact').value.trim(),
    preferred_slot: $('#slot').value.trim(),
    notes: $('#notes').value.trim(),
  };
  if (!payload.name || !payload.contact || !payload.preferred_slot) return;

  $('#apptResult').textContent = 'Sending appointment request...';
  try {
    const response = await fetch('/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to submit appointment');
    $('#apptResult').textContent = `Appointment request #${data.id} submitted.`;
  } catch (error) {
    $('#apptResult').textContent = error.message;
  }
}

function setupVoice() {
  if (!recognition) {
    $('#voiceButton').disabled = true;
    return;
  }

  recognition.lang = 'en-IN';
  recognition.interimResults = true;
  recognition.continuous = false;

  recognition.onstart = () => {
    state.listening = true;
    $('#voiceButton').classList.add('recording');
    $('#voiceButton').textContent = 'Stop';
  };

  recognition.onend = () => {
    state.listening = false;
    $('#voiceButton').classList.remove('recording');
    $('#voiceButton').textContent = 'Mic';
  };

  recognition.onresult = (event) => {
    let transcript = '';
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      transcript += event.results[index][0].transcript;
    }
    $('#message').value = transcript.trim();
  };

  $('#voiceButton').addEventListener('click', () => {
    if (state.listening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });
}

function setupExamples() {
  $$('.example-row button').forEach((button) => {
    button.addEventListener('click', () => {
      $('#message').value = button.dataset.example;
      $('#message').focus();
    });
  });
}

function setupCopy() {
  $('#copyResult').addEventListener('click', async () => {
    if (!state.lastResultText) return;
    await navigator.clipboard.writeText(state.lastResultText);
    $('#copyResult').textContent = 'Copied';
    window.setTimeout(() => { $('#copyResult').textContent = 'Copy'; }, 1400);
  });
}

$$('.mode button').forEach((button) => button.addEventListener('click', () => setMode(button.dataset.mode)));
$('#intake').addEventListener('submit', submitIntake);
$('#appointment').addEventListener('submit', submitAppointment);
setupVoice();
setupExamples();
setupCopy();
setMode('clinic');
checkHealth();

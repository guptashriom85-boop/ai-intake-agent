let token = '';

const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#039;',
})[char]);

function statCard(label, value) {
  return `<div class="stat"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function renderStats(stats) {
  $('#stats').innerHTML = [
    statCard('Intakes', stats.intakes),
    statCard('Urgent', stats.urgent_intakes),
    statCard('Handoffs', stats.handoffs),
    statCard('Appointments', stats.appointments),
  ].join('');
}

function renderIntakes(intakes) {
  $('#intakes').innerHTML = intakes.length
    ? intakes.map((item) => `
      <article class="record">
        <strong>#${escapeHtml(item.id)} ${escapeHtml(item.name)} - ${escapeHtml(item.risk)} / ${escapeHtml(item.urgency)}</strong>
        <p>${escapeHtml(item.summary)}</p>
        <small>${escapeHtml(item.mode)} | ${escapeHtml(item.contact)} | ${escapeHtml(item.status)} | handoff ${item.handoff_requested ? 'yes' : 'no'}</small>
      </article>
    `).join('')
    : '<p class="muted">No intakes yet.</p>';
}

function renderAppointments(appointments) {
  $('#appointments').innerHTML = appointments.length
    ? appointments.map((item) => `
      <article class="record">
        <strong>#${escapeHtml(item.id)} ${escapeHtml(item.name)} - ${escapeHtml(item.preferred_slot)}</strong>
        <p>${escapeHtml(item.notes || 'No notes')}</p>
        <small>${escapeHtml(item.mode)} | ${escapeHtml(item.contact)} | ${escapeHtml(item.status)}</small>
      </article>
    `).join('')
    : '<p class="muted">No appointments yet.</p>';
}

async function api(path) {
  const response = await fetch(path, { headers: { Authorization: `Bearer ${token}` } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

async function loadDashboard() {
  $('#refresh').disabled = true;
  try {
    const [stats, intakes, appointments] = await Promise.all([
      api('/api/admin/stats'),
      api('/api/admin/intakes'),
      api('/api/admin/appointments'),
    ]);
    renderStats(stats);
    renderIntakes(intakes);
    renderAppointments(appointments);
    $('#loginResult').textContent = 'Signed in.';
  } catch (error) {
    $('#loginResult').textContent = error.message;
  } finally {
    $('#refresh').disabled = false;
  }
}

$('#login').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('#loginResult').textContent = 'Signing in...';
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: $('#email').value, password: $('#password').value }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Login failed');
    token = data.access_token;
    $('#dashboard').hidden = false;
    await loadDashboard();
  } catch (error) {
    $('#loginResult').textContent = error.message;
  }
});

$('#refresh').addEventListener('click', loadDashboard);

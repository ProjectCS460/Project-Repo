// ── Config ──────────────────────────────────────────────
const CLIENT_URL = "http://localhost:8001";

// ── State ───────────────────────────────────────────────
const state = {
  userId: null,
  recordsVisible: false,
};

// ── DOM refs ────────────────────────────────────────────
const loginSection    = () => document.getElementById("login-section");
const mainSection     = () => document.getElementById("main-section");
const recordsSection  = () => document.getElementById("records-section");
const cardContainer   = () => document.getElementById("card-container");
const loginStatus     = () => document.getElementById("login-status");
const formStatus      = () => document.getElementById("form-status");
const submitBtn       = () => document.getElementById("submit-btn");
const recordsBtn      = () => document.getElementById("records-btn");
const recordCount     = () => document.getElementById("record-count");

// ── Utilities ───────────────────────────────────────────
function setStatus(el, msg, type = "error") {
  el.textContent = msg;
  el.className = `status-msg ${type}`;
}

function clearStatus(el) {
  el.textContent = "";
  el.className = "status-msg hidden";
}

function showSection(section) {
  section.classList.remove("hidden");
  section.classList.add("fade-in");
}

function hideSection(section) {
  section.classList.add("hidden");
  section.classList.remove("fade-in");
}

// ── Login ────────────────────────────────────────────────
async function handleLogin() {
  const id       = document.getElementById("login-id").value.trim();
  const password = document.getElementById("login-password").value;
  const btn      = document.getElementById("login-btn");

  if (!id || !password) {
    setStatus(loginStatus(), "ID and password are required.", "error");
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Authenticating...';
  clearStatus(loginStatus());

  try {
    const res = await fetch(`${CLIENT_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: id, password }),
    });

    const data = await res.json();

    if (res.ok && data.success) {
      state.userId = id;
      hideSection(loginSection());
      showSection(mainSection());
    } else {
      setStatus(loginStatus(), data.message || "Authentication failed.", "error");
    }
  } catch (err) {
    setStatus(loginStatus(), "Cannot reach client server.", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Authenticate";
  }
}

// ── Submit Form ──────────────────────────────────────────
async function handleSubmit() {
  const email     = document.getElementById("field-email").value.trim();
  const text      = document.getElementById("field-text").value.trim();
  const longText  = document.getElementById("field-longtext").value.trim();

  if (!email || !text || !longText) {
    setStatus(formStatus(), "All fields are required.", "error");
    return;
  }

  submitBtn().disabled = true;
  submitBtn().innerHTML = '<span class="spinner"></span>Sending...';
  clearStatus(formStatus());

  try {
    const res = await fetch(`${CLIENT_URL}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id:   state.userId,
        email,
        text,
        long_text: longText,
      }),
    });

    const data = await res.json();

    if (res.ok && data.success) {
      setStatus(formStatus(), "Submitted successfully.", "success");
      document.getElementById("field-email").value    = "";
      document.getElementById("field-text").value     = "";
      document.getElementById("field-longtext").value = "";
      // refresh records if visible
      if (state.recordsVisible) loadRecords();
    } else {
      setStatus(formStatus(), data.message || "Submission failed.", "error");
    }
  } catch (err) {
    setStatus(formStatus(), "Cannot reach client server.", "error");
  } finally {
    submitBtn().disabled = false;
    submitBtn().textContent = "Submit";
  }
}

// ── Load Records ─────────────────────────────────────────
async function toggleRecords() {
  if (state.recordsVisible) {
    hideSection(recordsSection());
    state.recordsVisible = false;
    recordsBtn().textContent = "View My Previous Submissions";
    return;
  }

  await loadRecords();
}

async function loadRecords() {
  showSection(recordsSection());
  state.recordsVisible = true;
  recordsBtn().textContent = "Hide Submissions";
  cardContainer().innerHTML = '<div class="empty-state"><span class="spinner"></span> Loading records...</div>';

  try {
    const res = await fetch(`${CLIENT_URL}/records?user_id=${encodeURIComponent(state.userId)}`);
    const data = await res.json();

    if (!res.ok) throw new Error(data.message || "Failed to load.");

    renderCards(data.records || []);
  } catch (err) {
    cardContainer().innerHTML = `<div class="empty-state">Error: ${err.message}</div>`;
  }
}

// ── Render Cards ─────────────────────────────────────────
function renderCards(records) {
  if (records.length === 0) {
    cardContainer().innerHTML = '<div class="empty-state">No submissions found.</div>';
    recordCount().textContent = "";
    return;
  }

  recordCount().textContent = `${records.length} record${records.length !== 1 ? "s" : ""}`;

  cardContainer().innerHTML = records.map((r, i) => `
    <div class="card" style="animation-delay:${i * 40}ms">
      <div class="card-meta">
        <span>#${String(i + 1).padStart(3, "0")}</span>
        <span>${r.submitted_at || "Unknown date"}</span>
      </div>
      <div class="card-email">${escapeHtml(r.email)}</div>
      <div class="card-text">${escapeHtml(r.text)}</div>
      <div class="card-long-text">${escapeHtml(r.long_text)}</div>
    </div>
  `).join("");
}

// ── Helpers ──────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Enter key on login ───────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  ["login-id", "login-password"].forEach(id => {
    document.getElementById(id)?.addEventListener("keydown", e => {
      if (e.key === "Enter") handleLogin();
    });
  });
});

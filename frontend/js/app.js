const API_BASE = "";
let currentSessionId = "sess_" + Math.random().toString(36).substring(2, 9);
let currentCustomer = "Alex Rivera";

// View Navigation Logic
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-item-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      navBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".view-body").forEach(v => v.classList.remove("active"));

      btn.classList.add("active");
      const targetView = btn.getAttribute("data-view");
      const viewEl = document.getElementById(targetView);
      if (viewEl) viewEl.classList.add("active");

      // Update top header title
      const titleMap = {
        "view-chat": "Chatbot for Customer Service — Live Support Widget",
        "view-analytics": "Chatbot for Customer Service — Analytics & KPI Hub",
        "view-escalations": "Chatbot for Customer Service — Live Agent Handoff Queue",
        "view-knowledge": "Chatbot for Customer Service — Knowledge Base Studio",
        "view-settings": "Chatbot for Customer Service — ML Model Architecture"
      };
      const headerTitle = document.getElementById("view-title-header");
      if (headerTitle && titleMap[targetView]) {
        headerTitle.textContent = titleMap[targetView];
      }

      // Fetch view data
      if (targetView === "view-analytics" || targetView === "view-escalations") {
        fetchAnalytics();
      } else if (targetView === "view-knowledge") {
        fetchKnowledge();
      } else if (targetView === "view-settings") {
        fetchModelInfo();
      }
    });
  });
}

// Chat Functionality
async function submitMessage(customText) {
  const inputEl = document.getElementById("user-input-box");
  const query = customText || (inputEl ? inputEl.value.trim() : "");
  if (!query) return;

  if (inputEl) inputEl.value = "";

  appendUserBubble(query);
  const typingId = showTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: query,
        session_id: currentSessionId,
        customer_name: currentCustomer
      })
    });

    removeTypingIndicator(typingId);

    if (res.ok) {
      const data = await res.json();
      renderBotResponse(data);
    } else {
      throw new Error(`Server returned ${res.status}`);
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    console.warn("API fallback:", err);
    runClientFallback(query);
  }
}

function runClientFallback(query) {
  const normalized = query.toLowerCase();
  const order_ids = normalized.match(/#?(?:ord|order)?-?\d{4,6}\b/gi) || [];

  let title = "General Inquiry";
  let reply = "Hello! I am your AI Customer Support Assistant. How can I assist you today?";
  let actions = ["Track Order #ORD-8421", "Refund Policy", "Talk to Agent"];

  if (normalized.includes("track") || normalized.includes("order") || normalized.includes("where") || order_ids.length > 0) {
    title = "Order Tracking & Status";
    reply = "All orders are processed and shipped within 24–48 hours. Provide your order number (e.g., #ORD-8421) to check live transit status.";
    actions = ["Track #ORD-8421", "Change Delivery Address", "Carrier Info"];
  } else if (normalized.includes("refund") || normalized.includes("return") || normalized.includes("money") || normalized.includes("damaged")) {
    title = "Refunds & Return Policy";
    reply = "Our policy allows 30 days for returns on eligible items. Once received, refunds are processed back to your original payment method in 3–5 business days.";
    actions = ["Start Return Request", "Download Return Label", "Refund Status"];
  } else if (normalized.includes("ship") || normalized.includes("cost") || normalized.includes("express")) {
    title = "Shipping Rates & Delivery";
    reply = "We offer Free Standard Shipping on orders over $50 (3–5 business days). Express shipping is $9.99.";
    actions = ["View Shipping Rates", "International Delivery FAQ"];
  } else if (normalized.includes("human") || normalized.includes("agent") || normalized.includes("person")) {
    title = "Live Agent Transfer";
    reply = "Transferring you to a live customer service specialist now. Current wait time is under 2 minutes.";
    actions = ["Wait in Queue", "Request Callback"];
  }

  if (order_ids.length > 0) {
    reply = `I detected your order reference **${order_ids[0].toUpperCase()}**! ` + reply;
  }

  renderBotResponse({
    reply,
    intent: title.toLowerCase().replace(/ /g, "_"),
    confidence: 0.92,
    suggested_actions: actions,
    response_time_ms: 3.8
  });
}

function appendUserBubble(text) {
  const container = document.getElementById("chat-messages-box");
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
  const container = document.getElementById("chat-messages-box");
  const id = "typing-" + Date.now();
  const row = document.createElement("div");
  row.id = id;
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="agent-avatar" style="width:32px; height:32px; background:linear-gradient(135deg, #3b82f6, #06b6d4)">AI</div>
    <div class="msg-bubble" style="color:var(--text-muted);">Finding best response...</div>
  `;
  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function renderBotResponse(data) {
  const container = document.getElementById("chat-messages-box");
  const row = document.createElement("div");
  row.className = "msg-row bot";

  let actionsHtml = "";
  if (data.suggested_actions && data.suggested_actions.length > 0) {
    actionsHtml = `
      <div class="action-pill-group">
        ${data.suggested_actions.map(act => `
          <button class="action-pill-btn" onclick="submitMessage('${escapeHtml(act)}')">${escapeHtml(act)}</button>
        `).join("")}
      </div>
    `;
  }

  const confPct = Math.round((data.confidence || 0.88) * 100);

  row.innerHTML = `
    <div class="agent-avatar" style="width:32px; height:32px; background:linear-gradient(135deg, #3b82f6, #06b6d4)">AI</div>
    <div class="msg-bubble">
      <div>${formatMarkdown(data.reply)}</div>
      ${actionsHtml}
      <div class="msg-meta-tag">
        🎯 ${escapeHtml(data.intent || "general")} (${confPct}%) • ⚡ ${data.response_time_ms || 3.8}ms
      </div>
    </div>
  `;

  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

// Analytics View Fetcher
async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/analytics`);
    if (!res.ok) return;
    const data = await res.json();

    const qEl = document.getElementById("kpi-total-queries");
    const rEl = document.getElementById("kpi-resolution-rate");
    const lEl = document.getElementById("kpi-latency");
    const eEl = document.getElementById("kpi-escalations");

    if (qEl) qEl.textContent = data.total_queries;
    if (rEl) rEl.textContent = `${data.resolution_rate_pct}%`;
    if (lEl) lEl.textContent = `${data.avg_latency_ms}ms`;
    if (eEl) eEl.textContent = data.escalated_count;

    // Render Intent Bars
    const listEl = document.getElementById("analytics-intents-list");
    if (listEl && data.top_intents) {
      const maxHits = Math.max(...data.top_intents.map(i => i.count), 1);
      listEl.innerHTML = data.top_intents.map(item => {
        const pct = Math.round((item.count / maxHits) * 100);
        return `
          <div class="bar-progress-row">
            <div class="bar-progress-label">
              <span><code>${escapeHtml(item.intent)}</code></span>
              <span style="color:var(--text-muted)">${item.count} hits</span>
            </div>
            <div class="bar-progress-track">
              <div class="bar-progress-fill" style="width: ${pct}%;"></div>
            </div>
          </div>
        `;
      }).join("");
    }

    // Render Escalation Table
    const tableEl = document.getElementById("escalation-table-body");
    if (tableEl && data.active_escalations) {
      tableEl.innerHTML = data.active_escalations.map(t => `
        <tr>
          <td><code style="color:#93c5fd">${escapeHtml(t.ticket_id)}</code></td>
          <td><strong>${escapeHtml(t.customer_name)}</strong></td>
          <td>${escapeHtml(t.reason)}</td>
          <td><span style="color:#fbbf24; font-weight:600">${escapeHtml(t.sentiment_label)}</span></td>
          <td><span style="color:#f43f5e; font-weight:600">${escapeHtml(t.priority)}</span></td>
          <td><span style="color:#34d399">${escapeHtml(t.status)}</span></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Analytics fetch error:", err);
  }
}

// Knowledge Fetcher
async function fetchKnowledge() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/knowledge`);
    if (!res.ok) return;
    const docs = await res.json();

    const grid = document.getElementById("kb-cards-grid");
    if (grid) {
      grid.innerHTML = docs.map(doc => `
        <div class="kb-document-card">
          <div style="font-weight:700; font-size:1rem; color:#93c5fd; margin-bottom:0.4rem">📄 ${escapeHtml(doc.title)}</div>
          <p style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.75rem">
            Doc: <code>${escapeHtml(doc.doc_name)}</code> • ${doc.sections.length} indexed sections
          </p>
          <div style="font-size:0.82rem; color:#cbd5e1; line-height:1.5;">
            ${doc.sections.slice(0, 2).map(s => `
              <div style="margin-bottom:0.5rem">
                <strong style="color:var(--accent-cyan)">${escapeHtml(s.section_title)}:</strong>
                <div>${escapeHtml(s.text.slice(0, 110))}...</div>
              </div>
            `).join("")}
          </div>
        </div>
      `).join("");
    }
  } catch (err) {
    console.error("Knowledge fetch error:", err);
  }
}

// Model Classes Fetcher
async function fetchModelInfo() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/intents`);
    if (!res.ok) return;
    const data = await res.json();

    const pillsEl = document.getElementById("model-classes-pills");
    if (pillsEl && data.classes) {
      pillsEl.innerHTML = data.classes.map(c => `
        <span style="background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle); padding:0.35rem 0.75rem; border-radius:999px; font-size:0.78rem; font-family:var(--font-mono); margin:3px; display:inline-block; color:#93c5fd;">${escapeHtml(c)}</span>
      `).join("");
    }
  } catch (err) {
    console.error("Model info fetch error:", err);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function formatMarkdown(str) {
  if (!str) return "";
  let s = escapeHtml(str);
  s = s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\n/g, "<br>");
  return s;
}

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();

  const inputEl = document.getElementById("user-input-box");
  if (inputEl) {
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") submitMessage();
    });
  }

  document.querySelectorAll(".quick-prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const text = chip.getAttribute("data-query");
      if (text) submitMessage(text);
    });
  });

  const resetBtn = document.getElementById("btn-reset-chat");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      document.getElementById("chat-messages-box").innerHTML = `
        <div class="msg-row bot">
          <div class="agent-avatar" style="width:32px; height:32px; background:linear-gradient(135deg, #3b82f6, #06b6d4)">AI</div>
          <div class="msg-bubble">
            Session reset. Hello! I'm your AI Customer Service Assistant. How can I help you today?
          </div>
        </div>
      `;
      currentSessionId = "sess_" + Math.random().toString(36).substring(2, 9);
    });
  }
});

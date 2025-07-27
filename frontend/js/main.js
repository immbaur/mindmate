const API_URL = "http://127.0.0.1:8000/chat";   // adjust if backend port differs
const USER_ID = "immi";                         // hard-coded for now

const btn   = document.getElementById("callBtn");
const input = document.getElementById("msgInput");
const out   = document.getElementById("output");

btn.addEventListener("click", async () => {
  const message = input.value.trim();
  if (!message) {
    alert("Please type a message first.");
    input.focus();
    return;
  }

  out.value = "⏳ Waiting for server…";

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID, message })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();           // { reply: "..." }
    out.value  = data.reply;
  } catch (err) {
    console.error(err);
    out.value = `❌ ${err}`;
  }
});
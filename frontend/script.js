let currentMode = "recommendation";

const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const body = document.body;
const modeToggleBtn = document.getElementById("mode-toggle");

// Append messages to chat
function appendMessage(role, text) {
  if (role === "bot") {
    const blocks = text.split(/\n\s*\n/).filter(b => b.trim() !== '');
    let i = 0;

    const typing = document.createElement("p");
    typing.className = "bot typing-indicator";
    typing.textContent = "Nova is typing...";
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    const showNext = () => {
      if (i < blocks.length) {
        typing.remove();
        const msg = document.createElement("p");
        msg.className = "bot";
        msg.innerHTML = `<strong>Nova:</strong><br>${blocks[i].replace(/\n/g, "<br>")}`;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
        i++;
        if (i < blocks.length) {
          chatBox.appendChild(typing);
          chatBox.scrollTop = chatBox.scrollHeight;
        }
        setTimeout(showNext, 900);
      }
    };

    setTimeout(showNext, 700);
  } else {
    const msg = document.createElement("p");
    msg.className = "user";
    msg.innerHTML = `<strong>You:</strong> ${text}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

// Mode themes
function applyAggressiveTheme() {
  body.classList.add("aggressive-theme");
}

function applyDefaultTheme() {
  body.classList.remove("aggressive-theme");
}

// Chat form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  userInput.value = "";

  if (message.toLowerCase() === "#chatbot") {
    currentMode = "chatbot";
    appendMessage("bot", "🧠 Switched to Chatbot mode. Ask me anything.");
    applyAggressiveTheme();
    return;
  }

  if (message.toLowerCase() === "#recommend") {
    currentMode = "recommendation";
    applyDefaultTheme();
    const res = await fetch("http://127.0.0.1:5000/init");
    const data = await res.json();
    appendMessage("bot", "🔄 Back to Recommendation mode.");
    appendMessage("bot", data.reply);
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, mode: currentMode }),
    });

    const data = await res.json();
    appendMessage("bot", data.reply);
  } catch {
    appendMessage("bot", "❌ Server error. Please try again later.");
  }
});

// Welcome
window.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch("http://127.0.0.1:5000/init");
  const data = await res.json();
  appendMessage("bot", data.reply);
});

// Optional: Toggle with button
modeToggleBtn.addEventListener("click", () => {
  if (body.classList.contains("aggressive-theme")) {
    currentMode = "recommendation";
    applyDefaultTheme();
  } else {
    currentMode = "chatbot";
    applyAggressiveTheme();
  }
});

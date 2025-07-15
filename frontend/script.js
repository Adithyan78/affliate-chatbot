const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// Function to append messages to chat box
function appendMessage(role, text) {
  const msg = document.createElement("p");
  msg.className = role;
  msg.textContent = `${role === "user" ? "You" : "Nova"}: ${text}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Handle form submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value;

  // Show user message
  appendMessage("user", message);
  userInput.value = "";

  // Fetch response from backend
  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();

  // Show bot reply
  appendMessage("bot", data.reply);
});

// Show initial bot message when page loads
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/init");
    const data = await res.json();
    appendMessage("bot", data.reply);
  } catch (error) {
    appendMessage("bot", "⚠️ Couldn't connect to server.");
  }
});

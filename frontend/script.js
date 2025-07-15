
const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value;

  // Show user message
  const userMsg = document.createElement("p");
  userMsg.className = "user";
  userMsg.textContent = "You: " + message;
  chatBox.appendChild(userMsg);

  // Clear input
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
  const botMsg = document.createElement("p");
  botMsg.className = "bot";
  botMsg.innerHTML = "Bot: " + data.reply;
  chatBox.appendChild(botMsg);

  chatBox.scrollTop = chatBox.scrollHeight;
});

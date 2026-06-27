const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = "message " + sender;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, "user");
    userInput.value = "";

    addMessage("Typing...", "bot");
    const typingNode = chatBox.lastChild;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        });
        const data = await res.json();
        typingNode.textContent = data.reply;
    } catch (err) {
        typingNode.textContent = "Sorry, something went wrong. Please try again.";
    }
});

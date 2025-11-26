async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage("You: " + message);
    input.value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: message })
        });

        const data = await response.json();
        addMessage("Bot: " + data.reply);

    } catch (error) {
        addMessage("Bot: ERROR connecting to backend.");
    }
}

function addMessage(text) {
    const box = document.getElementById("chat-box");
    const p = document.createElement("p");
    p.innerText = text;
    box.appendChild(p);
    box.scrollTop = box.scrollHeight;
}

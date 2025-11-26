async function sendMessage() {
    const inputField = document.getElementById("user-input");
    let userMessage = inputField.value.trim();

    if (!userMessage) return;

    addMessage("You: " + userMessage);
    inputField.value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text: userMessage })
        });

        const data = await response.json();
        addMessage("Bot: " + data.reply);

    } catch (error) {
        addMessage("Bot: ❌ Error connecting to backend.");
    }
}

function addMessage(text) {
    const chatBox = document.getElementById("chat-box");
    const message = document.createElement("p");
    message.innerText = text;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}

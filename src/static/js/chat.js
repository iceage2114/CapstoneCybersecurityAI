document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    let userInputField = document.getElementById("user-input");
    let userInput = userInputField.value.trim();

    if (userInput !== "") {
        updateChatHistory("You: " + userInput);

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: userInput }),
        });

        const data = await response.json();
        if (data?.data?.message) {
            updateChatHistory("AI: " + data.data.message);
        }
    }

    userInputField.value = "";
    userInputField.focus();
}

function updateChatHistory(message) {
    const chatHistory = document.getElementById("chat-history");
    const messageElement = document.createElement("p");
    messageElement.textContent = message;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

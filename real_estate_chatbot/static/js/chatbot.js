// chatbot.js - handles the floating chat widget UI and talks to /chatbot endpoint

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const closeBtn = document.getElementById("chatbot-close");
    const box = document.getElementById("chatbot-box");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");

    // Show a welcome message once when the widget first opens
    let hasGreeted = false;

    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = `chat-msg ${sender}`;
        msg.textContent = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    toggleBtn.addEventListener("click", () => {
        box.classList.toggle("hidden");
        if (!hasGreeted) {
            addMessage(
                "Hi! I'm your AI property assistant. Ask me about locations, budgets, or property types. Try: 'Show me apartments in Pune under 50 lakh'",
                "bot"
            );
            hasGreeted = true;
        }
    });

    closeBtn.addEventListener("click", () => {
        box.classList.add("hidden");
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        addMessage(text, "user");
        input.value = "";

        addMessage("Typing...", "bot");
        const typingIndicator = messages.lastChild;

        try {
            const response = await fetch("/chatbot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
            });
            const data = await response.json();
            typingIndicator.remove();
            addMessage(data.reply, "bot");
        } catch (err) {
            typingIndicator.remove();
            addMessage("Sorry, something went wrong connecting to the server.", "bot");
        }
    });
});

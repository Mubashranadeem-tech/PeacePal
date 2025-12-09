


// Function to add a message bubble to the chat
// We added a 'messageId' parameter to help us find specific messages later
function addMessage(text, sender, messageId = null) {
    const chatBox = document.getElementById('chatBox');
    const msgDiv = document.createElement('div');
    
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    // Assign an ID if provided (used for the loading message)
    if (messageId) {
        msgDiv.id = messageId;
    }
    
    // Convert newlines to breaks for the bot response
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
}

async function handlePrediction() {
    const userTextField = document.getElementById('userText');
    const userText = userTextField.value.trim();

    // 1. Validate Input
    if (userText === "") {
        alert("Please type how you are feeling first.");
        return;
    }

    // 2. Add User Message
    addMessage(userText, 'user');
    userTextField.value = ""; // Clear input
    
    // 3. Add "Analyzing..." Message with a UNIQUE ID
    const loadingId = "loading-bubble"; 
    addMessage("<i class='fa-solid fa-spinner fa-spin'></i> Analyzing...", 'bot', loadingId);
    
    // 4. Gather Data
    const healthData = {
        age: document.getElementById('age').value,
        sleep: document.getElementById('sleep').value,
        physical: document.getElementById('physical').value,
        screen: document.getElementById('screen').value,
        stress: document.getElementById('stress').value,
        smoking: document.getElementById('smoking').value,
        userText: userText
    };

    try {
        // 5. Send to Backend (Make sure port matches!)
        const response = await fetch('predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(healthData)
        });

        const result = await response.json();

        // --- THE FIX IS HERE ---
        // 6. Find the "Analyzing..." bubble and REMOVE it
        const loadingBubble = document.getElementById(loadingId);
        if (loadingBubble) {
            loadingBubble.remove();
        }
        
        // 7. Show the Real Response
        addMessage(result.advice, 'bot');
        
        // Update the Risk Badge
        const badge = document.getElementById('risk-badge');
        if (badge) {
            badge.innerText = result.risk;
            badge.className = "badge " + (result.risk.includes("High") ? "high-risk" : "low-risk");
        }

    } catch (error) {
        console.error(error);
        
        // Remove loading bubble even if there is an error
        const loadingBubble = document.getElementById(loadingId);
        if (loadingBubble) loadingBubble.remove();

        addMessage("⚠️ Error connecting to server. Is app.py running?", 'bot');
    }
}

// Allow pressing "Enter" to send
document.getElementById("userText").addEventListener("keydown", function(e) {
    if (e.key === "Enter") handlePrediction();
});

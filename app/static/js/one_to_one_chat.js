const token = localStorage.getItem("token");

const url = window.location.href;

// Split the URL by '/' and get the last value
const lastSegment = url.split('/').pop();

// Get the receiver's ID dynamically, e.g., from the URL or user selection
const receiverId = lastSegment; // Implement this to fetch the receiver ID
console.log(receiverId)

// Initialize WebSocket connection for one-to-one chat
const ws = new WebSocket(`ws://localhost:8001/api/chat/one-to-one/chat/${receiverId}?token=${token}`);

ws.onclose = () => {
    console.log("WebSocket connection for one-to-one chat closed.");
};

const messagesDiv = document.getElementById("message_to_one");
const messageInput = document.getElementById("messageInputToOne");

ws.onmessage = (event) => {
    const message = document.createElement("div");
    message.textContent = event.data;
    message.style.padding = "5px";
    message.style.borderBottom = "1px solid #eee";
    messagesDiv.appendChild(message);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
};

function sendMessageToOne() {
    const message = messageInput.value;
    if (message.trim() !== "") {
        ws.send(message);
        messageInput.value = "";
    } else {
        alert("Message cannot be empty!");
    }
}

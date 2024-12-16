//const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMiwiZXhwIjoxNzM2ODc3NjU0fQ.KFykHDQs1JxjPY8t8pGfieJ4NkhgsdEWbMyJUY0w_J8"
//
//
//const ws = new WebSocket('ws://localhost:8001/api/chat/ws/chat?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMiwiZXhwIjoxNzM2ODc3NjU0fQ.KFykHDQs1JxjPY8t8pGfieJ4NkhgsdEWbMyJUY0w_J8');

//const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMiwiZXhwIjoxNzM2ODc3NjU0fQ.KFykHDQs1JxjPY8t8pGfieJ4NkhgsdEWbMyJUY0w_J8"
const token = localStorage.getItem("token");

const ws = new WebSocket(`ws://localhost:8001/api/chat/ws/chat?token=${token}`);


ws.onclose = () => {
    console.log("WebSocket connection closed.");
};


const messagesDiv = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");


ws.onmessage = (event) => {
    const message = document.createElement("div");
    message.textContent = event.data;
    message.style.padding = "5px";
    message.style.borderBottom = "1px solid #eee";
    messagesDiv.appendChild(message);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
};


function sendMessage() {
    const message = messageInput.value;
    console.log(message);
    if (message.trim() !== "") {
        ws.send(message);
        messageInput.value = "";
    }
    else{
        ws.send("Can't get meessage!");
    }
}

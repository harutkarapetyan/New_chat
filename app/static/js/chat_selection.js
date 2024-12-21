const globalChatBtn = document.getElementById("globalChatBtn");
const oneToOneChatBtn = document.getElementById("oneToOneChatBtn");
const userListDiv = document.getElementById("userList");
const usersListElement = document.getElementById("users");

globalChatBtn.addEventListener("click", function () {
//  window.location.href = "/global/chat"; // Global Chat page URL
    window.location.href = "http://127.0.0.1:8001/home-page";
});

oneToOneChatBtn.addEventListener("click", function () {
  userListDiv.style.display = "block"; // Show user list
  fetchUsers();
});

// Function to fetch users for one-to-one chat
function fetchUsers() {
  fetch("http://127.0.0.1:8001/api/auth/users") // API endpoint to get list of users
    .then(response => response.json())
    .then(data => {
      usersListElement.innerHTML = ""; // Clear the existing list
      data.forEach(user => {
        const userItem = document.createElement("li");
        userItem.textContent = `${user.first_name} ${user.last_name}`;
        userItem.addEventListener("click", function () {
          startOneToOneChat(user.user_id);
        });
        usersListElement.appendChild(userItem);
      });
    })
    .catch(error => console.log("Error fetching users:", error));
}

// Function to initiate one-to-one chat with selected user
function startOneToOneChat(userId) {
  window.location.href = `/ws/one-to-one/${userId}`; // Redirect to specific one-to-one chat page
}

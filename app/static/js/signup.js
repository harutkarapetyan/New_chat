const submitButton = document.getElementById("submitBtn")
submitButton.addEventListener("click", function (e) {
   e.preventDefault();

  // Get the values from the form fields
  const firstName = document.getElementById("first_name").value;
  const lastName = document.getElementById("last_name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password").value;
  const phoneNumber = document.getElementById("phone_number").value;


  // Create an object with the form data
  const userData = {
    first_name: firstName,
    last_name: lastName,
    email: email,
    password: password,
    confirm_password: password,
    phone_number: phoneNumber
  };


  fetch("http://127.0.0.1:8001/api/auth/add-user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": 'application/json'
    },
    body: JSON.stringify(userData) // Send the form data as JSON
  })
  .then (window.location.href = "http://127.0.0.1:8001/signin-page")
});


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
//
//  console.log(firstName)
//  console.log(lastName)
//  console.log(email)
//  console.log(password)
//  console.log(confirmPassword)
//  console.log(phoneNumber)

//  // Basic validation to check if the passwords match
//  if (password !== confirmPassword) {
//    alert("Passwords do not match!");
//    return;
//  }

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



//fetch("http://127.0.0.1:8008/api/auth/add-user", {
//    method: "POST",
//    headers: {
//      "Content-Type": "application/json",
//      "Accept": 'application/json'
//    },
//    body: JSON.stringify({
//        first_name: "John",  // Not null
//        last_name: "Doe",    // Not null
//        email: "john.doe@gmail.com", // Not null, valid email format
//        password: "password123",  // Not null
//        confirm_password: "password123",  // Not null, and matches password
//        phone_number: "+1234567890"  // Not null, valid phone format
//    })
//})
//.then(response => response.json())
//.then(data => {
//    console.log(data);  // Log the response to check for errors
//})
//.catch(error => {
//    console.error('Error:', error);
//});



for (let btn of document.getElementsByClassName("log-user-out")) {
  btn.addEventListener("click", (event) => {
    alert("You have logged out successfully");
    console.log("Logged out")
  })
}
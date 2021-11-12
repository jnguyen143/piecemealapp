function signupDefault() {
    let username = document.getElementById("username").value;
    let email = document.getElementById("email").value;
    let givenName = document.getElementById("given_name").value;
    let familyName = document.getElementById("family_name").value;
    let password = document.getElementById("password").value;

    // Encrypt the data, then send it to the server
    let payload = {
        authentication: "Default",
        username: username,
        email: email,
        given_name: givenName,
        family_name: familyName,
        password: password
    };

    encryptData(JSON.stringify(payload)).then(data => {
        fetch("/api/start-signup", {
            method: "POST",
            headers: {
                'Content-Type': 'application/octet-stream'
            },
            body: data
        }).then(response => response.json()).then(response => {
            if (response.success)
                window.location.href = "/";
            else
                alert("Error signing up");
        });
    }).catch(err => alert("ERROR: " + err));

    return false;
}
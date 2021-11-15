import { encryptData } from './EncryptedRequests.js';

document.getElementById('login-form').onsubmit = () => {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    // Encrypt the data, then send it to the server
    let payload = {
        authentication: "Default",
        username: username,
        password: password
    };

    try {
        encryptData(JSON.stringify(payload)).then(data => {
            fetch("/api/start-login", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/octet-stream'
                },
                body: data
            }).then(response => response.json()).then(response => {
                if (response.success)
                    window.location.href = "/";
                else
                    alert("Error logging in");
            });
        }).catch(err => alert("ERROR: " + err));
    } catch (e) {
        alert("Err: " + e);
        return false;
    }

    return false;
};
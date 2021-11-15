import { showToast } from "./Toast.js";
import { encryptData } from "./EncryptedRequests.js";

// ========== CONTENT-SPECIFIC FUNCTIONS ========== //
function containsInvalidUsernameChars(str) {
    return !(/^([a-zA-Z0-9\$\.\_\-]+)$/.test(str));
}

function loadProfileEvents() {
    document.getElementById("profile-new-username-field").addEventListener("input", (event) => {
        let value = event.target.value;
        if (value === "") {
            // If the input is empty, just disable the button
            document.getElementById("profile-new-username-button").disabled = true;
            document.getElementById("profile-new-username-error").innerText = "";
        } else if (containsInvalidUsernameChars(value)) {
            // If the input contains invalid characters, disable the button and show an error message
            document.getElementById("profile-new-username-button").disabled = true;
            document.getElementById("profile-new-username-error").innerText = "You can only use alphanumeric characters, underscores, dashes, periods, and dollar signs in usernames";
        } else {
            // If everything is good, enable the button and clear the error message
            document.getElementById("profile-new-username-button").disabled = false;
            document.getElementById("profile-new-username-error").innerText = "";
        }
    });

    document.getElementById("profile-new-username-button").onclick = () => {
        let newUsername = document.getElementById("profile-new-username-field").value;
        fetch("/api/update-username", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ new_username: newUsername })
        }).then(response => response.json()).then(response => {
            if (response.result == 0) {
                gotoPage("profile").then(() => {
                    loadProfileEvents();
                    showToast("Username updated successfully");
                });
            } else if (response.result == 3) {
                showToast("The specified username was already taken");
            } else {
                showToast("Failed to update username");
            }
        }).catch(() => {
            showToast("Failed to update username");
        });
    };

    document.getElementById("profile-delete-account-button").onclick = () => {
        fetch("/api/delete-user", {
            method: "POST"
        }).then(response => response.json()).then(response => {
            if (response.result == 0)
                window.location.href = "/";
            else
                showToast("Failed to delete account");
        }).catch(() => showToast("Failed to delete account"));
    };

    let oldPasswordField = document.getElementById("profile-old-password-field");
    if (oldPasswordField != null) {
        oldPasswordField.addEventListener("input", (event) => {
            let value = event.target.value;
            if (value !== "") {
                // Check the new password field too before enabling the button
                let newPasswordField = document.getElementById("profile-new-password-field");
                if (newPasswordField.value !== "")
                    document.getElementById("profile-new-password-button").disabled = false;
                else
                    document.getElementById("profile-new-password-button").disabled = true;
            } else {
                document.getElementById("profile-new-password-button").disabled = true;
            }
        });

        document.getElementById("profile-new-password-field").addEventListener("input", (event) => {
            let value = event.target.value;
            if (value !== "") {
                // Check the old password field too before enabling the button
                let oldPasswordField = document.getElementById("profile-old-password-field");
                if (oldPasswordField.value !== "")
                    document.getElementById("profile-new-password-button").disabled = false;
                else
                    document.getElementById("profile-new-password-button").disabled = true;
            } else {
                document.getElementById("profile-new-password-button").disabled = true;
            }
        });

        document.getElementById("profile-new-password-button").onclick = () => {
            encryptData(JSON.stringify({
                old_password: document.getElementById("profile-old-password-field").value,
                new_password: document.getElementById("profile-new-password-field").value
            })).then(data => {
                fetch("/api/update-password", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/octet-stream"
                    },
                    body: data
                }).then(response => response.json()).then(response => {
                    if (response.result == 2)
                        showToast("Incorrect password");
                    else if (response.result != 0)
                        showToast("Failed to update password");
                    else {
                        gotoPage("profile").then(() => loadProfileEvents()).then(() => showToast("Password updated successfully"));
                    }
                }).catch(() => showToast("Failed to update password"));
            }).catch(() => showToast("Failed to update password"));
        };
    }
}

// ========== GENERAL FUNCTIONS ========== //

async function gotoPage(pageName) {
    await fetch("/api/account/" + pageName).then(response => response.text()).then(response => {
        document.getElementById("main-content").innerHTML = response;
    }).catch(() => showToast("Internal server error"));
}

document.getElementById("sb-profile").onclick = () => {
    gotoPage("profile").then(() => loadProfileEvents());
};

document.getElementById("sb-friends").onclick = () => {
    gotoPage("friends");
};

document.getElementById("sb-recipes").onclick = () => {
    gotoPage("recipes");
};

document.getElementById("sb-ingredients").onclick = () => {
    gotoPage("ingredients");
};

document.getElementById("sb-intolerances").onclick = () => {
    gotoPage("intolerances");
};

// As soon as the document loads, go to the profile page
gotoPage("profile").then(() => loadProfileEvents());
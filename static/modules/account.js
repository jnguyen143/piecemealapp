import { showToast } from "./Toast.js";
import { encryptData } from "./EncryptedRequests.js";

// ========== CONTENT-SPECIFIC FUNCTIONS ========== //

// ---------- FRIENDS ---------- //
function loadFriendsEvents() {
    for (let btn of document.getElementsByClassName("friend-delete")) {
        btn.addEventListener("click", (event) => {
            let userId = event.target.getAttribute("friend-id");
            fetch("/api/delete-relationship", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId })
            }).then(response => response.json()).then(response => {
                if (response.result != 0)
                    showToast("Failed to delete friend");
                else {
                    gotoPage("friends").then(() => loadFriendsEvents()).then(() => showToast("Successfully deleted friend"));
                }
            }).catch(() => showToast("Failed to delete friend"));
        });
    }

    for (let btn of document.getElementsByClassName("friend-request-accept")) {
        let listElement = btn.parentElement;
        btn.addEventListener("click", (event) => {
            let userId = event.target.getAttribute("friend-id");
            fetch("/api/handle-friend-request", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId, action: 1 })
            }).then(response => response.json()).then(response => {
                if (response.result != 0)
                    showToast("Failed to add friend");
                else {
                    listElement.remove();
                    gotoPage("friends").then(() => loadFriendsEvents()).then(() => showToast("Successfully added friend"));
                }
            }).catch(() => showToast("Failed to add friend"));
        });
    }

    for (let btn of document.getElementsByClassName("friend-request-deny")) {
        let listElement = btn.parentElement;
        btn.addEventListener("click", (event) => {
            let userId = event.target.getAttribute("friend-id");
            fetch("/api/handle-friend-request", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId, action: 0 })
            }).then(response => response.json()).then(response => {
                if (response.result != 0)
                    showToast("Failed to deny friend request");
                else {
                    listElement.remove();
                    gotoPage("friends").then(() => loadFriendsEvents()).then(() => showToast("Friend request denied"));
                }
            }).catch(() => showToast("Failed to deny friend request"));
        });
    }

    document.getElementById("friends-add-name-field").addEventListener("input", (event) => {
        // If this field is now blank, enable the username field
        let value = event.target.value;
        if (value === "") {
            document.getElementById("friends-add-username-field").disabled = false;
        } else {
            document.getElementById("friends-add-username-field").disabled = true;
        }
    });

    document.getElementById("friends-add-username-field").addEventListener("input", (event) => {
        // If this field is now blank, enable the name field
        let value = event.target.value;
        if (value === "") {
            document.getElementById("friends-add-name-field").disabled = false;
        } else {
            document.getElementById("friends-add-name-field").disabled = true;
        }
    });

    document.getElementById("friends-add-search-button").addEventListener("click", () => {
        let nameField = document.getElementById("friends-add-name-field");
        let usernameField = document.getElementById("friends-add-username-field");

        if (nameField.disabled) {
            // Search by username
            fetch("/api/account/search-users?" + new URLSearchParams({
                search_by: "username", query: usernameField.value
            })).then(response => response.text()).then(response => {
                document.getElementById("friends-add-search-results").innerHTML = response;
                loadFriendSearchEvents();
            }).catch((err) => showToast("Failed to search for users: " + err));
        } else {
            // Search by name
            fetch("/api/account/search-users?" + new URLSearchParams({
                search_by: "name", query: nameField.value
            })).then(response => response.text()).then(response => {
                document.getElementById("friends-add-search-results").innerHTML = response;
                loadFriendSearchEvents();
            }).catch((err) => showToast("Failed to search for users " + err));
        }
    });
}

function loadFriendSearchEvents() {
    for (let btn of document.getElementsByClassName("search-results-user-add")) {
        btn.addEventListener("click", (event) => {
            // Send a friend request
            let userId = event.target.getAttribute("user-id");
            fetch("/api/send-friend-request", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId })
            }).then(response => response.json()).then(response => {
                if (response.result == 0) {
                    showToast("Friend request sent");
                    btn.disabled = true;
                } else {
                    showToast("Failed to send friend request");
                }
            }).catch(() => showToast("Failed to send friend request"));
        });
    }
}

// ---------- PROFILE ---------- //

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
    gotoPage("friends").then(() => loadFriendsEvents());
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
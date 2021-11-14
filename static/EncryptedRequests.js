/**
Returns the original data encrypted using the server's public key.
*/
async function encryptData(original) {
    let result = "";
    await fetch("/api/get-public-key").then(response => response.json()).then(response => {
        let publicKey = forge.pki.publicKeyFromPem(response.key);
        let encrypted = publicKey.encrypt(original, "RSA-OAEP", {
            md: forge.md.sha256.create(),
            mgf1: forge.mgf1.create()
        });
        result = forge.util.encode64(encrypted);
    });
    return result;
}
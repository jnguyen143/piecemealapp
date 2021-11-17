/**
Returns the original data encrypted using the server's public key.
*/
async function encryptData(original) {
  /* eslint-disable no-undef */
  let result = '';
  await fetch('/api/get-public-key').then((response) => response.json()).then((response) => {
    const publicKey = forge.pki.publicKeyFromPem(response.key);
    const encrypted = publicKey.encrypt(original, 'RSA-OAEP', {
      md: forge.md.sha256.create(),
      mgf1: forge.mgf1.create(),
    });
    result = forge.util.encode64(encrypted);
  });
  return result;
}

export { encryptData }; // eslint-disable-line

from Crypto.PublicKey import RSA


def generate_keys():
    """
    Function that writes and exports the application's private and public keys
    """
    keypair = RSA.generate(2048)
    with open("../private_key.pem", "wb") as f:
        f.write(keypair.exportKey())
    with open("../public_key.pem", "wb") as f:
        f.write(keypair.publickey().exportKey())

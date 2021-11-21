"""
Generates public and private keypairs.
"""

from Crypto.PublicKey import RSA


def generate_keys():
    """
    Function that writes and exports the application's private and public keys
    """
    keypair = RSA.generate(2048)
    with open("../private_key.pem", "wb") as file:
        file.write(keypair.exportKey())
    with open("../public_key.pem", "wb") as file:
        file.write(keypair.publickey().exportKey())

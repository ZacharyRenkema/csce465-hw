import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

CMD = b'{"action":"READ","path":"notes.txt"}'

def encrypt(key, nonce, plaintext):
    return Cipher(algorithms.AES(key), modes.CTR(nonce)).encryptor().update(plaintext)

def decrypt(key, nonce, cipher):
    return Cipher(algorithms.AES(key), modes.CTR(nonce)).decryptor().update(cipher)

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def relay(cipher: bytes) -> bytes:
    pos = 11             
    old_cmd = b"READ"
    new_cmd = b"MAKE"

    tampered = bytearray(cipher)
    for i in range(len(new_cmd)):
        tampered[pos + i] ^= old_cmd[i] ^ new_cmd[i]
    return bytes(tampered)
    
def main():
    key = os.urandom(32)
    nonce = os.urandom(16)
    encr_text = encrypt(key, nonce, CMD)
    print("Encrypted using AES mode CTR:", encr_text)
    
    # decrypt
    decr_text = decrypt(key, nonce, encr_text)
    print ("Decrypted using Cipher decryptor:", decr_text)
    
    # use relay function
    modified_txt = relay(encr_text)
    print("Relay function used to mod original cmd:", modified_txt)
    new_decr_text = decrypt(key, nonce, modified_txt)
    print("Decrpyted new text:", new_decr_text)
    
    print("ct ^ tampered:", xor(encr_text, modified_txt)[11:15].hex())
    print("READ ^ MAKE  :", xor(b"READ", b"MAKE").hex())
    print("pt ^ new pt  :", xor(CMD, new_decr_text)[11:15].hex())

    for n in (1, 2):
        print(f"receiver processes copy #{n}:", decrypt(key, nonce, modified_txt))
    
if __name__ == "__main__":
    main()
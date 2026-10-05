import struct
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

VERSION = 1
GATEWAY_TO_NODE = 0x01
NODE_TO_GATEWAY = 0x02

HEADER = struct.Struct(">BBQBI")   
IV_LEN = 16
TAG_LEN = 32
MIN_RECORD_LEN = HEADER.size + IV_LEN + TAG_LEN
MAX_SEQUENCE = 2**64 - 1


class RecordError(Exception): pass
class MalformedRecord(RecordError): pass
class BadTag(RecordError): pass
class WrongDirection(RecordError): pass
class SequenceError(RecordError): pass


class SecureChannel:

    def __init__(self, role: bytes, keys):
        if role == b"gateway":
            self.send_direction, self.recv_direction = GATEWAY_TO_NODE, NODE_TO_GATEWAY
            self.send_enc, self.send_mac = keys.K_g2n_enc, keys.K_g2n_mac
            self.recv_enc, self.recv_mac = keys.K_n2g_enc, keys.K_n2g_mac
        elif role == b"node":
            self.send_direction, self.recv_direction = NODE_TO_GATEWAY, GATEWAY_TO_NODE
            self.send_enc, self.send_mac = keys.K_n2g_enc, keys.K_n2g_mac
            self.recv_enc, self.recv_mac = keys.K_g2n_enc, keys.K_g2n_mac
        else:
            raise ValueError("role must be b'gateway' or b'node'")

        self.session_id = keys.session_id
        self.send_sequence = 0   
        self.recv_sequence = 0   


def _build_iv(session_id: bytes, sequence: int) -> bytes:
    return session_id + struct.pack(">Q", sequence)


def _aes_ctr(key: bytes, iv: bytes, data: bytes) -> bytes:
    # CTR encryption and decryption are the same XOR with the keystream.
    context = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return context.update(data) + context.finalize()


def _new_mac(key: bytes, data: bytes) -> hmac.HMAC:
    mac = hmac.HMAC(key, hashes.SHA256())
    mac.update(data)
    return mac


def seal(channel: SecureChannel, message_type: int, plaintext: bytes) -> bytes:
    """Encrypt, then MAC. Returns the full record to put on the wire."""
    sequence = channel.send_sequence
    if sequence > MAX_SEQUENCE:
        raise SequenceError("send sequence space exhausted")

    iv = _build_iv(channel.session_id, sequence)
    ciphertext = _aes_ctr(channel.send_enc, iv, plaintext)
    header = HEADER.pack(VERSION, channel.send_direction, sequence,
                         message_type, len(ciphertext))
    tag = _new_mac(channel.send_mac, header + iv + ciphertext).finalize()

    channel.send_sequence = sequence + 1
    return header + iv + ciphertext + tag


def open_record(channel: SecureChannel, record: bytes):
    if len(record) < MIN_RECORD_LEN:
        raise MalformedRecord("record is too short")

    header = record[:HEADER.size]
    iv = record[HEADER.size:HEADER.size + IV_LEN]
    ciphertext = record[HEADER.size + IV_LEN:-TAG_LEN]
    tag = record[-TAG_LEN:]
    version, direction, sequence, message_type, declared_length = HEADER.unpack(header)

    if direction != channel.recv_direction:
        raise WrongDirection("record is not addressed to this direction")
    try:
        _new_mac(channel.recv_mac, header + iv + ciphertext).verify(tag)
    except InvalidSignature:
        raise BadTag("record failed authentication") from None

    if version != VERSION:
        raise MalformedRecord("unsupported record version")
    if declared_length != len(ciphertext):
        raise MalformedRecord("ciphertext length does not match header")
    if iv != _build_iv(channel.session_id, sequence):
        raise MalformedRecord("IV does not match session and sequence")
    if sequence != channel.recv_sequence:
        raise SequenceError(
            f"expected sequence {channel.recv_sequence}, got {sequence}")

    plaintext = _aes_ctr(channel.recv_enc, iv, ciphertext)
    channel.recv_sequence += 1
    return message_type, plaintext


def main():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from handshake import Party, load_params, demo_hs

    # demo and test
    params = load_params()
    gw_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    node_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    gateway = Party(b"gateway-01", b"gateway", gw_rsa,
                    b"node-01", node_rsa.public_key(), params)
    node = Party(b"node-01", b"node", node_rsa,
                 b"gateway-01", gw_rsa.public_key(), params)
    keys_gw, keys_nd = demo_hs(gateway, node)

    gw_channel = SecureChannel(b"gateway", keys_gw)
    node_channel = SecureChannel(b"node", keys_nd)

    cmd = b'{"action":"READ","path":"notes.txt"}'
    record = seal(gw_channel, 1, cmd)
    print("gateway to node:", record.hex())
    print("node:", open_record(node_channel, record))

    reply = seal(node_channel, 2, b'{"status":"ok"}')
    print("gateway:", open_record(gw_channel, reply))

    tampered = bytearray(seal(gw_channel, 1, cmd))
    for i, (old, new) in enumerate(zip(b"READ", b"MAKE")):
        tampered[HEADER.size + IV_LEN + 11 + i] ^= old ^ new
    try:
        open_record(node_channel, bytes(tampered))
    except RecordError as error:
        print("bitflip error:", type(error).__name__)

    try:
        open_record(node_channel, record)
    except RecordError as error:
        print("replay error:", type(error).__name__)


if __name__ == "__main__":
    main()
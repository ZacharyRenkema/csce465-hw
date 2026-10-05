"""incorrect RSA public key, invalid RSA-PSS transcript signature, or reflected handshake message"""
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from handshake import demo_hs, sha256, BadSignature, ReflectedMessage


def test_incorrect_rsa_public_key(parties):
    gateway, node = parties
    stranger = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    gateway.peer_rsa_public = stranger.public_key()   # gateway trusts the wrong key

    with pytest.raises(BadSignature):
        demo_hs(gateway, node)


def test_invalid_transcript_signature(parties):
    gateway, node = parties
    gateway.begin_session()
    node.begin_session()
    th = sha256(gateway.construct_canonical_transcript(
        node.identity, node.dh_public, node.nonce))
    signature = bytearray(node.sign_transcript(th))
    signature[0] ^= 0x01   

    with pytest.raises(BadSignature):
        gateway.verify_peer(node.identity, node.dh_public, node.nonce,
                            th, bytes(signature))


def test_reflected_handshake_message(parties):
    gateway, node = parties
    gateway.begin_session()
    th = sha256(gateway.construct_canonical_transcript(
        gateway.identity, gateway.dh_public, gateway.nonce))
    own_signature = gateway.sign_transcript(th)

    with pytest.raises(ReflectedMessage):   
        gateway.verify_peer(gateway.identity, gateway.dh_public, gateway.nonce,
                            th, own_signature)
import os
import struct
from pathlib import Path
from dataclasses import dataclass
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import dh, padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_parameters

# CONSTANTS
PARAMS_PATH = Path(__file__).parent / "ffdhe3072.pem"
PROTOCOL_LABEL = b"CSCE465-HS-v2"
GROUP_ID = b"ffdhe3072"


class HandshakeError(Exception): pass
class BadSignature(HandshakeError): pass
class UnexpectedIdentity(HandshakeError): pass
class ReflectedMessage(HandshakeError): pass
class MalformedTranscript(HandshakeError): pass

PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH)

def sha256(data: bytes) -> bytes:
    h = hashes.Hash(hashes.SHA256())
    h.update(data)
    return h.finalize()

@dataclass
class SessionKeys:
    K_g2n_enc: bytes
    K_g2n_mac: bytes
    K_n2g_enc: bytes
    K_n2g_mac: bytes
    session_id: bytes

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    return h.finalize()

class Party:
    """As per Task 2, this is the Party object for client and recipient 
    
    Attributes:
        identity: Party name
        role: Either gateway or node
        rsa_private: Long term private key (RSA signed)
        expected_peer_id: Name party is talking to
        peer_rsa_public: Peer public key
        params: Loaded from pem file (p and g)
        dh_private: Sessions S_A 
        dh_public: g^S_A mod p as 384 big-endian 
        nonce: random 16 bytes 
    """
    def __init__(self, identity, role, 
                 rsa_private, expected_peer_id, 
                 peer_rsa_public, params,):
        
        self.identity=identity
        self.role=role
        self.rsa_private=rsa_private
        self.expected_peer_id=expected_peer_id
        self.peer_rsa_public=peer_rsa_public
        self.params=params
        self.dh_private=None
        self.dh_public=None
        self.nonce=None
    
    # Session Functions
    def begin_session(self):
        """Loads DH key, public, and nonce"""
        self.dh_private = self.generate_dh_private()
        self.dh_public = self.generate_dh_public()
        self.nonce = self.generate_nonce()
    
    def construct_canonical_transcript(self, peer_identity,
                                   peer_dh_public, peer_nonce) -> bytes:
        
        if self.role == b"gateway":
            gw_id, gw_dh, gw_nonce = self.identity, self.dh_public, self.nonce
            nd_id, nd_dh, nd_nonce = peer_identity, peer_dh_public, peer_nonce
        else:
            gw_id, gw_dh, gw_nonce = peer_identity, peer_dh_public, peer_nonce
            nd_id, nd_dh, nd_nonce = self.identity, self.dh_public, self.nonce

        header     = self.length_prefixed(PROTOCOL_LABEL) + self.length_prefixed(GROUP_ID)
        identities = self.length_prefixed(gw_id) + self.length_prefixed(nd_id)
        dh_publics = self.length_prefixed(gw_dh) + self.length_prefixed(nd_dh)
        nonces     = self.length_prefixed(gw_nonce) + self.length_prefixed(nd_nonce)

        return b"".join([header, identities, dh_publics, nonces])
    
    
    # TODO: 
    def verify_peer(self, peer_identity, peer_dh_public, peer_nonce,
                th, signature) -> None:
        # verify reflection
        if (self.dh_public == peer_dh_public) or (self.identity == peer_identity) or (self.nonce == peer_nonce):
            raise ReflectedMessage("peer values match my own")

        # verify identity
        if peer_identity != self.expected_peer_id:
            raise UnexpectedIdentity("unexpected peer identity")

        # verify signature
        peer_role = b"node" if self.role == b"gateway" else b"gateway"
        try:
            self.peer_rsa_public.verify(signature, peer_role + th, PSS, hashes.SHA256())
        except InvalidSignature:
            raise BadSignature("peer signature did not verify")
        
    def derive_session(self, peer_dh_public: bytes, th: bytes) -> SessionKeys:
        y = int.from_bytes(peer_dh_public, "big")
        peer_key = dh.DHPublicNumbers(y, self.params.parameter_numbers()).public_key()
        z = self.dh_private.exchange(peer_key).rjust(384, b"\x00")

        K_master   = sha256(b"CSCE465-KDF-v1" + z + th)
        K_g2n_enc    = hmac_sha256(K_master, b"gateway-to-node encryption" + th)
        K_g2n_mac    = hmac_sha256(K_master, b"gateway-to-node MAC" + th)
        K_n2g_enc    = hmac_sha256(K_master, b"node-to-gateway encryption" + th)
        K_n2g_mac    = hmac_sha256(K_master, b"node-to-gateway MAC" + th)
        session_id = hmac_sha256(K_master, b"session identifier" + th)[:8]
        
        return SessionKeys(K_g2n_enc, K_g2n_mac, K_n2g_enc, K_n2g_mac, session_id)
    
    @staticmethod
    def decode_transcript(data: bytes) -> list:
        transcript_fields = [] 
        pos = 0
        while pos < len(data):
            if len(data) - pos < 4:
                raise MalformedTranscript("truncated length prefix")
            
            (length,) = struct.unpack(">I", data[pos:pos + 4])
            pos += 4
            
            if len(data) - pos < length:
                raise MalformedTranscript("declared length exceeds remaining data")
            
            transcript_fields.append(data[pos:pos + length])
            pos += length

        if len(transcript_fields) != 8:
            raise MalformedTranscript("mismatch in num of fields in transcript")
        if transcript_fields[0] != PROTOCOL_LABEL or transcript_fields[1] != GROUP_ID:
            raise MalformedTranscript("wrong protocol label or group")
        if len(transcript_fields[4]) != 384 or len(transcript_fields[5]) != 384:
            raise MalformedTranscript("wrong byte count")
        if len(transcript_fields[6]) != 16 or len(transcript_fields[7]) != 16:
            raise MalformedTranscript("nonce is not 16 bytes")
        return transcript_fields
        
    # Helper Functions    
    def generate_dh_private(self):
        return self.params.generate_private_key()

    def generate_dh_public(self):
        y = self.dh_private.public_key().public_numbers().y
        return y.to_bytes(384, "big")

    def generate_nonce(self):
        return os.urandom(16)

    @staticmethod
    def length_prefixed(field: bytes) -> bytes:
        return struct.pack(">I", len(field)) + field
    
    def sign_transcript(self, th: bytes) -> bytes:
        return self.rsa_private.sign(self.role + th, PSS, hashes.SHA256())


def load_params():
    with open(PARAMS_PATH, "rb") as f:
        return load_pem_parameters(f.read())


def demo_hs(gateway, node):
    gateway.begin_session()
    node.begin_session()
    t_gw = gateway.construct_canonical_transcript(node.identity, node.dh_public, node.nonce)
    t_nd = node.construct_canonical_transcript(gateway.identity, gateway.dh_public, gateway.nonce)
    Party.decode_transcript(t_gw)
    Party.decode_transcript(t_nd)
    th_gw, th_nd = sha256(t_gw), sha256(t_nd)

    sig_gw = gateway.sign_transcript(th_gw)
    sig_nd = node.sign_transcript(th_nd)

    gateway.verify_peer(node.identity, node.dh_public, node.nonce, th_gw, sig_nd)
    node.verify_peer(gateway.identity, gateway.dh_public, gateway.nonce, th_nd, sig_gw)

    keys_gw = gateway.derive_session(node.dh_public, th_gw)
    keys_nd = node.derive_session(gateway.dh_public, th_nd)
    return keys_gw, keys_nd


def main():
    params = load_params()
    gw_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    node_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    gateway = Party(b"gateway-01", b"gateway", gw_rsa,
                    b"node-01", node_rsa.public_key(), params)
    node = Party(b"node-01", b"node", node_rsa,
                 b"gateway-01", gw_rsa.public_key(), params)

    keys_gw, keys_nd = demo_hs(gateway, node)
    assert keys_gw == keys_nd
    print("handshake complete, session_id:", keys_gw.session_id.hex())
    
    
if __name__ == "__main__":
    main()
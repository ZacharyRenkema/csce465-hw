"""This is the configuration file defining params for pytests"""

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from handshake import Party, load_params, demo_hs
from secure_record import SecureChannel


@pytest.fixture(scope="session")
def rsa_keys():
    gw_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    node_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return gw_rsa, node_rsa


@pytest.fixture
def parties(rsa_keys):
    gw_rsa, node_rsa = rsa_keys
    params = load_params()
    gateway = Party(b"gateway-01", b"gateway", gw_rsa,
                    b"node-01", node_rsa.public_key(), params)
    node = Party(b"node-01", b"node", node_rsa,
                 b"gateway-01", gw_rsa.public_key(), params)
    return gateway, node


@pytest.fixture
def channels(parties):
    keys_gw, keys_nd = demo_hs(*parties)
    gw_channel = SecureChannel(b"gateway", keys_gw)
    node_channel = SecureChannel(b"node", keys_nd)
    return gw_channel, node_channel
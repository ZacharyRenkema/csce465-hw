"""This is the test file that tests for a valid handshake and bidirectional messages"""
from handshake import demo_hs
from secure_record import SecureChannel, seal, open_record

def test1(parties):
    keys_gw, keys_nd = demo_hs(*parties)
    assert keys_gw == keys_nd
    assert len(keys_gw.session_id) == 8
 
    gw = SecureChannel(b"gateway", keys_gw)
    nd = SecureChannel(b"node", keys_nd)
    assert open_record(nd, seal(gw, 1, b"ping")) == (1, b"ping")
    assert open_record(gw, seal(nd, 2, b"pong")) == (2, b"pong")
    assert open_record(nd, seal(gw, 1, b"ping again")) == (1, b"ping again")
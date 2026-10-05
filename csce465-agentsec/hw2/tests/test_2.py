"""Test code for (2) in task 4 for modified ciphertext"""
import pytest
from secure_record import seal, open_record, BadTag

CIPHER = 31   

def test_modified_ciphertext_is_rejected(channels):
    gw, nd = channels
    record = bytearray(seal(gw, 1, b'{"action":"READ","path":"notes.txt"}'))
    record[CIPHER + 11] ^= 0x1F   

    with pytest.raises(BadTag):
        open_record(nd, bytes(record))
    assert nd.recv_sequence == 0   

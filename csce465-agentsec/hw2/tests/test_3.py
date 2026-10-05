"""modified authenticated header"""
import pytest
from secure_record import seal, open_record, BadTag

MESSAGE_TYPE_INDEX = 10   


def test_modified_header_is_rejected(channels):
    gw, nd = channels
    record = bytearray(seal(gw, 1, b"hello world!"))
    record[MESSAGE_TYPE_INDEX] ^= 0x01   

    with pytest.raises(BadTag):
        open_record(nd, bytes(record))
    assert nd.recv_sequence == 0
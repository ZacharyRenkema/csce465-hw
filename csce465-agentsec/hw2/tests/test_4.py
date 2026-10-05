"""replayed record test"""
import pytest
from secure_record import seal, open_record, SequenceError


def test_replayed_record_is_rejected(channels):
    gw, nd = channels
    record = seal(gw, 1, b"run once")

    assert open_record(nd, record) == (1, b"run once")   
    with pytest.raises(SequenceError):
        open_record(nd, record)                          
    assert nd.recv_sequence == 1
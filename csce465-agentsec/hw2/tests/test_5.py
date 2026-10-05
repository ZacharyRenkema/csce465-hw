"""record reflected into the opposite direction test"""
import pytest
from secure_record import (seal, open_record, WrongDirection, BadTag,
                           NODE_TO_GATEWAY)

DIRECTION_INDEX = 1


def test_reflected_record_is_rejected(channels):
    gw, nd = channels
    record = seal(gw, 1, b"node only")

    with pytest.raises(WrongDirection):
        open_record(gw, record)  


def test_reflected_record_with_rewritten_direction_is_rejected(channels):
    gw, nd = channels
    record = bytearray(seal(gw, 1, b"node only"))
    record[DIRECTION_INDEX] = NODE_TO_GATEWAY   

    with pytest.raises(BadTag):
        open_record(gw, bytes(record))
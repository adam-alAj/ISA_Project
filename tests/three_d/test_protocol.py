"""Protocol validation stays GPU and Qt independent."""

import json

import pytest

from src.visualization.three_d.protocol import command, decode_message, encode_message


def test_protocol_round_trip_is_versioned_json_lines():
    message = command("speed", multiplier=4.0)
    encoded = encode_message(message)
    assert encoded.endswith(b"\n")
    assert decode_message(encoded) == message


@pytest.mark.parametrize("value", [
    {"schema_version": 2, "cmd": "play"},
    {"schema_version": 1, "cmd": "not-a-command"},
    [1, 2, 3],
])
def test_protocol_rejects_unknown_version_commands_and_non_objects(value):
    with pytest.raises((ValueError, TypeError)):
        decode_message(json.dumps(value))

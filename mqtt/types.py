from uctypes import BF_LEN, BF_POS, BFUINT8, UINT8, UINT16

MQTTHeaderLayout = {
    "type": 0 | BFUINT8 | 4 << BF_POS | 4 << BF_LEN,
    "dup": 0 | BFUINT8 | 3 << BF_POS | 1 << BF_LEN,
    "qos": 0 | BFUINT8 | 1 << BF_POS | 2 << BF_LEN,
    "retain": 0 | BFUINT8 | 0 << BF_POS | 1 << BF_LEN,
}

MQTTConnectFlagsLayout = {
    "username": 0 | BFUINT8 | 7 << BF_POS | 1 << BF_LEN,
    "password": 0 | BFUINT8 | 6 << BF_POS | 1 << BF_LEN,
    "will_retain": 0 | BFUINT8 | 5 << BF_POS | 1 << BF_LEN,
    "will_qos": 0 | BFUINT8 | 3 << BF_POS | 2 << BF_LEN,
    "will": 0 | BFUINT8 | 2 << BF_POS | 1 << BF_LEN,
    "clean_session": 0 | BFUINT8 | 1 << BF_POS | 1 << BF_LEN,
}

MQTTConnAckLayout = {
    "length": 1 | UINT8,
    "session_present": 2 | BFUINT8 | 0 << BF_POS | 1 << BF_LEN,
    "return_code": 3 | UINT8,
}

MQTTAckRecvLayout = {
    "length": 1 | UINT8,
    "packet_id": 2 | UINT16,
}

MQTTAckSendLayout = {
    "header": (0, MQTTHeaderLayout),
    "length": 1 | UINT8,
    "packet_id": 2 | UINT16,
}

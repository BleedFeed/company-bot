import hashlib

# Same weird JS hex alphabet (note: 'd' is missing, 'e' duplicated)
HEX_MAP = "0123456789abceef"


def lXt_py(value):
    s = str(value) + "a"
    b = s.encode("utf-8")
    md5_bytes = hashlib.md5(b).digest()
    out = []
    for x in md5_bytes:
        out.append(HEX_MAP[(x >> 4) & 0xF])
        out.append(HEX_MAP[x & 0xF])

    return "".join(out)

import hashlib
import struct
from array import array

from .general import *
from .swfunc import xor_arrays

def generate_key_iv(filepath, size):
    """
    This was reverse engineered from game code and is not standard AES.

    IN: filepath: relative file path
        size : size in bytes

    OUT: key, iv tuple

    RE notes:
    1. Get utf-16 version of relative file path. Needs to be lower case version of path.
      Example: "data\\settings\all.settings" is represented by b"\x64\x00\x61\x00\x74\x00\x61\x00..."
                (note the 2 bytes per character "d" = b"\x64\x00")

    2. Do a SHA-1 hash on the filepath.

    3. The first 4 bytes of this hash and the size in bytes of the file is then used on a algorithm that seems to be
       some sort of PRNG. There was more instructions reversed in the actual algorithm, but they didn't seem to affect
       output.

    """

    sha1 = hashlib.sha1()

    filenameutf = filepath.lower().encode('utf-16LE')

    sha1.update(filenameutf)
    seed = sha1.hexdigest()[:8]

    word = int(seed, 16)
    word = struct.pack('<L', word)
    word = struct.unpack(">L", word)[0]
    word *= size
    word &= 0xFFFFFFFF

    keyiv = []
    for _ in range(32):
        lower = word & 0xFFFF
        higher = word >> 16
        mul = (lower * 18000) + higher
        lastbyte = mul & 0xFF
        if mul == 0:
            lastbyte = b"\xFF"
        word = mul
        keyiv.append(lastbyte)

    key = array('B', keyiv[0:16])
    iv = array('B', keyiv[16:32])

    return key, iv


def expand_key(key):
    """
    This was reverse engineered from game code and is not standard AES.

    IN: key: 16 byte key.

    OUT: roundkeys: List with 11 round keys. 16 bytes each.

    RE notes:

    This one fooled me for quite a while. But it's basically using the aeskeygenassist x86 instruction to generate
    round keys in a non-standard way as far as I can tell. (I'm not a crypto expert :P)
    """

    def aeskeygenassist_short(key):
        return array('B', [SBOX[key[1]], SBOX[key[2]], SBOX[key[3]], SBOX[key[0]]])

    def genkey(roundkey, mode, rcon=1):
        rk1 = roundkey[0:4]
        rk2 = roundkey[4:8]
        rk3 = roundkey[8:12]
        rk4 = roundkey[12:16]

        if mode == 1:
            res1 = xor_arrays(rk1, aeskeygenassist_short(rk4))
            res2 = xor_arrays(res1, array('B', [RCON[rcon], 0, 0, 0]))

        else:  # elif mode == 2:
            res1 = xor_arrays(aeskeygenassist_short(rk4), array('B', [RCON[rcon], 0, 0, 0]))
            res2 = xor_arrays(res1, rk1)

        res3 = xor_arrays(res2, rk2)
        res4 = xor_arrays(res3, rk3)
        res5 = xor_arrays(res4, rk4)
        return res2 + res3 + res4 + res5

    roundkeys = []
    roundkeys.append(key.tobytes())
    roundkeys.append(genkey(roundkey=key, mode=1, rcon=1).tobytes())

    for round_ in range(1, 10):
        rk = roundkeys[round_]
        roundkeys.append(genkey(roundkey=rk, mode=2, rcon=round_ + 1).tobytes())

    return roundkeys

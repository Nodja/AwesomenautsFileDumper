from array import array
import hashlib, struct
from ._aesenc import ffi, lib

SBOX = bytearray.fromhex('637c777bf26b6fc53001672bfed7ab76'
                         'ca82c97dfa5947f0add4a2af9ca472c0'
                         'b7fd9326363ff7cc34a5e5f171d83115'
                         '04c723c31896059a071280e2eb27b275'
                         '09832c1a1b6e5aa0523bd6b329e32f84'
                         '53d100ed20fcb15b6acbbe394a4c58cf'
                         'd0efaafb434d338545f9027f503c9fa8'
                         '51a3408f929d38f5bcb6da2110fff3d2'
                         'cd0c13ec5f974417c4a77e3d645d1973'
                         '60814fdc222a908846eeb814de5e0bdb'
                         'e0323a0a4906245cc2d3ac629195e479'
                         'e7c8376d8dd54ea96c56f4ea657aae08'
                         'ba78252e1ca6b4c6e8dd741f4bbd8b8a'
                         '703eb5664803f60e613557b986c11d9e'
                         'e1f8981169d98e949b1e87e9ce5528df'
                         '8ca1890dbfe6426841992d0fb054bb16')

RCON = bytearray.fromhex('8d01020408102040801b366cd8ab4d9a'
                         '2f5ebc63c697356ad4b37dfaefc59139'
                         '72e4d3bd61c29f254a943366cc831d3a'
                         '74e8cb8d01020408102040801b366cd8'
                         'ab4d9a2f5ebc63c697356ad4b37dfaef'
                         'c5913972e4d3bd61c29f254a943366cc'
                         '831d3a74e8cb8d01020408102040801b'
                         '366cd8ab4d9a2f5ebc63c697356ad4b3'
                         '7dfaefc5913972e4d3bd61c29f254a94'
                         '3366cc831d3a74e8cb8d010204081020'
                         '40801b366cd8ab4d9a2f5ebc63c69735'
                         '6ad4b37dfaefc5913972e4d3bd61c29f'
                         '254a943366cc831d3a74e8cb8d010204'
                         '08102040801b366cd8ab4d9a2f5ebc63'
                         'c697356ad4b37dfaefc5913972e4d3bd'
                         '61c29f254a943366cc831d3a74e8cb')


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
       some sort of PRNG. There was more instructions reversed in the actual algorithm, but they didn't seem to do
       anything.

    """

    sha1 = hashlib.sha1()

    filenameutf = filepath.lower().encode('utf-16LE')

    sha1.update(filenameutf)
    seed = sha1.hexdigest()[:8]

    word = int(seed, 16)
    word = struct.pack('<L', word)
    word = struct.unpack(">L", word)[0]
    word *= size
    word = word & 0xFFFFFFFF

    keyIV = []
    for _ in range(32):
        lower = word & 0xFFFF
        higher = word >> 16
        mul = (lower * 18000) + higher
        lastbyte = mul & 0xFF
        if (mul == 0):
            lastbyte = b"\xFF"
        word = mul
        keyIV.append(lastbyte)

    key = array('B', keyIV[0:16])
    iv = array('B', keyIV[16:32])

    return key, iv

def xor_arrays(arr1, arr2):
    """ Does a XOR on 2 arrays, very slow"""
    retarr = array('B')
    for i in range(len(arr1)):
        retarr.append(arr1[i] ^ arr2[i])
    return retarr

def fast_xor(arr1, arr2):
    """ Fast XOR on 2 arrays, uses cffi (native C code)
    Make sure arrays are 16 bytes long or you will have problems.
    """
    ptr_block = ffi.from_buffer(arr1)
    ptr_ctext = ffi.from_buffer(arr2)
    lib.fast_xor(ptr_block, ptr_ctext)

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

        else: # elif mode == 2:
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

def encrypt_block(block, roundkeys):
    """ Does the whole AES 11 rounds on one block, can probably be made faster if we pass a pointer to roundkeys instead
        of the list itself.
    """
    ptr = ffi.from_buffer(block)
    lib.encrypt(ptr, ptr, roundkeys)

def encrypt_data(plaintext, filepath):
    """
    Encrypt data in CFB mode
    """

    filesize = len(plaintext)

    key, iv = generate_key_iv(filepath, filesize)
    roundkeys =  expand_key(key)

    ptext = array('B', plaintext)
    ctext = array('B')

    block = iv
    for offset in range(0, len(ptext), 16):
        encrypt_block(block, roundkeys)
        block = xor_arrays(ptext[offset:offset + 16], block)
        ctext += block
    return ctext.tobytes()

def decrypt_data(ciphertext, filepath):
    """Decrypt data in CFB mode"""

    filesize = len(ciphertext)

    key, iv = generate_key_iv(filepath, filesize)
    roundkeys =  expand_key(key)

    ctext = array('B', ciphertext)
    plaintext = array('B')

    block = iv

    tail = len(ctext) % 16
    for offset in range(0, len(ctext) - tail, 16):
        encrypt_block(block, roundkeys)
        fast_xor(block, ctext[offset:offset + 16])
        plaintext += block
        block = ctext[offset:offset + 16]

    if tail > 0:
        encrypt_block(block, roundkeys)
        ctext_padded = ctext[-tail:] + array('B', [0] * (16 - tail))
        fast_xor(block, ctext_padded)
        plaintext += block[:tail]
    return plaintext.tobytes()
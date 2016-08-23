from .awesomefuncs import *
from .general import *

if has_accel():
    from .hwfunc import inplace_xor, encrypt_block
else:
    print("Your cpu does not support AES acceleration, gg.")

def encrypt_data(plaintext, filepath):
    """
    Encrypt data in CFB mode
    """

    filesize = len(plaintext)

    key, iv = generate_key_iv(filepath, filesize)
    roundkeys = expand_key(key)

    ptext = array('B', plaintext)
    ctext = array('B')

    block = iv
    for offset in range(0, len(ptext), 16):
        encrypt_block(block, roundkeys)
        inplace_xor(block, ptext[offset:offset + 16])
        ctext += block
    return ctext.tobytes()


def decrypt_data(ciphertext, filepath):
    """Decrypt data in CFB mode"""

    filesize = len(ciphertext)

    key, iv = generate_key_iv(filepath, filesize)
    roundkeys = expand_key(key)

    ctext = array('B', ciphertext)
    plaintext = array('B')

    block = iv

    tail = len(ctext) % 16
    for offset in range(0, len(ctext) - tail, 16):
        encrypt_block(block, roundkeys)
        inplace_xor(block, ctext[offset:offset + 16])
        plaintext += block
        block = ctext[offset:offset + 16]

    if tail > 0:
        encrypt_block(block, roundkeys)
        ctext_padded = ctext[-tail:] + array('B', [0] * (16 - tail))
        inplace_xor(block, ctext_padded)
        plaintext += block[:tail]
    return plaintext.tobytes()

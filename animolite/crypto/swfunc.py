# most code taken from https://github.com/realpython/book2-exercises/blob/master/py2manager/gluon/contrib/aes.py
from array import array
from .general import *


def xor_arrays(arr1, arr2):
    """ Does a XOR on 2 arrays, very slow"""
    retarr = array('B')
    for i in range(len(arr1)):
        retarr.append(arr1[i] ^ arr2[i])
    return retarr


def sub_bytes(block):
    """SubBytes step, apply S-box to all bytes
    Depending on whether encrypting or decrypting, a different sbox array
    is passed in.
    """

    for i in range(16):
        block[i] = SBOX[block[i]]


def shift_rows(b):
    """ShiftRows step. Shifts 2nd row to left by 1, 3rd row by 2, 4th row by 3
    Since we're performing this on a transposed matrix, cells are numbered
    from top to bottom::
      0  4  8 12   ->    0  4  8 12    -- 1st row doesn't change
      1  5  9 13   ->    5  9 13  1    -- row shifted to left by 1 (wraps around)
      2  6 10 14   ->   10 14  2  6    -- shifted by 2
      3  7 11 15   ->   15  3  7 11    -- shifted by 3
    """

    b[1], b[5], b[9], b[13] = b[5], b[9], b[13], b[1]
    b[2], b[6], b[10], b[14] = b[10], b[14], b[2], b[6]
    b[3], b[7], b[11], b[15] = b[15], b[3], b[7], b[11]


def mix_columns(block):
    """MixColumns step. Mixes the values in each column"""

    # Cache global multiplication tables (see below)
    mul_by_2 = gf_mul_by_2
    mul_by_3 = gf_mul_by_3

    # Since we're dealing with a transposed matrix, columns are already
    # sequential
    for i in range(4):
        col = i * 4

        # v0, v1, v2, v3 = block[col : col+4]
        v0, v1, v2, v3 = (block[col], block[col + 1], block[col + 2],
                          block[col + 3])

        block[col] = mul_by_2[v0] ^ v3 ^ v2 ^ mul_by_3[v1]
        block[col + 1] = mul_by_2[v1] ^ v0 ^ v3 ^ mul_by_3[v2]
        block[col + 2] = mul_by_2[v2] ^ v1 ^ v0 ^ mul_by_3[v3]
        block[col + 3] = mul_by_2[v3] ^ v2 ^ v1 ^ mul_by_3[v0]


def add_round_key(block, roundkey):
    """AddRoundKey step in AES. This is where the key is mixed into plaintext"""
    inplace_xor(block, roundkey)


def encrypt_block(block, roundkeys):
    """Encrypts a single block. This is the main AES function"""

    # use array instead of bytes
    roundkeys = [array('B', roundkey) for roundkey in roundkeys]

    # For efficiency reasons, the state between steps is transmitted via a
    # mutable array, not returned.
    add_round_key(block, roundkeys[0])

    for round in range(1, 10):
        sub_bytes(block)
        shift_rows(block)
        mix_columns(block)
        add_round_key(block, roundkeys[round])

    sub_bytes(block)
    shift_rows(block)
    # no mix_columns step in the last round
    add_round_key(block, roundkeys[10])

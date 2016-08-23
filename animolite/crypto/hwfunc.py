from ._aesenc import ffi, lib


def inplace_xor(arr1, arr2):
    """ Fast XOR on 2 arrays, uses cffi (native C code)
    Make sure arrays are 16 bytes long or you will have problems.
    """
    ptr_block = ffi.from_buffer(arr1)
    ptr_ctext = ffi.from_buffer(arr2)
    lib.fast_xor(ptr_block, ptr_ctext)


def encrypt_block(block, roundkeys):
    """ Does the whole AES 11 rounds on one block, can probably be made faster if we pass a pointer to roundkeys instead
        of the list itself.
    """
    ptr = ffi.from_buffer(block)
    lib.encrypt(ptr, ptr, roundkeys)

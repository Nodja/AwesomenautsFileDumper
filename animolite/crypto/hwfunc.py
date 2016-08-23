from ._aesenc import ffi, lib


def encrypt_block(block, roundkeys):
    """ Does the whole AES 11 rounds on one block, can probably be made faster if we pass a pointer to roundkeys instead
        of the list itself.
    """
    ptr = ffi.from_buffer(block)
    lib.encrypt(ptr, ptr, roundkeys)

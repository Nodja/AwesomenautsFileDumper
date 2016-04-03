import os
import struct
import zlib
from .crypto import decrypt_data, encrypt_data


def decrypt(data, filepath):
    if data.startswith(b"\x78\x9C"):  # already decrypted, but needs inflation
        return inflate(data)

    decrypteddata = decrypt_data(data, filepath)
    if decrypteddata.startswith(b"\x78\x9C"):  # check for zlib compression
        decrypteddata = inflate(decrypteddata)
    return decrypteddata


def encrypt(data, filepath):
    data = deflate(data)  # TODO: not all files are inflated, needs looking into
    encrypteddata = encrypt_data(data, filepath)
    return encrypteddata


def inflate(data):
    d = zlib.decompressobj()
    out = d.decompress(data)
    out += d.flush()
    return out


def deflate(data):
    c = zlib.compressobj()
    out = c.compress(data)
    out += c.flush(zlib.Z_SYNC_FLUSH)
    return out


def createdir(file):
    directory = os.path.dirname(file)
    if not os.path.exists(directory):
        os.makedirs(directory)


def createandwrite(path, data):
    createdir(path)
    outfile = open(path, "wb")
    outfile.write(data)
    outfile.close()

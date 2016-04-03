import os
import struct
from io import BytesIO


def getfileext(data):
    """Binded file names don't store extensions, this will try to guess the extension according to file data"""
    if data[0:4] == b'RIFF' and data[8:12] == b'WAVE':
        return '.wav'
    if data[0:4] == b'DDS ':
        return '.dds'
    if data[0:12] == b'\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00':
        return '.tga'
    if b'xml version' in BytesIO(data).readline():
        return '.xml'
    else:
        return ''


def unbind(filedata):
    """This is old code I didn't bother refactoring, sorry for the mess"""
    binded = BytesIO(filedata)

    binded.seek(-4, os.SEEK_END)
    indexsize = binded.read(4)
    indexsize = struct.unpack('<I', indexsize)[0]

    binded.seek(0 - (indexsize + 4), os.SEEK_END)
    endofdata = binded.tell()

    indexdata = binded.read(indexsize - 1)

    binded.seek(endofdata, os.SEEK_SET)

    files = []
    for line in reversed(indexdata.splitlines()):
        file = line.split(b'/')
        if (file[0] != b"__END_OF_SERIES_OF_BINDED_FILES__"):
            fstart = int(file[1], 10)
            fend = binded.tell()
            fsize = (fend - fstart)
            binded.seek(-fsize, os.SEEK_CUR)
            buffer = binded.read(fsize + 1)
            name = file[0].decode('utf-8') + getfileext(buffer)
            if (fstart > 0):
                binded.seek(fstart - 1, os.SEEK_SET)
            files.append((name, buffer))
    return files


def bind(files):
    pass  # TODO

import glob
import os
import sys
import re
from settings import nodecrypt
from animolite.filetools import decrypt, createandwrite
from animolite.binded import unbind


def dump(gamedir='.'):
    running_dir = os.getcwd()
    os.chdir(gamedir)
    datafiles = glob.glob('data/**', recursive=True)

    for filepath in datafiles:
        if os.path.isfile(filepath) and not filepath.startswith(tuple(nodecrypt)):
            print("Decrypting {}".format(filepath))

            data_in = open(filepath, "rb").read()
            decrypt_path = filepath.lower()
            data_out = decrypt(data_in, decrypt_path)

            outfilepath = os.path.join(running_dir, '_decrypted', filepath.lstrip("data" + os.path.sep))
            if filepath.endswith("binded"):
                binded_dir = re.sub('\d+\.binded$', '.binded', outfilepath)
                for bindedfile in unbind(data_out):
                    bf_name = bindedfile[0]
                    bf_data = bindedfile[1]
                    out_path = os.path.join(binded_dir, bf_name)
                    createandwrite(out_path, bf_data)
            else:
                createandwrite(outfilepath, data_out)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        dump(sys.argv[1])
    else:
        dump()

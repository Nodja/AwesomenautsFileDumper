import pycpuid

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


def has_accel():
    return 'AES' in pycpuid.features()

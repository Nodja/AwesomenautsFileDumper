from array import array


def xor_arrays(arr1, arr2):
    """ Does a XOR on 2 arrays, very slow"""
    retarr = array('B')
    for i in range(len(arr1)):
        retarr.append(arr1[i] ^ arr2[i])
    return retarr

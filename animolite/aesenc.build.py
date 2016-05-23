"""
I'm not an experienced C programmer, apologies for the code quality bellow. Pull requests accepted. :)
"""

from cffi import FFI
ffi = FFI()

ffi.set_source("_aesenc",
    """ 
        #include <wmmintrin.h>
	#include <stdint.h>

	void encrypt(uint8_t* in, uint8_t* out, uint8_t  rk[][16])
	{

		__m128i m = _mm_loadu_si128((const __m128i*) in);

		__m128i roundkeys[11] = { _mm_loadu_si128((__m128i const*)(&rk[0])),
			_mm_loadu_si128((__m128i const*)(&rk[1])),
			_mm_loadu_si128((__m128i const*)(&rk[2])),
			_mm_loadu_si128((__m128i const*)(&rk[3])),
			_mm_loadu_si128((__m128i const*)(&rk[4])),
			_mm_loadu_si128((__m128i const*)(&rk[5])),
			_mm_loadu_si128((__m128i const*)(&rk[6])),
			_mm_loadu_si128((__m128i const*)(&rk[7])),
			_mm_loadu_si128((__m128i const*)(&rk[8])),
			_mm_loadu_si128((__m128i const*)(&rk[9])),
			_mm_loadu_si128((__m128i const*)(&rk[10]))
		};

		m = _mm_xor_si128(m, roundkeys[0]);
		
		m = _mm_aesenc_si128(m, roundkeys[1]);
		m = _mm_aesenc_si128(m, roundkeys[2]);
		m = _mm_aesenc_si128(m, roundkeys[3]);
		m = _mm_aesenc_si128(m, roundkeys[4]);
		m = _mm_aesenc_si128(m, roundkeys[5]);
		m = _mm_aesenc_si128(m, roundkeys[6]);
		m = _mm_aesenc_si128(m, roundkeys[7]);
		m = _mm_aesenc_si128(m, roundkeys[8]);
		m = _mm_aesenc_si128(m, roundkeys[9]);
		m = _mm_aesenclast_si128(m, roundkeys[10]);
		
		_mm_storeu_si128((__m128i*) out, m);
		
	}
	
	void fast_xor(uint8_t* arr1, uint8_t* arr2)
	{
		__m128i _arr1 = _mm_loadu_si128((const __m128i*) arr1);
		__m128i _arr2 = _mm_loadu_si128((const __m128i*) arr2);

		_arr1 = _mm_xor_si128(_arr1, _arr2);
		_mm_storeu_si128((__m128i*) arr1, _arr1);
	}
    """,
    libraries=[])

ffi.cdef(""" 
		void encrypt(uint8_t* in, uint8_t* out, uint8_t  rk[][16]);
		void fast_xor(uint8_t* arr1, uint8_t* arr2);
""")

if __name__ == "__main__":
    ffi.compile()

# -*- coding: UTF-8 -*-
#
# PyTurboJPEG - A Python wrapper of libjpeg-turbo for decoding and encoding JPEG image.
#
# Copyright (c) 2018, LiloHuang. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ctypes import *
import platform
import numpy as np
import math

# default libTurboJPEG library path
DEFAULT_LIB_PATH = {
    'Darwin' : '/usr/local/opt/jpeg-turbo/lib/libturbojpeg.dylib',   # for Mac OS X
    'Linux'  : '/usr/lib/x86_64-linux-gnu/libturbojpeg.so.0',           # for Linux
    'Windows': 'C:/libjpeg-turbo64/bin/turbojpeg.dll'                # for Windows
}

# pixel formats
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJPF_RGB = 0
TJPF_BGR = 1
TJPF_RGBX = 2
TJPF_BGRX = 3
TJPF_XBGR = 4
TJPF_XRGB = 5
TJPF_GRAY = 6
TJPF_RGBA = 7
TJPF_BGRA = 8
TJPF_ABGR = 9
TJPF_ARGB = 10
TJPF_CMYK = 11

# chrominance subsampling options
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJSAMP_444 = 0
TJSAMP_422 = 1
TJSAMP_420 = 2
TJSAMP_GRAY = 3
TJSAMP_440 = 4

class TurboJPEG(object):
    """A Python wrapper of libjpeg-turbo for decoding and encoding JPEG image."""
    def __init__(self, lib_path=None):
        turbo_jpeg = cdll.LoadLibrary(
            DEFAULT_LIB_PATH[platform.system()] if lib_path is None else lib_path)
        self.__init_decompress = turbo_jpeg.tjInitDecompress
        self.__init_decompress.restype = c_void_p
        
        self.__init_compress = turbo_jpeg.tjInitCompress
        self.__init_compress.restype = c_void_p
        
        self.__destroy = turbo_jpeg.tjDestroy
        self.__destroy.argtypes = [c_void_p]
        self.__destroy.restype = c_int
        
        self.__decompress_header = turbo_jpeg.tjDecompressHeader3
        self.__decompress_header.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        self.__decompress_header.restype = c_int
        
        self.__decompress = turbo_jpeg.tjDecompress2
        self.__decompress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_ubyte),
            c_int, c_int, c_int, c_int, c_int]
        self.__decompress.restype = c_int
        
        self.__compress = turbo_jpeg.tjCompress2
        self.__compress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_int, c_int, c_int, c_int,
            POINTER(c_void_p), POINTER(c_ulong), c_int, c_int, c_int]
        self.__compress.restype = c_int
        
        self.__free = turbo_jpeg.tjFree
        self.__free.argtypes = [c_void_p]
        self.__free.restype = None
        
        self.__get_error_str = turbo_jpeg.tjGetErrorStr
        self.__get_error_str.restype = c_char_p
        self.__scaling_factors = []
        
        class ScalingFactor(Structure):
            _fields_ = ('num', c_int), ('denom', c_int)
        get_scaling_factors = turbo_jpeg.tjGetScalingFactors
        get_scaling_factors.argtypes = [POINTER(c_int)]
        get_scaling_factors.restype = POINTER(ScalingFactor)
        num_scaling_factors = c_int()
        scaling_factors = get_scaling_factors(byref(num_scaling_factors))
        
        for i in range(num_scaling_factors.value):
            self.__scaling_factors.append(
                (scaling_factors[i].num, scaling_factors[i].denom))

    def decode(self, jpeg_buf, new_width, new_height, pixel_format=TJPF_BGR, scaling_factor=None):
        """decode JPEG memory buffer to numpy array."""
        handle = self.__init_decompress()
        try:
            if scaling_factor is not None and \
                scaling_factor not in self.__scaling_factors:
                raise ValueError('supported scaling factors are ' +
                    str(self.__scaling_factors))
            pixel_size = [3, 3, 4, 4, 4, 4, 1, 4, 4, 4, 4, 4]
            
            width = c_int()
            height = c_int()
            jpeg_subsample = c_int()
            jpeg_colorspace = c_int()
            jpeg_array = np.frombuffer(jpeg_buf, dtype=np.uint8)
            src_addr = jpeg_array.ctypes.data_as(POINTER(c_ubyte))
            
            status = self.__decompress_header(
                handle, src_addr, jpeg_array.size, byref(width), byref(height),
                byref(jpeg_subsample), byref(jpeg_colorspace))
            
            if status != 0:
                raise IOError(self.__get_error_str().decode())
                
            """
            if (new_width != 0) and (new_height != 0):
                scaled_width = new_width
                scaled_height = new_height
            elif (new_width != 0):
                scaled_width = new_width
                scaled_height = height.value
            elif (new_height != 0):
                scaled_width = width.value
                scaled_height = new_height
            else:
                scaled_width = new_width
                scaled_height = new_height
            """
            
            print(str(scaled_width))
            print(str(scaled_height))
            
            if scaling_factor is not None:
                def get_scaled_value(dim, num, denom):
                    return (dim * num + denom - 1) // denom
                scaled_width = get_scaled_value(
                    scaled_width, scaling_factor[0], scaling_factor[1])
                scaled_height = get_scaled_value(
                    scaled_height, scaling_factor[0], scaling_factor[1])
            
            
            img_array = np.empty(
                [scaled_height, scaled_width, pixel_size[pixel_format]],
                dtype=np.uint8)
            
            dest_addr = img_array.ctypes.data_as(POINTER(c_ubyte))
            
            status = self.__decompress(
                handle, src_addr, jpeg_array.size, dest_addr, scaled_width,
                0, scaled_height, pixel_format, 0)
            
            if status != 0:
                raise IOError(self.__get_error_str().decode())
            
            if (new_width != None) and (new_height != None):
                img_array = cv2.resize(img_array, (new_width, new_height))
                
            return img_array
        
        finally:
            self.__destroy(handle)

    def encode(self, img_array, quality=85, pixel_format=TJPF_BGR, jpeg_subsample=TJSAMP_422):
        """encode numpy array to JPEG memory buffer."""
        handle = self.__init_compress()
        try:
            jpeg_buf = c_void_p()
            jpeg_size = c_ulong()
            height, width, _ = img_array.shape
            src_addr = img_array.ctypes.data_as(POINTER(c_ubyte))
            status = self.__compress(
                handle, src_addr, width, 0, height, pixel_format,
                byref(jpeg_buf), byref(jpeg_size), jpeg_subsample, quality, 0)
            if status != 0:
                raise IOError(self.__get_error_str().decode())
            dest_buf = create_string_buffer(jpeg_size.value)
            memmove(dest_buf, jpeg_buf.value, jpeg_size.value)
            self.__free(jpeg_buf)
            return dest_buf.raw
        finally:
            self.__destroy(handle)

if __name__ == '__main__':
    jpeg = TurboJPEG()
    in_file = open('cat.1.jpg', 'rb')
    img_array = jpeg.decode(in_file.read(), 64, 64)
    in_file.close()
    # out_file = open('output.jpg', 'wb')
    #out_file.write(jpeg.encode(img_array))
    #out_file.close()
    import matplotlib.pyplot as plt
    plt.imshow(img_array)
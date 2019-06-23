#!/usr/bin/python3
'''
 Image Reformer converts images into C code that can be used with the MSP430 Graphics Library.
 Original Image reformer application from Texas instruments - support UI only (eclipse project)
 This python script can replace it for monochrome pictures only
'''

import sys
import math
import imghdr                              # used to validate file type
import cv2                                 # pip install matplotlib numpy opencv-python ; used to read the bitmap
from colorama import init as init_colorama # used for colored output
from termcolor import colored              # used for colored output

COLOR_CODE = {"ERROR": 'red',
              "DEBUG": 'magenta',
              "RESULT": 'green',}

SOURCE_PROLOGUE = '/* This file was automatically generated using image_reformer.py */' \
                  '\n\n'                                                            \
                  '#include "grlib.h"\n'                                              \
                  '#include "../gfx.h"\n'                                             \
                  '\n'                                                                \
                  'static const unsigned char pixel_{0}1BPP_UNCOMP[] =\n'             \
                  '{{\n'

SOURCE_EPILOGUE = '}};\n'                             \
                  '\n'                                \
                  'const tImage  {0}1BPP_UNCOMP=\n'   \
                  '{{\n'                              \
                  '\tIMAGE_FMT_1BPP_UNCOMP,\n'        \
                  '\t{1},\n'                          \
                  '\t{2},\n'                          \
                  '\t2,\n'                            \
                  '\tg_gfx_palette,\n'                \
                  '\tpixel_{0}1BPP_UNCOMP,\n'         \
                  '}};\n\n'


g_debug_logging = True


def print_debug(message):
    if g_debug_logging:
        print(colored(message, COLOR_CODE["DEBUG"]))


def print_err(message):
    print(colored(message, COLOR_CODE["ERROR"]))


def print_result(message):
    print(colored(message, COLOR_CODE["RESULT"]))


def check_bmp(input_file_name):
    """ Check if filename is a BMP file
        :param input_file_name: input file name
        :type input_file_name:  string
        :return whether the file is .bmp
        :rtype boolean
    """
    return 'bmp' == imghdr.what(input_file_name)


def create_output_source(output_obj_name, bitmap_dimensions, bitmap_values):
    """ Convert hex data to c source file
        :param output_obj_name: desired output object (and filename)
        :type output_obj_name:  string
        :param bitmap_dimensions: bitmap dimensions (x, y)
        :type bitmap_dimensions:  tuple
        :param bitmap_values: values of each bit in bitmap sorted in 2d array
        :type bitmap_values:  list (2d)
    """
    output_file_name = "{}.c".format(output_obj_name)
    print_debug("create_output_source {0}".format(output_file_name))

    # write source file
    with open(output_file_name, 'w') as output_source_file:
        # write prologue
        prologue = SOURCE_PROLOGUE.format(output_obj_name)
        output_source_file.write(prologue)
        
        # write the data structure
        for byte_arr in bitmap_values:
            line = ""
            for byte in byte_arr:
                line += '0x' + hex(byte)[2:] + ', '
            output_source_file.write(line + '\n')

        # write the epilogue
        epilogue = SOURCE_EPILOGUE.format(output_obj_name,
                                          bitmap_dimensions[0],
                                          bitmap_dimensions[1])
        output_source_file.write(epilogue)       


def convert_monochrome(input_bmp_file_name, output_obj_name):
    """ Convert Monochrome BMP file into C file
        :param input_bmp_file_name: input .bmp file in monochrome format
        :type input_bmp_file_name:  string
        :param output_obj_name: desired output object (and filename)
        :type output_obj_name:  string
    """
    image_grayscale = cv2.imread(input_bmp_file_name, 0) # read image as grayscale
    # image_grayscale is an array with values between 0 - 255. 0 equals black and 255 equals white
    image_monochrome = image_grayscale / 255
    # image_monochrome is an array with values between 0 - 1. 0 equals black and 1 equals white
    img_height, img_width = image_monochrome.shape[0], image_monochrome.shape[1]
    print_debug(input_bmp_file_name + " dimensions: {} x {}".format(img_width,img_height))
    print_debug(image_monochrome)
    # create empty 2d list of bytes
    output_arr = [[0 for x in range(math.ceil(img_width/8))] for y in range(img_height)]
    # fill in the 2d list of bytes with the bitmap values
    for y in range(img_height):
        for x in range(img_width):
            if image_monochrome[y][x]:
                output_arr[y][int(x/8)] = output_arr[y][int(x/8)] + (1 << (7-int(x%8)))

    # print_debug(output_arr)
    create_output_source(output_obj_name, (img_width, img_height), output_arr)


def get_args():
    """ Convert Command line arguments into strings
        :return list of arguments strings
        :rtype list
    """
    return sys.argv[1:]


def main():
    file_names = get_args()
    print_debug("args: " + str(file_names))
    if not len(file_names) == 2:
        print_err("Wrong number of arguments")
        return -1
    if not check_bmp(file_names[0]) and check_monochrome(file_names[0]):
        print_err("{0} is not a monochrome bmp file".format(file_names[0]))
        return -2

    convert_monochrome(file_names[0], file_names[1])
    print_result("{0} converted to {1}.c successfully".format(file_names[0], file_names[1]))
    return 0


#
# Run main
#
if __name__ == "__main__":
    init_colorama()
    sys.exit(main())

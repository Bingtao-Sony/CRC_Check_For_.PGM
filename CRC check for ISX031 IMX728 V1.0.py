'''
----------------------------------------------------------------------------------------------------------
This script targets ISX031 with YUV16bits output and IMX728 with RAW12 output saved as .PGM file.

This script will read a pgm file from any where on PC and calculate the CRC and output
its Hex value and line CRC value LINE-BY-LINE.

The out put will be a Folder named CRC_Output_YYMMDDHHMMSS,in it it has 3 file
    1. a copy of the original XX.PGM file which has a timestamp append to it as XX_YYMMDDHHMMSS.PGM
    2. OutPut_CRC_Width_Height_YYMMDDHHMMSS
    3. OutPut_HEX_Width_Height_YYMMDDHHMMSS

After the file is processed, users can click a OPEN FOLDER bottom to open the file folder

Edited by Bingtao.Liu@sony.com
----------------------------------------------------------------------------------------------------------
'''

import crcmod
import os
import re
import shutil
import time
import tkinter as tk
from tkinter import filedialog, Label, Button, StringVar, OptionMenu

# 创建CRC函数
crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)

def read_p5_pgm(filename):
    with open(filename, 'rb') as f:
        header = f.readline().decode().strip()  # Read and decode the first line (P5)

        # Skip lines 2-9
        for _ in range(8):
            line = f.readline().decode().strip()

        width, height = map(int, f.readline().decode().split())  # Read image width and height
        max_value = int(f.readline().decode())  # Read maximum pixel value

        pixels = f.read()  # Read the binary pixel data

    return width, height, max_value, pixels

def calculate_crc_imx728(data):
    # Remove the four padding zeros from each pixel (12 bits)
    clean_data = [data[i:i+3] for i in range(0, len(data), 4)]

    crc_result = crc32_func(b''.join(clean_data))
    return hex(crc_result)

def convert_to_hex_imx728(data):
    # Remove the four padding zeros from each pixel (12 bits)
    clean_data = [data[i:i+3] for i in range(0, len(data), 4)]

    hex_values = ' '.join([f'0x{value:03X}' for value in b''.join(clean_data)])
    return hex_values

def calculate_crc_isx031(data):
    crc_result = crc32_func(data)
    return hex(crc_result)

def convert_to_hex_isx031(data):
    hex_values = ' '.join([f'0x{((value[0] << 8) | value[1]):04X}' for value in zip(data[0::2], data[1::2])])
    return hex_values

def select_algorithm(algorithm):
    global current_algorithm
    current_algorithm = algorithm
    result_label.config(text=f"Selected Algorithm: {current_algorithm}")

def select_file():
    global input_pgm_filename
    input_pgm_filename = filedialog.askopenfilename(filetypes=[("PGM files", "*.pgm")])
    file_label.config(text=f"Selected File: {input_pgm_filename}")

def open_input_folder():
    if input_pgm_filename:
        folder_path = os.path.dirname(input_pgm_filename)
        os.startfile(folder_path)
    else:
        result_label.config(text="Please select a PGM file first.")

def process_file():
    if input_pgm_filename:
        width, height, _, pixels = read_p5_pgm(input_pgm_filename)

        current_time = time.strftime("%y%m%d%H%M%S", time.localtime())

        if current_algorithm == "IMX728—RAW12":
            calculate_crc = calculate_crc_imx728
            convert_to_hex = convert_to_hex_imx728
            pixel_size = 3  # Each pixel is 12 bits (3 bytes)
            folder_suffix = "_IMX728_RAW12"
        elif current_algorithm == "ISX031—YUV4:2:2":
            calculate_crc = calculate_crc_isx031
            convert_to_hex = convert_to_hex_isx031
            pixel_size = 2  # Each pixel is 16 bits (2 bytes)
            folder_suffix = "_ISX031_YUV422"

        output_dir = f"CRC_Output_{current_time}{folder_suffix}"
        os.makedirs(output_dir, exist_ok=True)

        pgm_basename = os.path.basename(input_pgm_filename)
        pgm_dest_path = os.path.join(output_dir, pgm_basename)

        output_file_name = f"OutPut_CRC_{width}_{height}_{current_time}.txt"
        output_file_path = os.path.join(output_dir, output_file_name)

        hex_output_file_name = f"OutPut_Hex_{width}_{height}_{current_time}.txt"
        hex_output_file_path = os.path.join(output_dir, hex_output_file_name)

        with open(output_file_path, 'w') as f, open(hex_output_file_path, 'w') as hex_f:
            for line_number in range(height):
                start_idx = line_number * width * pixel_size
                end_idx = start_idx + width * pixel_size
                row_data = pixels[start_idx:end_idx]
                crc_result = calculate_crc(row_data)
                f.write(f"Line {line_number + 1}: {crc_result}\n")
                hex_values = convert_to_hex(row_data)
                hex_f.write(f"Line {line_number + 1}: {hex_values}\n")

        shutil.copy(input_pgm_filename, pgm_dest_path)
        pgm_dest_with_suffix = os.path.splitext(pgm_dest_path)[0] + f"_{current_time}.pgm"
        os.rename(pgm_dest_path, pgm_dest_with_suffix)

        result_label.config(text=f"CRC results and PGM file saved in {output_dir}")
    else:
        result_label.config(text="Please select a PGM file first.")

def main():
    global file_label, result_label, current_algorithm

    window = tk.Tk()
    window.title("PGM CRC Calculator")

    decoration_label_1 = Label(window, text="************************************************************")
    decoration_label_1.pack()

    algorithms = ["IMX728—RAW12", "ISX031—YUV4:2:2"]
    current_algorithm = algorithms[0]

    algorithm_label = Label(window, text="Select Algorithm:")
    algorithm_label.pack()

    algorithm_var = StringVar(window)
    algorithm_var.set(current_algorithm)
    algorithm_menu = OptionMenu(window, algorithm_var, *algorithms, command=select_algorithm)
    algorithm_menu.pack()

    select_button = Button(window, text="Select PGM File", command=select_file)
    select_button.pack()

    file_label = Label(window, text="")
    file_label.pack()

    process_button = Button(window, text="Process File", command=process_file)
    process_button.pack()

    open_folder_button = Button(window, text="Open Folder", command=open_input_folder)
    open_folder_button.pack()

    result_label = Label(window, text="", justify=tk.LEFT)
    result_label.pack()

    decoration_label_2 = Label(window, text="By Bingtao.Liu@Sony.com")
    decoration_label_2.pack()

    decoration_label_3 = Label(window, text="************************************************************")
    decoration_label_3.pack()

    window.mainloop()

if __name__ == '__main__':
    main()

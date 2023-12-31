# CRC_Check_For_.PGM

This script targets .PGM file (P5 mode) generated by CMOS image sensors developed by SONY Semiconductor Solutions Corporation (SSS).
The supported sensor types are ISX031 (has a YUV 4:2:2 output, 16bits-depth) and IMX728 (has a RAW12[R:G:B = 4:4:4] output, which is 
compressed from RAW24[R:G:B = 8:8:8] but saved as 16bits-depth by adding b.0000 at MSB).

This script will generate a GUI and you can select from ISX031 (which means 16bits-depth) and IMX728 (which is equivilant to 12bits-depth).
Then it reads a pgm file from any where on PC from a pop-out window after clicking "Open file" foulder and calculate the CRC and output its 
Hex value and line CRC value LINE-BY-LINE.

Please note that when selecting IMX728 (which is equivilant to 12bits-depth), the algorithom autometically crops the padded b.0000 at MSB, 
which means that "0x0ABC (pixel 1) 0x0123 (pixel 2)" becomes "0xABC (pixel 1) 0x123 (pixel 2)". The reason for this is that when doing a MIPI
4-lane transmission inside the system, there is no padded b.0000 at MSB. This script is written to determine the line CRC of the transmission 
frame, which means we are intersted in the 12bits per pixel on the wire for IMX728 not (b.0000 + 12bits) per pixel stored in the .pgm file.

The out put will be a Folder named CRC_Output_YYMMDDHHMMSS,in it it has 3 file.
    1. a copy of the original XX.PGM file which has a timestamp append to it as XX_YYMMDDHHMMSS.PGM
    2. OutPut_CRC_Width_Height_YYMMDDHHMMSS (with line CRC clearly labeled as lineX:_____________)
    3. OutPut_HEX_Width_Height_YYMMDDHHMMSS (with padded b.0000 cropped for 12bits-depth)

After the file is processed, users can click a OPEN FOLDER bottom to open the file folder.

Also, please note that the CRC generator matrix is CRC-32-IEEE 802.3 
  Polinomial: 0x04C11DB7
  Initial value: 0xFFFFFFFF
  Input reversal: Enable
  Output reversal: Enable
  XOR value: 0xFFFFFFFF


Edited by Bingtao.Liu@sony.com


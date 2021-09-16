# RN4871-Test-Fixture
RN4871/BM71 module programmer with bed of nails and a TAG Connect cable for in-circuit programming.

This design utilizes the MCP2221A USB to RS-232 bridge for accessing a virtual COM port as well as HID control of GPIO. The GPIO are used to control the MODE and RESET signals of the module. This allows full autonomous control, including COM port selection. 

The PC software is written in Python and supports a simple GUI for ease of use. 

Features -
	Automatic COM port selection
	Automatic MODE and RESET signal control
	HEX file selection
	Programming
	Reading the firmware version of the module
	Programming status via progress bar


![DFU_Box_2 (Custom)](https://user-images.githubusercontent.com/57275578/133635424-63dbe74d-44dc-4b84-8371-615bef7b4764.jpg)
![DFU_Box_3 (Custom)](https://user-images.githubusercontent.com/57275578/133635438-daea0b2b-8d7d-4c5e-9653-2b30cec0ea9e.jpg)
![DFU_Box_4 (Custom)](https://user-images.githubusercontent.com/57275578/133635447-ddd66308-c7f1-4fd5-a29c-cf0db33f8ad4.jpg)
![DFU_Box_1 (Custom)](https://user-images.githubusercontent.com/57275578/133635457-ac1d6277-9632-4716-a20f-be665f76d383.jpg)


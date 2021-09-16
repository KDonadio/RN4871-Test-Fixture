![DFU_Box_2 (Custom)](https://user-images.githubusercontent.com/57275578/133635148-f2f70d4f-9951-4fda-ac90-638b10054015.jpg)



![DFU_Box_2 (Small)](https://user-images.githubusercontent.com/57275578/133633556-05b9bfe1-442c-4597-8312-7c8035a479a7.jpg)
![DFU_Box_3 (Small)](https://user-images.githubusercontent.com/57275578/133633578-8d292f46-6a7c-4e4c-b799-e7bdccfbc217.jpg)
![DFU_Box_4 (Small)](https://user-images.githubusercontent.com/57275578/133633590-b6ddc124-d45e-4049-beb5-0123fe63674a.jpg)
![DFU_Box_1 (Small)](https://user-images.githubusercontent.com/57275578/133633598-6360ad94-8089-469e-a2c1-9588b0838532.jpg)
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

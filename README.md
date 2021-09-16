![DFU_Box_2](https://user-images.githubusercontent.com/57275578/133633045-d0c9493c-c99c-4e1e-8811-038a0f28ac90.jpg)
![DFU_Box_3](https://user-images.githubusercontent.com/57275578/133633060-b0a9f7cd-8acf-418e-9bcc-c0c1a844b5b0.jpg)
![DFU_Box_4](https://user-images.githubusercontent.com/57275578/133633079-c3a701e8-694c-45f9-944f-b142994b10e6.jpg)
![DFU_Box_1](https://user-images.githubusercontent.com/57275578/133633085-e6dd5c8e-dab8-4fb5-a177-a47186a5b829.jpg)
# RN4871-Test-Fixture
RN4871/BM71 programmer with bed of nails and TAG Connect cable for in-circuit programming.
This design utilizes the MCP2221A USB to RS-232 bridge for accessing a virtual COM port as well as HID control of GPIO. The GPIO are used to control the MODE and RESET signals of the module. This allows full autonomous control including COM port selection. 
The PC software is written in Python and supports a simple GUI for ease of use. 
Features -
    Automatic COM port selection
    Automatic control of MODE and RESET signals
    HEX file selection
    Programming
    Reading the version of the module
    Prorgammin status via progress bar

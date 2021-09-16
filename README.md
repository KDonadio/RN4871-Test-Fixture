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

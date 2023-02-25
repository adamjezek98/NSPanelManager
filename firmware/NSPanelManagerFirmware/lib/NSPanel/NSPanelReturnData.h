#include <Arduino.h>

// Return data from command execution
#define NEX_RET_CMD_FAILED (0x00)
#define NEX_RET_CMD_FINISHED (0x01)
#define NEX_RET_EVENT_LAUNCHED (0x88)
#define NEX_RET_EVENT_UPGRADED (0x89)
#define NEX_RET_EVENT_TOUCH_HEAD (0x65)
#define NEX_RET_EVENT_POSITION_HEAD (0x67)
#define NEX_RET_EVENT_SLEEP_POSITION_HEAD (0x68)
#define NEX_RET_CURRENT_PAGE_ID_HEAD (0x66)
#define NEX_RET_STRING_HEAD (0x70)
#define NEX_RET_NUMBER_HEAD (0x71)
#define NEX_RET_INVALID_CMD (0x00)
#define NEX_RET_INVALID_COMPONENT_ID (0x02)
#define NEX_RET_INVALID_PAGE_ID (0x03)
#define NEX_RET_INVALID_PICTURE_ID (0x04)
#define NEX_RET_INVALID_FONT_ID (0x05)
#define NEX_RET_INVALID_BAUD (0x11)
#define NEX_RET_INVALID_VARIABLE (0x1A)
#define NEX_RET_INVALID_OPERATION (0x1B)

// Data received without command execution
#define NEX_OUT_STARTUP (0x00)
#define NEX_OUT_BUFFER_OVERFLOW (0x24)
#define NEX_OUT_TOUCH_EVENT (0x65)
#define NEX_OUT_ENTERED_AUTO_SLEEP (0x86)
#define NEX_OUT_LEFT_AUTO_SLEEP (0x87)
#define NEX_OUT_READY (0x88)
#define NEX_OUT_LEAVING_TRANSPARENT_MODE (0xFD)
#define NEX_OUT_TRANSPARENT_MODE_READY (0xFD)
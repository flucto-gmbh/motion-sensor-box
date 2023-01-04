/*****************************************************************************
* | File      	:   TCS34725.h
* | Author      :   Waveshare team
* | Function    :   TCS34725 driver
* | Info        :
*                Tcs34725 initialization, reading data, writing data 
                 and data processing
*----------------
* |	This version:   V1.0
* | Date        :   2019-01-16
* | Info        :

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
******************************************************************************/
#include "DEV_Config.h"

/**
* Device address
**/
// I2C 7-bit address 0x29, 8-bit address 0x52
#define TCS34725_ADDRESS          (0x29<<1)

/**
* Register
**/
#define TCS34725_CMD_BIT          0x80
#define TCS34725_CMD_Read_Byte    0x00
#define TCS34725_CMD_Read_Word    0x20
#define TCS34725_CMD_Clear_INT    0x66     /* RGBC Interrupt flag clear */

#define TCS34725_ENABLE           0x00     
#define TCS34725_ENABLE_AIEN      0x10    /* RGBC Interrupt Enable */
#define TCS34725_ENABLE_WEN       0x08     /* Wait enable - Writing 1 activates the wait timer */
#define TCS34725_ENABLE_AEN       0x02     /* RGBC Enable - Writing 1 actives the ADC, 0 disables it */
#define TCS34725_ENABLE_PON       0x01    /* Power on - Writing 1 activates the internal oscillator, 0 disables it */

#define TCS34725_ATIME            0x01    /* Integration time */
#define TCS34725_WTIME            0x03    /* Wait time (if TCS34725_ENABLE_WEN is asserted) */
#define TCS34725_WTIME_2_4MS      0xFF    /* WLONG0 = 2.4ms   WLONG1 = 0.029s */
#define TCS34725_WTIME_204MS      0xAB    /* WLONG0 = 204ms   WLONG1 = 2.45s  */
#define TCS34725_WTIME_614MS      0x00    /* WLONG0 = 614ms   WLONG1 = 7.4s   */

#define TCS34725_AILTL            0x04    /* Clear channel lower interrupt threshold */
#define TCS34725_AILTH            0x05
#define TCS34725_AIHTL            0x06    /* Clear channel upper interrupt threshold */
#define TCS34725_AIHTH            0x07

#define TCS34725_PERS             0x0C    /* Persistence register - basic SW filtering mechanism for interrupts */
#define TCS34725_PERS_NONE        0x00  /* Every RGBC cycle generates an interrupt                                */
#define TCS34725_PERS_1_CYCLE     0x01  /* 1 clean channel value outside threshold range generates an interrupt   */
#define TCS34725_PERS_2_CYCLE     0x02  /* 2 clean channel values outside threshold range generates an interrupt  */
#define TCS34725_PERS_3_CYCLE     0x03  /* 3 clean channel values outside threshold range generates an interrupt  */
#define TCS34725_PERS_5_CYCLE     0x04  /* 5 clean channel values outside threshold range generates an interrupt  */
#define TCS34725_PERS_10_CYCLE    0x05  /* 10 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_15_CYCLE    0x06  /* 15 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_20_CYCLE    0x07  /* 20 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_25_CYCLE    0x08  /* 25 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_30_CYCLE    0x09  /* 30 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_35_CYCLE    0x0a  /* 35 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_40_CYCLE    0x0b  /* 40 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_45_CYCLE    0x0c  /* 45 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_50_CYCLE    0x0d  /* 50 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_55_CYCLE    0x0e  /* 55 clean channel values outside threshold range generates an interrupt */
#define TCS34725_PERS_60_CYCLE    0x0f  /* 60 clean channel values outside threshold range generates an interrupt */

#define TCS34725_CONFIG           0x0D
#define TCS34725_CONFIG_WLONG     0x02    /* Choose between short and long (12x) wait times via TCS34725_WTIME */

#define TCS34725_CONTROL          0x0F    /* Set the gain level for the sensor */
#define TCS34725_ID               0x12    /* 0x44 = TCS34721/TCS34725, 0x4D = TCS34723/TCS34727 */

#define TCS34725_STATUS           0x13
#define TCS34725_STATUS_AINT      0x10    /* RGBC Clean channel interrupt */
#define TCS34725_STATUS_AVALID    0x01    /* Indicates that the RGBC channels have completed an integration cycle */

#define TCS34725_CDATAL           0x14    /* Clear channel data */
#define TCS34725_CDATAH           0x15
#define TCS34725_RDATAL           0x16    /* Red channel data */
#define TCS34725_RDATAH           0x17
#define TCS34725_GDATAL           0x18    /* Green channel data */
#define TCS34725_GDATAH           0x19
#define TCS34725_BDATAL           0x1A    /* Blue channel data */
#define TCS34725_BDATAH           0x1B

/**
* Offset and Compensated
**/
#define TCS34725_R_Coef 0.136 
#define TCS34725_G_Coef 1.000
#define TCS34725_B_Coef -0.444
#define TCS34725_GA 1.0
#define TCS34725_DF 310.0
#define TCS34725_CT_Coef 3810.0
#define TCS34725_CT_Offset 1391.0

/**
* Integration Time
**/
typedef enum
{
  TCS34725_INTEGRATIONTIME_2_4MS  = 0xFF,   /**<  2.4ms - 1 cycle    - Max Count: 1024  */
  TCS34725_INTEGRATIONTIME_24MS   = 0xF6,   /**<  24ms  - 10 cycles  - Max Count: 10240 */
  TCS34725_INTEGRATIONTIME_50MS   = 0xEB,   /**<  50ms  - 20 cycles  - Max Count: 20480 */
  TCS34725_INTEGRATIONTIME_101MS  = 0xD5,   /**<  101ms - 42 cycles  - Max Count: 43008 */
  TCS34725_INTEGRATIONTIME_154MS  = 0xC0,   /**<  154ms - 64 cycles  - Max Count: 65535 */
  TCS34725_INTEGRATIONTIME_700MS  = 0x00    /**<  700ms - 256 cycles - Max Count: 65535 */
}
TCS34725IntegrationTime_t;

/**
* Gain
**/
typedef enum
{
  TCS34725_GAIN_1X                = 0x00,   /**<  No gain  */
  TCS34725_GAIN_4X                = 0x01,   /**<  4x gain  */
  TCS34725_GAIN_16X               = 0x02,   /**<  16x gain */
  TCS34725_GAIN_60X               = 0x03    /**<  60x gain */
}
TCS34725Gain_t;


typedef struct{
   UWORD R;
   UWORD G;
   UWORD B;
   UWORD C;
}RGB;

/*-----------------------------------------------------------------------------*/
//initialization
UBYTE TCS34725_Init(void);
void TCS34725_SetLight(UWORD value);
void TCS34725_Set_Gain(TCS34725Gain_t gain);
void TCS34725_Set_IntegrationTime(TCS34725IntegrationTime_t it);
// void TCS34725_Set_Config(TCS34725Gain_t gain, TCS34725IntegrationTime_t it);

//Read Color
RGB TCS34725_Get_RGBData(void);
UWORD TCS34725_Get_ColorTemp(RGB rgb);
UWORD TCS34725_GetRGB565(RGB rgb);
UDOUBLE TCS34725_GetRGB888(RGB rgb);


//Read Light
UWORD TCS34725_Get_Lux(RGB rgb);
UBYTE TCS34725_GetLux_Interrupt(UWORD Threshold_H, UWORD Threshold_L);

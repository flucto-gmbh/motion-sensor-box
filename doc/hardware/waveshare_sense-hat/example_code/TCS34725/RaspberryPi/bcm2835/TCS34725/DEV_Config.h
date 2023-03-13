/*****************************************************************************
* | File      	:   DEV_Config.h
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2018-11-22
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
#
******************************************************************************/
#ifndef _DEV_CONFIG_H_
#define _DEV_CONFIG_H_

#include <termio.h>
#include <stdio.h>
#include <bcm2835.h>
#include <math.h>

#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t
/**
* GPIO 
**/
#define PWM_PIN 18
#define INT_PIN 17

/**
 * GPIO read and write
**/
#define DEV_Digital_Write(_pin, _value)  bcm2835_gpio_write(_pin, _value == 0? LOW:HIGH)
#define DEV_Digital_Read(_pin) 			 bcm2835_gpio_lev(_pin)

/**
* IIC 
**/
#define IIC_Addr					    0x29

/**
 * delay x ms
**/
#define DEV_Delay_ms(__xms)   bcm2835_delay(__xms)

/**
 * PWM
**/
#define DEV_Set_PWM(_Value)     bcm2835_pwm_set_data( 0, _Value)
#define DEV_PWM_value           1000

/*-----------------------------------------------------------------------------*/
void DEV_Set_I2CAddress(UBYTE Add);
void DEV_I2C_WriteByte(UBYTE add_, UBYTE data_);
void DEV_I2C_WriteWord(UBYTE add_, UWORD data_);
UBYTE DEV_I2C_ReadByte(UBYTE add_);
UWORD DEV_I2C_ReadWord(UBYTE add_);

UBYTE DEV_ModuleInit(void);
void DEV_ModuleExit(void);

#endif
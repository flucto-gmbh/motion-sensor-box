/*****************************************************************************
* | File      	:   DEV_Config.c
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
#include "DEV_Config.h"



/******************************************************************************
function:   Set the I2C device address
parameter	:
        Add : Device address
******************************************************************************/
void DEV_Set_I2CAddress(UBYTE Add)
{
    bcm2835_i2c_setSlaveAddress(Add);   
}
/******************************************************************************
function:	
	I2C Write and Read
******************************************************************************/
void DEV_I2C_WriteByte(UBYTE add_, UBYTE data_)
{
	char Buf[2] = {0, 0};
	Buf[0] = add_;
	Buf[1] = data_;
	bcm2835_i2c_write(Buf, 2); 
}

void DEV_I2C_WriteWord(UBYTE add_, UWORD data_)
{
	char Buf[2] = {0, 0};
	Buf[0] = add_;
	Buf[1] = data_ >> 8;
    Buf[2] = data_ & 0xff;
	bcm2835_i2c_write(Buf, 3);
}


UBYTE DEV_I2C_ReadByte(UBYTE add_)
{
	char Buf[1]={add_};
	bcm2835_i2c_write(Buf, 1);
	bcm2835_i2c_read(Buf, 1);
	return Buf[0];
}

UWORD DEV_I2C_ReadWord(UBYTE add_)
{
    char Buf[2]={add_, 0};
    bcm2835_i2c_write(Buf, 1);
    bcm2835_i2c_read(Buf, 2);
    return ((Buf[1] << 8) | (Buf[0] & 0xff));
}

/******************************************************************************
function:	
	Module initialization, I2C protocol
******************************************************************************/
UBYTE DEV_ModuleInit(void)
{
	if (!bcm2835_init()){
		printf("bcm2835 init failed  !!! \r\n");
		return 1;
	}else {
        printf("bcm2835 init success !!! \r\n");
	}
    //GPIO Config
    bcm2835_gpio_fsel(INT_PIN, BCM2835_GPIO_FSEL_INPT);
    //Since the output pin is an open drain output
	bcm2835_gpio_set_pud(INT_PIN, BCM2835_GPIO_PUD_UP);//Pull up input
    
	//I2C Config
    bcm2835_i2c_begin();
	bcm2835_i2c_setSlaveAddress(IIC_Addr);  //i2c address
	bcm2835_i2c_set_baudrate(10000);    //10K baudrate 10000
	bcm2835_i2c_setClockDivider(BCM2835_I2C_CLOCK_DIVIDER_626);
    //PWM
	bcm2835_gpio_fsel(PWM_PIN, BCM2835_GPIO_FSEL_ALT5);
	bcm2835_pwm_set_clock(BCM2835_PWM_CLOCK_DIVIDER_16);
	bcm2835_pwm_set_mode(0,1,1);
	bcm2835_pwm_set_range(0, DEV_PWM_value);
	
	return 0;
}

/******************************************************************************
function:	
	Module exits, closes I2C
******************************************************************************/
void DEV_ModuleExit(void)
{
    bcm2835_i2c_end();
    bcm2835_close();
}


/************************************************/

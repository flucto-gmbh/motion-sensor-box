/*****************************************************************************
* | File        :   SC16IS752GPIO.h
* | Author      :   Waveshare team
* | Function    :   Drive SC16IS752 GPIO
* | Info        :
*                The SC16IS752/SC16IS762 is an I2C-bus/SPI bus interface to 
*                a dual-channel high performance UART offering data rates up 
*                to 5 Mbit/s, low operating and sleeping current;it provides 
*                the application with 8 additional programmable I/O pins. 
*----------------
* |	This version:   V1.0
* | Date        :   2018-09-28
* | Info        :   Basic version
*
******************************************************************************/
#ifndef __SC16IS752GPIO_
#define __SC16IS752GPIO_

#define IN  0
#define OUT 1

#define LOW  0
#define HIGH 1

#define NUM_MAXBUF  4
#define DIR_MAXSIZ  60

#define PIN0    496

void SC16IS752GPIO_Init(void);
void SC16IS752GPIO_Exit(void);
void SC16IS752GPIO_Mode(int Pin, int Mode);
int SC16IS752GPIO_Read(int pin);
int SC16IS752GPIO_Write(int pin, int value);

#endif
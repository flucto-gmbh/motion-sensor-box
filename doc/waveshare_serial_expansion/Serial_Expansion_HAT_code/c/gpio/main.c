/*****************************************************************************
* | File        :   MotorDriver.h
* | Author      :   Waveshare team
* | Function    :   Drive TB6612FNG
* | Info        :
*                TB6612FNG is a driver IC for DC motor with output transistor in
*                LD MOS structure with low ON-resistor. Two input signals, IN1
*                and IN2, can choose one of four modes such as CW, CCW, short
*                brake, and stop mode.
*----------------
* |	This version:   V1.0
* | Date        :   2018-09-04
* | Info        :   Basic version
*
******************************************************************************/
#include "SC16IS752GPIO.h"
#include <stdlib.h>     //exit()
#include <stdio.h>      //printf()
#include <signal.h>
#include <wiringPi.h>

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:GPIO Stop\r\n");
    SC16IS752GPIO_Exit();

    exit(0);
}

int main(int argc, char *argv[])
{
    // int i = 0;

    SC16IS752GPIO_Init();
    SC16IS752GPIO_Mode(0, OUT);
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    for(;;) {
        SC16IS752GPIO_Write(0, 1);
        delay(1000);
        SC16IS752GPIO_Write(0, 0);
        delay(1000);
    }
    SC16IS752GPIO_Exit();
    return 0;
}
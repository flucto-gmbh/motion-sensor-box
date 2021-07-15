#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <math.h>
#include "LPS22HB.h"
int fd;
char I2C_readByte(int reg)
{
	return wiringPiI2CReadReg8(fd, reg);
}

unsigned short I2C_readU16(int reg)
{
	return wiringPiI2CReadReg16(fd, reg);
}
void I2C_writeByte(int reg, int val)
{
	wiringPiI2CWriteReg8(fd, reg, val);
}
void LPS22HB_RESET()
{   unsigned char Buf;
    Buf=I2C_readU16(LPS_CTRL_REG2);
    Buf|=0x04;                                         
    I2C_writeByte(LPS_CTRL_REG2,Buf);                  //SWRESET Set 1
    while(Buf)
    {
        Buf=I2C_readU16(LPS_CTRL_REG2);
        Buf&=0x04;
    }
}
void LPS22HB_START_ONESHOT()
{
    unsigned char Buf;
    Buf=I2C_readU16(LPS_CTRL_REG2);
    Buf|=0x01;                                         //ONE_SHOT Set 1
    I2C_writeByte(LPS_CTRL_REG2,Buf);
}
unsigned char LPS22HB_INIT()
{
    fd=wiringPiI2CSetup(LPS22HB_I2C_ADDRESS);
    if(I2C_readByte(LPS_WHO_AM_I)!=LPS_ID) return 0;    //Check device ID 
    LPS22HB_RESET();                                    //Wait for reset to complete
    I2C_writeByte(LPS_CTRL_REG1 ,   0x02);              //Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0 
    return 1;
}

int main()
{   float PRESS_DATA=0;
    float TEMP_DATA=0;
    unsigned char u8Buf[3];
    if (wiringPiSetup() < 0) return 1;
    printf("\nPressure Sensor Test Program ...\n");
    if(!LPS22HB_INIT())
    {
        printf("\nPressure Sensor Error\n");
        return 0;
    }
    printf("\nPressure Sensor OK\n");
    while(1)
    {
        LPS22HB_START_ONESHOT();        //Trigger one shot data acquisition
        if((I2C_readByte(LPS_STATUS)&0x01)==0x01)   //a new pressure data is generated
        {
            u8Buf[0]=I2C_readByte(LPS_PRESS_OUT_XL);
            u8Buf[1]=I2C_readByte(LPS_PRESS_OUT_L);
            u8Buf[2]=I2C_readByte(LPS_PRESS_OUT_H);
            PRESS_DATA=(float)((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0f;
        }
        if((I2C_readByte(LPS_STATUS)&0x02)==0x02)   // a new pressure data is generated
        {
            u8Buf[0]=I2C_readByte(LPS_TEMP_OUT_L);
            u8Buf[1]=I2C_readByte(LPS_TEMP_OUT_H);
            TEMP_DATA=(float)((u8Buf[1]<<8)+u8Buf[0])/100.0f;
        }
        
       printf("Pressure = %6.2f hPa , Temperature = %6.2f °C\r\n", PRESS_DATA, TEMP_DATA);
    }
    return 0;
}
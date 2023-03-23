#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdio.h>
#include <math.h>
#include"AD.h"
int Config_Set;
int fd; 
int I2C_readU16(int reg)
{   int val;
    unsigned char Val_L,Val_H;
    val=wiringPiI2CReadReg16(fd,reg);                    //High and low bytes are the opposite       
    Val_H=val&0xff;
    Val_L=val>>8;
    val=(Val_H<<8)|Val_L;                               //Correct byte order
    return val;
}
void I2C_writeWord(int reg, int val)
{   unsigned char Val_L,Val_H;
    Val_H=val&0xff;
    Val_L=val>>8;
    val=(Val_H<<8)|Val_L;                               ////Correct byte order
	wiringPiI2CWriteReg16(fd,reg,val);
}
unsigned int ADS1015_INIT()
{   unsigned int state;
    state=I2C_readU16(ADS_POINTER_CONFIG) & 0x8000  ;
    return state;
}
unsigned int ADS1015_SINGLE_READ(unsigned int channel)           //Read single channel data
{   unsigned int data;
    Config_Set = ADS_CONFIG_MODE_NOCONTINUOUS        |   //mode：Single-shot mode or power-down state    (default)
                 ADS_CONFIG_PGA_4096                 |   //Gain= +/- 4.096V                              (default)
                 ADS_CONFIG_COMP_QUE_NON             |   //Disable comparator                            (default)
                 ADS_CONFIG_COMP_NONLAT              |   //Nonlatching comparator                        (default)
                 ADS_CONFIG_COMP_POL_LOW             |   //Comparator polarity：Active low               (default)
                 ADS_CONFIG_COMP_MODE_TRADITIONAL    |   //Traditional comparator                        (default)
                 ADS_CONFIG_DR_RATE_1600             ;   //Data rate=1600SPS                             (default)
    switch (channel)
    {
        case (0):
            Config_Set |= ADS_CONFIG_MUX_SINGLE_0;
            break;
        case (1):
            Config_Set |= ADS_CONFIG_MUX_SINGLE_1;
            break;
        case (2):
            Config_Set |= ADS_CONFIG_MUX_SINGLE_2;
            break;
        case (3):
            Config_Set |= ADS_CONFIG_MUX_SINGLE_3;
            break;
    }
    Config_Set |=ADS_CONFIG_OS_SINGLE_CONVERT;
    I2C_writeWord(ADS_POINTER_CONFIG,Config_Set);
    delay(2);
    data=I2C_readU16(ADS_POINTER_CONVERT)>>4;
    return data;
}
int main()
{
	int  AIN0_DATA,AIN1_DATA,AIN2_DATA,AIN3_DATA;
    wiringPiSetup();
    fd=wiringPiI2CSetup(ADS_I2C_ADDRESS);
	printf("\nADS1015 Test Program ...\n");
    if(ADS1015_INIT()!=0x8000)
	{	printf("\nADS1015 Error\n");
		return 0;
	}
	delay(10);
	printf("\nADS1015 OK\n");
    while(1)
    {
        AIN0_DATA=ADS1015_SINGLE_READ(0);
        AIN1_DATA=ADS1015_SINGLE_READ(1);
        AIN2_DATA=ADS1015_SINGLE_READ(2);
        AIN3_DATA=ADS1015_SINGLE_READ(3);
        printf("\nAIN0 = %d(%dmv) ,AIN1 = %d(%dmv) ,AIN2 = %d(%dmv) AIN3 = %d(%dmv)\n\r", AIN0_DATA,AIN0_DATA*2, AIN1_DATA,AIN1_DATA*2,AIN2_DATA,AIN2_DATA*2,AIN3_DATA,AIN3_DATA*2);
        delay(500);
    }
    return 1;
}
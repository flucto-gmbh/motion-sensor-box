#include <bcm2835.h>
#include <stdio.h>
#include <math.h>
#include"AD.h"
uint16_t Config_Set; 
uint16_t I2C_readU16(char reg)
{
	char buf[] = { reg,0 };
	bcm2835_i2c_read_register_rs(buf, buf, 2);
	int value = buf[0] * 0x100 + buf[1];
	return value;
}
void I2C_writeWord(char reg, uint16_t val)
{
	char buf[] = { reg,val>>8,val};
	bcm2835_i2c_write(buf, 3);
}
uint16_t ADS1015_INIT()
{   uint16_t state;
    bcm2835_i2c_begin();
	bcm2835_i2c_setSlaveAddress(ADS_I2C_ADDRESS);
	bcm2835_i2c_set_baudrate(10000);
    state=I2C_readU16(ADS_POINTER_CONFIG) & 0x8000  ;
    return state;
}
uint16_t ADS1015_SINGLE_READ(uint8_t channel)           //Read single channel data
{   uint16_t data;
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
    bcm2835_delay(2);
    data=I2C_readU16(ADS_POINTER_CONVERT)>>4;
    return data;
}
int main()
{
	int16_t  AIN0_DATA,AIN1_DATA,AIN2_DATA,AIN3_DATA;
	printf("\nADS1015 Test Program ...\n");
	if (!bcm2835_init()) return 1;
    if(ADS1015_INIT()!=0x8000)
	{	printf("\nADS1015 Error\n");
		return 0;
	}
	bcm2835_delay(10);
	printf("\nADS1015 OK\n");
    while(1)
    {   
      
        AIN0_DATA=ADS1015_SINGLE_READ(0);
        AIN1_DATA=ADS1015_SINGLE_READ(1);
        AIN2_DATA=ADS1015_SINGLE_READ(2);
        AIN3_DATA=ADS1015_SINGLE_READ(3);
        printf("\nAIN0 = %d(%dmv) ,AIN1 = %d(%dmv) ,AIN2 = %d(%dmv) AIN3 = %d(%dmv)\n\r", AIN0_DATA,AIN0_DATA*2, AIN1_DATA,AIN1_DATA*2,AIN2_DATA,AIN2_DATA*2,AIN3_DATA,AIN3_DATA*2);
        bcm2835_delay(500);
    }
    return 1;
}
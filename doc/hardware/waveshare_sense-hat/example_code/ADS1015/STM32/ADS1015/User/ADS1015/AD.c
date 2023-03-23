#include "AD.h"
#include "DEV_Config.h"
unsigned int Config_Set; 
unsigned short ADS1015_INIT(void)
{   
	unsigned int state;
  state=DEV_I2C_ReadWord(ADS_POINTER_CONFIG) & 0x8000  ;
  return state;
}
unsigned int ADS1015_SINGLE_READ(unsigned char channel)           //Read single channel data
{   unsigned int data;
		Config_Set = ADS_CONFIG_MODE_NOCONTINUOUS        |   //mode:Single-shot mode or power-down state    (default)
                 ADS_CONFIG_PGA_4096                 |   //Gain= +/- 4.096V                              (default)
                 ADS_CONFIG_COMP_QUE_NON             |   //Disable comparator                            (default)
                 ADS_CONFIG_COMP_NONLAT              |   //Nonlatching comparator                        (default)
                 ADS_CONFIG_COMP_POL_LOW             |   //Comparator polarity:Active low               (default)
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
    DEV_I2C_WriteWord(ADS_POINTER_CONFIG,Config_Set);
     DEV_Delay_ms(2);
    data=DEV_I2C_ReadWord(ADS_POINTER_CONVERT)>>4;
    return data;
}

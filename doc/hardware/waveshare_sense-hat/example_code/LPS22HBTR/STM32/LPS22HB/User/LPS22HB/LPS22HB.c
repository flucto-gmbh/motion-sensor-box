#include "DEV_Config.h"
#include "LPS22HB.h"
void LPS22HB_RESET(void)
{   unsigned char Buf;
    Buf=DEV_I2C_ReadWord(LPS_CTRL_REG2);
    Buf|=0x04;                                         
    DEV_I2C_WriteByte(LPS_CTRL_REG2,Buf);                  //SWRESET Set 1
    while(Buf)
    {
        Buf=DEV_I2C_ReadWord(LPS_CTRL_REG2);
        Buf&=0x04;
    }
}
void LPS22HB_START_ONESHOT(void)
{
    unsigned char Buf;
    Buf=DEV_I2C_ReadWord(LPS_CTRL_REG2);
    Buf|=0x01;                                         //ONE_SHOT Set 1
    DEV_I2C_WriteByte(LPS_CTRL_REG2,Buf);
}
unsigned char LPS22HB_INIT(void)
{
    if(DEV_I2C_ReadByte(LPS_WHO_AM_I)!=LPS_ID) return 0;    //Check device ID 
    LPS22HB_RESET();                                    //Wait for reset to complete
    DEV_I2C_WriteByte(LPS_CTRL_REG1 ,   0x02);              //Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0 
    return 1;
}

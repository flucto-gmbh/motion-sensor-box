#include <bcm2835.h>
#include <stdio.h>
#include <math.h>
#include"SHTC3.h"
float TH_Value,RH_Value;
char checksum;
char SHTC3_CheckCrc(char data[],uint8_t len,uint8_t checksum)
{
  uint8_t bit;        // bit mask
  uint8_t crc = 0xFF; // calculated checksum
  uint8_t byteCtr;    // byte counter
  // calculates 8-Bit checksum with given polynomial
  for(byteCtr = 0; byteCtr < len; byteCtr++) {
    crc ^= (data[byteCtr]);
    for(bit = 8; bit > 0; --bit) {
      if(crc & 0x80) {
        crc = (crc << 1) ^ CRC_POLYNOMIAL;
      } else {
        crc = (crc << 1);
      }
    }
  }

  // verify checksum
  if(crc != checksum) {                 
    return 1;                       //Error
  } else {
    return 0;                       //No error
  }       
}

uint8_t SHTC3_WriteCommand(unsigned short cmd)
{   uint8_t state;
    char buf[] = { (cmd>>8) ,cmd};
    state=bcm2835_i2c_write(buf, 2);           
    return state;                                             //1:error 0:No error
}
uint8_t SHTC3_WAKEUP()
{   uint8_t state;  
    state=!bcm2835_i2c_begin();
    state|=SHTC3_WriteCommand(SHTC3_WakeUp);                  // write wake_up command  
    bcm2835_delayMicroseconds(300);                          //Delay 300us
    bcm2835_i2c_end();
    return state;  
}
uint8_t SHTC3_SLEEP()
{   uint8_t state; 
    state=!bcm2835_i2c_begin();
    state|=SHTC3_WriteCommand(SHTC3_Sleep);                        // Write sleep command
    bcm2835_i2c_end();
    return state;  
}

uint8_t SHTC_SOFT_RESET()
{   uint8_t state;
    state=!bcm2835_i2c_begin();
    state|=SHTC3_WriteCommand(SHTC3_Software_RES);                 // Write reset command
    bcm2835_delayMicroseconds(300);                                 //Delay 300us
    bcm2835_i2c_end();
    return state; 
}
uint8_t SHTC3_Read_DATA()
{   uint8_t state;
    unsigned short TH_DATA,RH_DATA;
    char buf[3];
    state=!bcm2835_i2c_begin();
    state|=SHTC3_WriteCommand(SHTC3_NM_CD_ReadTH);                 //Read temperature first,clock streching disabled (polling)
    bcm2835_delay(20);
    
  	state|=bcm2835_i2c_read(buf,3);
    checksum=buf[2];
    state|=SHTC3_CheckCrc(buf,2,checksum);
    if(!state)
    TH_DATA=(buf[0]<<8|buf[1]);

    state|=SHTC3_WriteCommand(SHTC3_NM_CD_ReadRH);                 //Read temperature first,clock streching disabled (polling)
    bcm2835_delay(20);
    
    state|=bcm2835_i2c_read(buf,3);
    checksum=buf[2];
    state|=SHTC3_CheckCrc(buf,2,checksum);
    if(!state)
    RH_DATA=(buf[0]<<8|buf[1]);

    if(!state)
    { 
      TH_Value=175 * (float)TH_DATA / 65536.0f - 45.0f;       //Calculate temperature value
      RH_Value=100 * (float)RH_DATA / 65536.0f;              //Calculate humidity value
    }
    else
    {
      printf("\n SHTC3 Sensor Error\n");
    } 
    bcm2835_i2c_end();
    return state;
}

int main()
{   uint8_t state;
    printf("\n SHTC3 Sensor Test Program ...\n");
    if (!bcm2835_init()) return 1;
	  bcm2835_i2c_setSlaveAddress(SHTC3_I2C_ADDRESS);
	  bcm2835_i2c_set_baudrate(10000);
    SHTC_SOFT_RESET();
    while (1)
    {
        state=SHTC3_Read_DATA();
        state|=SHTC3_SLEEP();
        state|=SHTC3_WAKEUP();
        if(state)
        printf("\n SHTC3 Sensor Error\n");
        else
	    	printf("Temperature = %6.2f°C , Humidity = %6.2f%% \r\n", TH_Value, RH_Value);
    }
    return 0;
}
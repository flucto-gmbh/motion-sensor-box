#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <math.h>
#include"SHTC3.h"
#include <unistd.h>
float TH_Value,RH_Value;
char checksum;
int fd;
char SDA = 8;
char SCL = 9;
char SHTC3_CheckCrc(char data[],unsigned char len,unsigned char checksum)
{
  unsigned char bit;        // bit mask
  unsigned char crc = 0xFF; // calculated checksum
  unsigned char byteCtr;    // byte counter
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
void SHTC3_WriteCommand(unsigned short cmd)
{   
    char buf[] = { (cmd>>8) ,cmd};
    wiringPiI2CWriteReg8(fd,buf[0],buf[1]);          
                                                 //1:error 0:No error
}
void SHTC3_WAKEUP()
{     
    SHTC3_WriteCommand(SHTC3_WakeUp);                  // write wake_up command  
    delayMicroseconds(300);                          //Delay 300us
      
}
void SHTC3_SLEEP()
{    
 //   bcm2835_i2c_begin();
    SHTC3_WriteCommand(SHTC3_Sleep);                        // Write sleep command
      
}

void SHTC_SOFT_RESET()
{   
    SHTC3_WriteCommand(SHTC3_Software_RES);                 // Write reset command
    delayMicroseconds(300);                                 //Delay 300us
     
}

void SHTC3_Read_DATA()
{   
    unsigned short TH_DATA,RH_DATA;
    char buf[3];
   SHTC3_WriteCommand(SHTC3_NM_CD_ReadTH);                 //Read temperature first,clock streching disabled (polling)
    delay(20);
    read(fd, buf, 3);

   checksum=buf[2];
   if(!SHTC3_CheckCrc(buf,2,checksum))
        TH_DATA=(buf[0]<<8|buf[1]);
    
    SHTC3_WriteCommand(SHTC3_NM_CD_ReadRH);                 //Read temperature first,clock streching disabled (polling)
    delay(20);
    read(fd, buf, 3);

    checksum=buf[2];
    if(!SHTC3_CheckCrc(buf,2,checksum))
        RH_DATA=(buf[0]<<8|buf[1]);
    
    TH_Value=175 * (float)TH_DATA / 65536.0f - 45.0f;       //Calculate temperature value
    RH_Value=100 * (float)RH_DATA / 65536.0f;              //Calculate humidity value  
    
}

int main()
{   
    printf("\n SHTC3 Sensor Test Program ...\n");
    if (wiringPiSetup() < 0) return 1;
    fd=wiringPiI2CSetup(SHTC3_I2C_ADDRESS);
    SHTC_SOFT_RESET();
    while (1)
    {
        SHTC3_Read_DATA();
        SHTC3_SLEEP();
        SHTC3_WAKEUP();

	    printf("Temperature = %6.2f°C , Humidity = %6.2f%% \r\n", TH_Value, RH_Value);
    }
    return 0;
}
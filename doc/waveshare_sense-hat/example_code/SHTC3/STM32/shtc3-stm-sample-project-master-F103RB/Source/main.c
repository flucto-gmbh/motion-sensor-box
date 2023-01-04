//This code is modified based on the official SENSIRION code.
//For application with STM32F103RB
#include "system.h"
#include "shtc3.h"
#include "stdbool.h"

static void LedInit(void);
static void Led3(bool on);
static void Led2(bool on);

//------------------------------------------------------------------------------
int main(void)
{
  etError  error;       // error code
  uint16_t id;          // sensor ID
  float    temperature; // temperature
  float    humidity;    // relative humidity

  SystemInit();
  LedInit();

  // initalize sensor module with the i2c address 0x70
  SHTC3_Init(0x70);

  // demonstartion of SoftReset command
  error = SHTC3_SoftReset();

  // demonstartion of GetId command
  error = SHTC3_GetId(&id);

  while(1) {
    // read temperature and relative humidity
    error = SHTC3_GetTempAndHumiPolling(&temperature, &humidity);

    // if no error occurs -> the green LED lights up
    Led2(error == NO_ERROR);

    // if the Relative Humidity is over 50% -> the blue LED lights up
    Led3(humidity > 80);

    // activate the sleep mode of the sensor to save energy
    SHTC3_Sleep();
    // wait 1 second
    DelayMicroSeconds(1000000);
    // wake up the sensor from sleep mode
    SHTC3_Wakeup();
  }
}

//------------------------------------------------------------------------------
static void LedInit(void)          /* -- adapt this code for your platform -- */
{
  RCC->APB2ENR |= 0x00000010;  // I/O port C clock enabled
  GPIOC->CRH   &= 0xFFFFFF00;  // set general purpose output mode for LEDs
  GPIOC->CRH   |= 0x00000011;  //
  GPIOC->BSRR   = 0x03000000;  // LEDs off
}

//------------------------------------------------------------------------------
static void Led3(bool on)       /* -- adapt this code for your platform -- */
{
  if(on) {
    GPIOC->BSRR = 0x00000100;
  } else {
    GPIOC->BSRR = 0x01000000;
  }
}

//------------------------------------------------------------------------------
static void Led2(bool on)      /* -- adapt this code for your platform -- */
{
  if(on) {
    GPIOC->BSRR = 0x00000200;
  } else {
    GPIOC->BSRR = 0x02000000;
  }
}

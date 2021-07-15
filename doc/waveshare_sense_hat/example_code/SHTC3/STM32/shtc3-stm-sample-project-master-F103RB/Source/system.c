
#include "system.h"

//------------------------------------------------------------------------------
void SystemInit(void){
}

//------------------------------------------------------------------------------
void DelayMicroSeconds(uint32_t nbrOfUs)  /* - adapt this delay for your uC - */
{
  for(uint32_t i = 0; i < nbrOfUs; i++) {
    __nop();  // nop's may be added or removed for timing adjustment
    __nop();
    __nop();
    __nop();
  }
}

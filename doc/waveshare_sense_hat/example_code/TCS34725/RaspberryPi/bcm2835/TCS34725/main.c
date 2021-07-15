#include <stdio.h>      //printf()
#include <stdlib.h>     //exit()
#include <signal.h>

#include "DEV_Config.h"
#include "TCS34725.h"

UWORD r,g,b,c;
UWORD cpl,lux,k;

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:Program stop\r\n");     
    DEV_ModuleExit();
    exit(0);
}

int main(int argc, char **argv)
{
    RGB rgb;
    UDOUBLE RGB888=0;
    UWORD   RGB565=0;
	if (DEV_ModuleInit() != 0){
        exit(0);
    }
    
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    
    if(TCS34725_Init() != 0){
        printf("TCS34725 initialization error!!\r\n");
        exit(0);
    } 
    printf("TCS34725 initialization success!!\r\n");
    
    TCS34725_SetLight(60);
    // DEV_Delay_ms(2000);
    
    while(1){    
        rgb=TCS34725_Get_RGBData();
        RGB888=TCS34725_GetRGB888(rgb);
        RGB565=TCS34725_GetRGB565(rgb);
        printf(" RGB888 :R=%d   G=%d  B=%d   RGB888=0X%X  RGB565=0X%X  ", (RGB888>>16), \
                (RGB888>>8) & 0xff, (RGB888) & 0xff, RGB888, RGB565);
                
        if(TCS34725_GetLux_Interrupt(0xff00, 0x00ff) == 1){
            printf("Lux_Interrupt = 1\r\n");
        }else{
            printf("Lux_Interrupt = 0\r\n");
        }
     

        
	}

	DEV_ModuleExit();
    return 0; 
}
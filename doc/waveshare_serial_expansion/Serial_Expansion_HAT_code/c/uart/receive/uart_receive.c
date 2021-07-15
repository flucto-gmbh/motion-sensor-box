#include <wiringSerial.h>
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>     //exit()
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>
#include <sys/time.h>


#define UART_DEV1    "/dev/ttySC0"
#define UART_DEV2    "/dev/ttySC1"

int fd;

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:serialClose \r\n");
    serialClose(fd);

    exit(0);
}

int main(void)
{
    if((fd = serialOpen (UART_DEV2, 115200)) < 0) {
        printf("serial err\n");
        return -1;
    }
    printf("This is a test ascii program, receive(get '~' is over)\r\n");

    char str;
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    for (;;) {
        str = serialGetchar (fd);
        //putchar(str) ;
        printf("%c", str);
        fflush (stdout) ;

        if(str == '~'){
            printf("\r\n");
            break;
        }
    }

    return 0;
}

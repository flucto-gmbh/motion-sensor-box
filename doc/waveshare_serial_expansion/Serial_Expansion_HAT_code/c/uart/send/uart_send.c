#include <wiringSerial.h>
#include <wiringPi.h>
#include <stdio.h>
#include <strings.h>
#include <unistd.h>

#define UART_DEV1 "/dev/ttySC0"
#define UART_DEV2 "/dev/ttySC1"

int main(void)
{
    int fd;
    if ((fd = serialOpen(UART_DEV1, 115200)) < 0)
    {
        printf("serial err\n");
        return -1;
    }
    printf("This is a test ascii program, send\r\n");

    char count;
    // char str[35];
    unsigned int nextTime;
    nextTime = millis() + 100;

    for (count = 33; count < 128; ){ //Visible characters
        if (millis() > nextTime){
            printf("%c", count);
            fflush(stdout);
            serialPutchar(fd, count);
            nextTime += 100;
            ++count;
        }

        // delay(3);
    }

    printf("\n");
    return 0;
}

#ifndef _AD_H
#define _AD_H

//i2c address
#define ADS_I2C_ADDRESS		              0x48

//Pointer Register
#define ADS_POINTER_CONVERT               0x00
#define ADS_POINTER_CONFIG                0x01
#define ADS_POINTER_LOWTHRESH             0x02  
#define ADS_POINTER_HIGHTHRESH            0x03

//Config Register
#define ADS_CONFIG_OS_BUSY                  0x0000      //Device is currently performing a conversion
#define ADS_CONFIG_OS_NOBUSY                0x8000      //Device is not currently performing a conversion              
#define ADS_CONFIG_OS_SINGLE_CONVERT        0x8000      //Start a single conversion (when in power-down state)  
#define ADS_CONFIG_OS_NO_EFFECT             0x0000      //No effect
#define ADS_CONFIG_MUX_MUL_0_1              0x0000      //Input multiplexer,AINP = AIN0 and AINN = AIN1(default)
#define ADS_CONFIG_MUX_MUL_0_3              0x1000      //Input multiplexer,AINP = AIN0 and AINN = AIN3
#define ADS_CONFIG_MUX_MUL_1_3              0x2000      //Input multiplexer,AINP = AIN1 and AINN = AIN3
#define ADS_CONFIG_MUX_MUL_2_3              0x3000      //Input multiplexer,AINP = AIN2 and AINN = AIN3
#define ADS_CONFIG_MUX_SINGLE_0             0x4000      //SINGLE,AIN0
#define ADS_CONFIG_MUX_SINGLE_1             0x5000      //SINGLE,AIN1
#define ADS_CONFIG_MUX_SINGLE_2             0x6000      //SINGLE,AIN2
#define ADS_CONFIG_MUX_SINGLE_3             0x7000      //SINGLE,AIN3
#define ADS_CONFIG_PGA_6144                 0x0000      //Gain= +/- 6.144V
#define ADS_CONFIG_PGA_4096                 0x0200      //Gain= +/- 4.096V
#define ADS_CONFIG_PGA_2048                 0x0400      //Gain= +/- 2.048V(default)
#define ADS_CONFIG_PGA_1024                 0x0600      //Gain= +/- 1.024V
#define ADS_CONFIG_PGA_512                  0x0800      //Gain= +/- 0.512V
#define ADS_CONFIG_PGA_256                  0x0A00      //Gain= +/- 0.256V
#define ADS_CONFIG_MODE_CONTINUOUS          0x0000      //Device operating mode:Continuous-conversion mode        
#define ADS_CONFIG_MODE_NOCONTINUOUS        0x0100      //Device operating mode：Single-shot mode or power-down state (default)
#define ADS_CONFIG_DR_RATE_128              0x0000      //Data rate=128SPS
#define ADS_CONFIG_DR_RATE_250              0x0020      //Data rate=250SPS
#define ADS_CONFIG_DR_RATE_490              0x0040      //Data rate=490SPS
#define ADS_CONFIG_DR_RATE_920              0x0060      //Data rate=920SPS
#define ADS_CONFIG_DR_RATE_1600             0x0080      //Data rate=1600SPS
#define ADS_CONFIG_DR_RATE_2400             0x00A0      //Data rate=2400SPS
#define ADS_CONFIG_DR_RATE_3300             0x00C0      //Data rate=3300SPS
#define ADS_CONFIG_COMP_MODE_WINDOW         0x0010      //Comparator mode：Window comparator
#define ADS_CONFIG_COMP_MODE_TRADITIONAL    0x0000      //Comparator mode：Traditional comparator (default)
#define ADS_CONFIG_COMP_POL_LOW             0x0000      //Comparator polarity：Active low (default)
#define ADS_CONFIG_COMP_POL_HIGH            0x0008      //Comparator polarity：Active high
#define ADS_CONFIG_COMP_LAT                 0x0004      //Latching comparator 
#define ADS_CONFIG_COMP_NONLAT              0x0000      //Nonlatching comparator (default)
#define ADS_CONFIG_COMP_QUE_ONE             0x0000      //Assert after one conversion
#define ADS_CONFIG_COMP_QUE_TWO             0x0001      //Assert after two conversions
#define ADS_CONFIG_COMP_QUE_FOUR            0x0002      //Assert after four conversions
#define ADS_CONFIG_COMP_QUE_NON             0x0003      //Disable comparator and set ALERT/RDY pin to high-impedance (default)

#endif

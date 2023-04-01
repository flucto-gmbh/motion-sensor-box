# Configuration Refactor Architecture

## Configuration Files

Primary configuration file for all generic configurations, such as
zeromq socket addresses and ports, motion sensor box serial number, etc
```bash
$MSB_CONF/msb/msb.yaml
```

`conf.d` subdirectory containing individual configuration files for
different services:

```bash
$MSB_CONF/msb/conf.d/imu.yaml
$MSB_CONF/msb/conf.d/gps.yaml
$MSB_CONF/msb/conf.d/fusionlog.yaml
$MSB_CONF/msb/conf.d/piletrack.yaml
$MSB_CONF/msb/conf.d/wifi.yaml
```



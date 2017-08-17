#include "mbed.h"
#include "BME280.h"

Serial pc(USBTX, USBRX);

//
// This program uses BME280 library for mbed.
// It's located at,
// https://developer.mbed.org/components/BME280-Combined-humidity-and-pressure-se/
//
// I2C address is taken from the Arduino library
// Arduino uses 7-bits for I2C addressing
// whereas mbed uses 8-bits. It's required to
// shift the address 0x77 one bit left in order
// to get it working with mbed.
//
// reference:
// https://developer.mbed.org/questions/4064/i2c-on-Nucleo-F401RE/
//
// arduino library:
// https://github.com/sparkfun/SparkFun_BME280_Arduino_Library
//
//

BME280 sensor(PB_9,   PB_8,     (0x77<<1));
//           (I2C_SDA, I2C_SCL, I2C_Address);
// change those pins with respect to your board

int main() {
    while(1) {
        pc.printf(
            "%2.2f degC, %04.2f hPa, %2.2f %%\n",
            sensor.getTemperature(),
            sensor.getPressure(),
            sensor.getHumidity());
        wait_ms(10);
    }
}


#!/usr/bin/env python3.2

import os, sys, time, datetime, atexit

time_between = 36
time_on      = 3

class GPIO_pin():
    ''' mapping of pin number, GPIO name, and bit number
    http://www.hobbytronics.co.uk/raspberry-pi-gpio-pinout
    
    pin 7       GPIO 4          0
    pin 11      GPIO 17         1
    pin 12      GPIO 18         2
    pin 13      GPIO 21         3
    pin 15      GPIO 22         4
    pin 16      GPIO 23         5
    pin 18      GPIO 24         6
    pin 22      GPIO 25         7
    '''


    bit2gpio  = {0:'4', 1:'17', 2:'18', 3:'21', 4:'22', 5:'23', 6:'24', 7:'25'}
    pin2bit   = {7:0, 11:1, 12:2, 13:3, 15:4, 16:5, 18:6, 22:7}
    gpio2bit  = {4:0, 17:1, 18:2, 21:3, 22:4, 23:5, 24:6, 25:7}
    
    
    def __init__(self, bit_id=None, pin_id=None, gpio_id=None, direction=None):
        '''
        bit_id is the IO ID as a 0-7 integer, we'll map it to a GPIO pin
        '''
        if not (bit_id or pin_id or gpio_id):
            raise ValueError('Please specify one of: bit_id, pin_id, or gpio_id, being an integer')
        
        if bit_id:
            if not isinstance(bit_id, int):
                raise TypeError('bit_id should be an integer, 0-7')
            if not 0 <= bit_id <= 7:
                raise ValueError('bit_id should be an integer, 0-7')
            self.bit_id = bit_id

        elif pin_id:
            if not isinstance(pin_id, int):
                raise TypeError('pin_id should be an integer')
            if not pin_id in self.pin2bit:
                raise ValueError('pin_id should be an integer in the set (7, 11, 12, 13, 15, 16, 18, 22)')
            self.bit_id = self.pin2gpio[pin_id]

        elif gpio_id:
            if not isinstance(gpio_id, int):
                raise TypeError('gpio_id should be an integer')
            if not gpio_id in self.gpio2bit:
                raise ValueError('gpio_id should be an integer in the set (4, 17, 18, 21, 22, 23, 24, 25)')
            self.bit_id = self.gpio2bit[gpio_id]

        print ('set bit_id to {!r}'.format(self.bit_id))
        self._enable_bit_id()   
        self._set_direction(direction)
        
    def _enable_bit_id(self):
        try:
            with open('/sys/class/gpio/export', 'w') as f:
                print('enabling GPIO# {}'.format(self.bit2gpio[self.bit_id]))
                f.write(self.bit2gpio[self.bit_id]+'\n')
        except:
            raise

    def _disable_bit_id(self):
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(self.bit2gpio[self.bit_id]+'\n')

    def _set_direction(self, direction=None):
        ''' out/False = output, in/True/None = input (default) '''
        
        path = '/sys/class/gpio/gpio{}/direction'.format(self.bit2gpio[self.bit_id])
        
        # wait a wee bit for the files to appear
        ctr = 0
        while True:
            if not os.path.exists(path):
                time.sleep(0.1)
                if ctr > 10:
                    raise Exception('i fucked up')
                ctr += 1
            else:
                break
        
        # force to True or False
        print ('setting direction')   
        direction = direction in ('in', True, None)
        
        direction = ('out', 'in')[direction]
        with open(path, 'w') as f:
            f.write(direction)
    
    def set(self, value):
        ''' set a binary off(0) or on(1) value '''
        if value.lower() in ('off', 'on'):
            value = {'off':'0', 'on':'1'}[value.lower()]
        elif value in (False, True):
            value = {False:'0', True:'1'}[value]
        elif isinstance(value, int):
            value = str(value)

        if not value in ('0', '1'):
            raise ValueError
        
        with open('/sys/class/gpio/gpio{}/value'.format(self.bit2gpio[self.bit_id]), 'w') as f:
            f.write(value)

    def get(self):
        with open('/sys/class/gpio/gpio{}/value'.format(self.bit2gpio[self.bit_id]), 'r') as f:
            return f.read() 


def cleanup():   
    print('unregistering GPIO')
    for key,pin in {0:'4', 1:'17', 2:'18', 3:'21', 4:'22', 5:'23', 6:'24', 7:'25'}.items():
        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(pin+'\n')
            print ('unregistered GPIO#: {}'.format(pin))
        except:
            pass
    print ('completed')
    

atexit.register(cleanup) 

if __name__ == '__main__':
    sprinkler = GPIO_pin(gpio_id=18, direction='out')     
    
    while True:
      print('spurting for: 0.1 sec')
      sprinkler.set('on')
      time.sleep(0.2)
      sprinkler.set('off')
      print('''engaging ♂ sleep mode''')
      time.sleep(300)
    
    print ('done')

#!/usr/bin/python3
# for android
# version 0.1.1 28-07-2022
import os

os.environ['KIVY_NO_FILELOG'] = '1'  # eliminate file log

import time
import math

import kivy                   
from kivy.config import Config
Config.set('kivy', 'log_level', 'error')
Config.write()

from usb4a import usb
from usbserial4a import serial4a

save=True  #save to file
path='./'  #path
midnight=False   #new file after midnight
dt=60         #time interval (seconds)
baudrate=115200   #com port baudrate

def mpsas2nelm(mpsas):
    if mpsas>18.3: nelm=7.93-5*math.log10(math.pow(10,4.316-(mpsas/5.))+1)    #Scotopic vision
    else: nelm=4.305-5*math.log10(math.pow(10,2.316-(mpsas/5.))+1)      #Photopic vision
    return nelm


def read1():
    '''read one data'''
    t0=time.time()
    com.write(b'rx\r')
    time.sleep(5)  #wait for completing measurements
    ans=com.readline().decode().strip()
    data=ans.split(',')     #r,-09.42m,0000005915Hz,0000000000c,0000000.000s, 027.0C -> r,mpsas,freq,period,per,temp
    #t=time.strftime('%Y_%m_%d %H:%M:%S',time.localtime(t0))
    t=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t0))      #for better import to excel
    mpsas=float(data[1][:-1])   #mpsas
    nelm=round(mpsas2nelm(mpsas),2) #nelm
    temp=float(data[-1][:-1])  #temperature in C
    
    print(t,mpsas,nelm,temp)
    
    if save:
        name=path+'sqm_'+time.strftime('%Y_%m_%d')+'.dat'
        #not create new file after midnight
        if time.localtime().tm_hour<12 and not midnight:
            if os.path.isfile(path+'sqm_'+time.strftime('%Y_%m_%d',time.localtime(time.time()-86400))+'.dat'):
                name=path+'sqm_'+time.strftime('%Y_%m_%d',time.localtime(time.time()-86400))+'.dat'
        if os.path.isfile(name): f=open(name,'a')
        else:
            f=open(name,'w')
            f.write('Date Time MPSAS NELM Temp(C)\n')
        f.write('%s %5.2f %5.2f %4.1f\n' %(t,mpsas,nelm,temp))
        f.close()
    return t0

def init():
    '''init serial COM port'''
    global com
    #com=serial.Serial(portVar.get())
    
    #com.baudrate=baudVar.get()
    usb_device_list = usb.get_usb_device_list()
    com = serial4a.get_serial_port(usb_device_list[0].getDeviceName(),baudrate,8,'N',1)   # Baudrate, Number of data bits(5, 6, 7 or 8), Parity('N', 'E', 'O', 'M' or 'S'), Number of stop bits(1, 1.5 or 2)
    time.sleep(1)

init()
while True:
    read1()
    time.sleep(dt)

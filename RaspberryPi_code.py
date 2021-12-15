import RPi.GPIO as GPIO                                                         #import the RPi.GPIO module to use the board GPIO pins
import pyrebase                                                                 #import the pyrebase module to communicate with the firebase
import time                                                                     #import the time modulde to add delays
import Adafruit_DHT                                                             #import DHT sensor libraries
from gpiozero import MotionSensor
from gpiozero import LED

config = {                                                                      #define dictionary named config with several key-value pairs that configure the connection to the firebase database
        "apiKey": "AIzaSyDwWRVMPeHzXoB4pYt_d2JipGyR6Qszlpg",
        "authDomain": "project-7700667.firebaseapp.com",
        "databaseURL": "https://project-7700667-default-rtdb.firebaseio.com",
        "storageBucket": "project-7700667.appspot.com"
}

firebase = pyrebase.initialize_app(config)                                      #initialize communication with the firebase database
#GPIO Setup  for GPIO numbering, choose BCM 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Lights Setup
light = LED(12)
lights = 12                                                                     #set GPIO pin 12 for lights
GPIO.setup(lights, GPIO.OUT)

#Temp & Humidity Sensory Setup
THsensor = Adafruit_DHT.DHT11
THpin = 27                                                                      #set GPIO pin 27 for TH sensor

#Motion Detector Setup
pir = 22
GPIO.setup(22,GPIO.IN)                #setup GPIO pin 22 for motion, Read output from PIR motion sensor

def initialize():
    # GPIO.output(lights, True)
    database = firebase.database()                                              #take an instance from the firebase database
    database.child("IoTSystem1").child("System").set("ON")                 #set all keys to off for initialization
    database.child("IoTSystem1").child("Lights").set("OFF")                 # ...
    database.child("IoTSystem1").child("TH").child("Temp").set("0.00")
    database.child("IoTSystem1").child("TH").child("Humid").set("0.00")
    database.child("IoTSystem1").child("Motion").set("OFF")
    
def lightFunc():
    database = firebase.database()                                         
    lightStatus = database.child("IoTSystem1").child("Lights").get().val()  #get status of lights
    if "on" in lightStatus.lower():                                            
        GPIO.output(lights, True)
    else:                                                                       #if value is on, turn LED on
        GPIO.output(lights, False)

def THFunc():
    database = firebase.database()
    humidity, temperature = Adafruit_DHT.read_retry(THsensor, THpin)            #get reading from TH sensor
    if (sysStatus == "ON" ): 
        str_temp = ' {0:0.2f}'.format(temperature)
        str_humid  = ' {0:0.2f}'.format(humidity)    
        database.child("IoTSystem1").child("TH").child("Temp").set(str_temp)    #send readings to firebase database
        database.child("IoTSystem1").child("TH").child("Humid").set(str_humid)  # ...
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        database.child("IoTSystem1").child("TH").child("Temp").set("0.00")
        database.child("IoTSystem1").child("TH").child("Humid").set("0.00")

def pirFunc():
    if GPIO.input(pir) == True:                                        #if motion pin goes high, motion is detected
        database.child("IoTSystem1").child("Motion").set("ON")
        print("Motion detected now...")
    else:
        database.child("IoTSystem1").child("Motion").set("OFF")
        print("no motion detected...")

try:
    initialize()
    database = firebase.database() 
    while(True):
        lightStatus = database.child("IoTSystem1").child("Lights").get().val()  #get status of lights
        sysStatus = database.child("IoTSystem1").child("System").get().val()    #get status of system
        print("system status...", sysStatus)
        print("light status...", lightStatus)
                                                   #if system on, monitor all components
        if "on" in sysStatus.lower():                                        #if system off, set all components to off
            pirFunc()
            THFunc()
            lightFunc()
       # elif "off" in sysStatus.lower():

        elif "on" in lightStatus.lower():                                        
            lightFunc()
        else:
            exit()
    #time.sleep(0.1)

except KeyboardInterrupt:                                                       #if CTRL+C is pressed, exit 
    initialize()
    GPIO.cleanup()                                                              #cleanup all GPIO
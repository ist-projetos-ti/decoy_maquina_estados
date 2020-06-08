import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
import time

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH) #Enable do motor de passo
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW) #Direção motor de passo
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) #PWM do motor de passo
#pwm=GPIO.PWM(12,500)     #Configura para 100 Hz
#pwm.start(50)            #Inicia com DC=0%

def gira_motor_horario(voltas):
    GPIO.output(16, GPIO.LOW) # Turn on enable
    GPIO.output(22, GPIO.HIGH) # Sentido
    for y in range(voltas):
        for x in range(405):
            GPIO.output(12, GPIO.LOW) # Turn on enable
            time.sleep(0.01) 
            GPIO.output(12, GPIO.HIGH) # Sentido
            time.sleep(0.01)
            x=x+1
        y=y+1
    GPIO.output(16, GPIO.HIGH) # Turn on enable

        
def gira_motor_anti_horario(voltas):
    GPIO.output(16, GPIO.LOW) # Turn on enable
    GPIO.output(22, GPIO.LOW) # Sentido
    for y in range(voltas):
        for x in range(405):
            GPIO.output(12, GPIO.LOW) # Turn on enable
            time.sleep(0.001) 
            GPIO.output(12, GPIO.HIGH) # Sentido
            time.sleep(0.001)
            x=x+1
        y=y+1
    GPIO.output(16, GPIO.HIGH) # Turn on enable
    
    
#gira_motor_horario(2)
#gira_motor_anti_horario(30)
#while True:

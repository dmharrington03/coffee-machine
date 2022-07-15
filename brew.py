import sched, time
import RPi.GPIO as GPIO

def startBrew(pin):
  GPIO.output(pin, GPIO.HIGH)


def stopBrew(pin):
  GPIO.output(pin, GPIO.LOW)
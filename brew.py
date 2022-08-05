import sched, time
import RPi.GPIO as GPIO

def startBrew(pin, secs):
  GPIO.output(pin, GPIO.HIGH)
  time.sleep(secs)
  GPIO.output(pin, GPIO.LOW)


def stopBrew(pin):
  GPIO.output(pin, GPIO.LOW)
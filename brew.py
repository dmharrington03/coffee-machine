import sched, time
# import RPi.GPIO as GPIO

def startBrew(pin: int, secs: int, stopFunc):
#   GPIO.output(pin, GPIO.HIGH)
    print("STARTING BREW - GPIO HIGH")
    for i in range(secs):
        if stopFunc():
            return
        time.sleep(1)
#   GPIO.output(pin, GPIO.LOW)
    print("STOPPING BREW - GPIO LOW")
    # pass


def stopBrew(pin):
#   GPIO.output(pin, GPIO.LOW)
    print("STOPPING BREW ON STOP - GPIO LOW")
    # pass
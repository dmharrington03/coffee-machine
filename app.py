from flask import Flask, render_template,  url_for, redirect, request
# from requests import request
from form import CoffeeForm
import sched, threading, time
from datetime import timedelta, datetime
# from gpiozero import OutputDevice
# import brew

pin = 18

# Initiate scheduler
timeScheduler = sched.scheduler(time.time, time.sleep)

# Initialize time
brewTime = datetime(time.localtime(1))

# relay = OutputDevice(pin)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/', methods=('GET', 'POST'))
def index():
    data = {}

    form = CoffeeForm()
    if request.method == 'GET':
        return render_template('index.html', form=form, **data)

    else:
        inputTime = form.time.data
        currentTime = datetime.now()
        brewTime = datetime.combine(currentTime.date(), inputTime)

        # Check if time should be for the next day
        if (brewTime.hour < datetime.now().hour) and (brewTime.minute < datetime.now().minute):
            brewTime += timedelta(days=1)
            
        timeScheduler.enterabs(time.mktime(brewTime.timetuple()), priority=1, action=print, argument=(brewTime,))
        startThread = threading.Thread(target=timeScheduler.run)
        startThread.start()
        
        return render_template('index.html', form=form, **data)

        
        

@app.route('/brew')
def changeState(action):
    if action == 'off':
        # GPIO.output(pin, GPIO.LOW)
        templateData = {'status': 'on'}
    else:
        # GPIO.output(pin, GPIO.HIGH)
        templateData = {'status': 'off'}
    form = CoffeeForm()
    return render_template('index.html', form=form, **templateData)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
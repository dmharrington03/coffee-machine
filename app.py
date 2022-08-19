import math
from flask import Flask, render_template, redirect, url_for, request
# from requests import request
from form import CoffeeForm
import sched, threading, time
from datetime import date, timedelta, datetime
import sqlite3
# import RPi.GPIO as GPIO
import atexit, os
from brew import startBrew, stopBrew

pin = 4
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(pin, GPIO.OUT)
# GPIO.output(pin, GPIO.HIGH)

# atexit.register(GPIO.cleanup)

# Initiate scheduler
timeScheduler = sched.scheduler(time.time, time.sleep)

# relay = OutputDevice(pin)
BREW_SECS = 330 # 5.5 minutes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/', methods=('GET', 'POST'))
def index():

    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()
    res = dbcur.execute("SELECT * FROM times").fetchall()
    try:
        res = res[0][0]
    except:
        res = None

    form = CoffeeForm()
    if request.method == 'GET':
        
        # If there is a stored time
        if res:

            print(f"Stored time {res}")
            brewTime = datetime.fromtimestamp(res)

            timeDiff = (datetime.now() - brewTime).total_seconds()
            # Done Brewing
            if timeDiff>= BREW_SECS:
                dbcur.execute("DELETE FROM times")
                db.commit()
                # Return DONE BREWING
                return render_template('index.html', form=form)

            # Brewing in Progress
            elif (timeDiff < BREW_SECS) and (timeDiff > 0):
                return render_template('inProgress.html')
            
            # Brewing not in Progress
            else:
                # Show listed alarm
                return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'))

        return render_template('index.html', form=form)

    # POST
    else:
        inputTime = form.time.data
        currentTime = datetime.now()
        brewTime = datetime.combine(currentTime.date(), inputTime)

        # Check if time should be for the next day
        if (brewTime.hour < datetime.now().hour) and (brewTime.minute < datetime.now().minute):
            brewTime += timedelta(days=1)
        
        res = dbcur.execute("SELECT * FROM times").fetchall()
        timeDiff = (datetime.now() - brewTime).total_seconds()
        if res: # The user refreshes and the page POSTs the same alarm
            if (timeDiff < BREW_SECS) and (timeDiff > 0): # Brewing in progress
                return render_template('inProgress.html')
            elif timeDiff >= BREW_SECS: # Brewing done
                return render_template('index.html', form=form)
            else: # Brewing not yet started
                return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'))

        # else (the page is not a refresh)

        value = (int(round(brewTime.timestamp())),)
        dbcur.execute("INSERT INTO times (time) VALUES (?)", value)
        db.commit()
        timeScheduler.enterabs(time.mktime(brewTime.timetuple()), priority=1, action=startBrew, argument=(pin, BREW_SECS))
        startThread = threading.Thread(target=timeScheduler.run)
        startThread.start()

        timeDiff = brewTime - datetime.now()

        return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'))


@app.route('/brew')
def brew():
    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()
    dbcur.execute("DELETE FROM times")
    value = (int(math.floor(time.time())),)
    dbcur.execute("INSERT INTO times (time) VALUES (?)", value)
    db.commit()
    db.close()
    form = CoffeeForm()
    startThread = threading.Thread(target=startBrew, args=(pin, BREW_SECS))
    startThread.start()

    return redirect("/")

@app.route('/finished')
def finished():
    return render_template('finished.html')

@app.route('/delete')
def delete():
    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()
    dbcur.execute("DELETE FROM times")
    db.commit()
    db.close()
    stopBrew(pin)
    return redirect("/")
        

@app.route('/progress')
def progress():
    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()
    res = dbcur.execute("SELECT * FROM times").fetchall()[0][0]
    db.close()
    timeDiff = (datetime.now() - datetime.fromtimestamp(res)).total_seconds()
    if (timeDiff < BREW_SECS) and (timeDiff > 0): # If brewing in progress, should always be called
        return str(math.floor(timeDiff)) # Seconds elapsed
    else: # Alarm not yet gone off, should never be called
        return ""



@app.route('/stop')
def stop():
    form = CoffeeForm()
    return render_template('index.html', form=form)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
import math
import sched
from flask import Flask, render_template, redirect, url_for, request
from form import CoffeeForm
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta, datetime
import sqlite3
import RPi.GPIO as GPIO
import atexit, os
from brew import startBrew, stopBrew

pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.HIGH)

atexit.register(GPIO.cleanup)

scheduler = BackgroundScheduler()
stopBrewing = False


relay = OutputDevice(pin)
BREW_SECS = 330 # 5.5 minutes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

def stopState():
    return stopBrewing

@app.route('/', methods=('GET', 'POST'))
def index():

    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()
    res = dbcur.execute("SELECT * FROM times").fetchall()
    try:
        res = res[0][0]
    except:
        res = None
    
    day = ""

    form = CoffeeForm()
    if request.method == 'GET':
        
        # If there is a stored time
        if res:

            brewTime = datetime.fromtimestamp(res)
            if brewTime.time() < datetime.now().time():
                day = "Tomorrow"
            else: 
                day = "Today"
        

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
                return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'), day=day)

        return render_template('index.html', form=form)

    # POST
    else:
        inputTime = form.time.data
        currentTime = datetime.now()
        brewTime = datetime.combine(currentTime.date(), inputTime)


        # Check if the inputted time is earlier than the current time
        if inputTime < currentTime.time():
            brewTime += timedelta(days=1)
            day = "Tomorrow"
        else: 
            day = "Today"
        

        res = dbcur.execute("SELECT * FROM times").fetchall()
        timeDiff = (datetime.now() - brewTime).total_seconds()
        if res: # The user refreshes and the page POSTs the same alarm
            if (timeDiff < BREW_SECS) and (timeDiff > 0): # Brewing in progress
                return render_template('inProgress.html')
            elif timeDiff >= BREW_SECS: # Brewing done
                return render_template('index.html', form=form)
            else: # Brewing not yet started
                return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'), day=day)

        # else (the page is not a refresh)

        value = (int(round(brewTime.timestamp())),)
        dbcur.execute("INSERT INTO times (time) VALUES (?)", value)
        db.commit()

        scheduler.remove_all_jobs()
        
        scheduledJob = scheduler.add_job(startBrew, 'date', run_date=datetime.fromtimestamp(time.mktime(brewTime.timetuple())), args=(pin, BREW_SECS, stopState))
        if not scheduler.running:
            scheduler.start()

        print(f'Alarm set for {str(brewTime)}')

        timeDiff = brewTime - datetime.now()

        return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'), day=day)


# 'Brew now' button pressed
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

    # Remove any scheduled start processes and tell running functions to stop
    if scheduler.get_jobs():
        scheduler.remove_all_jobs()
        stopBrewing = True
        time.sleep(2)
        stopBrewing = False

    instantStartJob = scheduler.add_job(startBrew, 'date', run_date=datetime.now(), args=(pin, BREW_SECS, stopState))

    if not scheduler.running:
        scheduler.start()
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

    # Kill any brew processes running
    if scheduler.get_jobs():
        scheduler.remove_all_jobs()
    
    stopBrewing = True
    time.sleep(2)
    stopBrewing = False

    return redirect("/")

@app.route('/progress')
def progress():
    db = sqlite3.connect('./times.db')
    dbcur = db.cursor()

    # If client queries after time is already deleted
    try:
        res = dbcur.execute("SELECT * FROM times").fetchall()[0][0]
        timeDiff = (datetime.now() - datetime.fromtimestamp(res)).total_seconds()
        if (timeDiff < BREW_SECS) and (timeDiff > 0): # If brewing in progress, should always be called
            return str(math.floor(timeDiff)) # Seconds elapsed
        else: # Alarm not yet gone off, should never be called
            return ""

    except IndexError:
        print("index error when querying progress API")

    db.close()
    return ""



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
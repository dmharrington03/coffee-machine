from flask import Flask, render_template,  url_for, redirect, request
# from requests import request
from form import CoffeeForm
import sched, threading, time
from datetime import date, timedelta, datetime
import sqlite3
# from gpiozero import OutputDevice
# import brew

pin = 18

# Initiate scheduler
timeScheduler = sched.scheduler(time.time, time.sleep)

# relay = OutputDevice(pin)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/', methods=('GET', 'POST'))
def index():

    db = sqlite3.connect("./times.db")
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

            timeDiff = brewTime - datetime.now()
            if timeDiff.total_seconds() <= 0:
                dbcur.execute("DELETE FROM times")
                db.commit()
                # Return DONE BREWING
                return render_template('index.html', form=form)

            if timeDiff < timedelta(minutes=5):
                return render_template('inProgress.html', remaining=round(timeDiff.total_seconds()))
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
        
        value = (int(round(brewTime.timestamp())),)
        dbcur.execute("INSERT INTO times (time) VALUES (?)", value)
        db.commit()
        timeScheduler.enterabs(time.mktime(brewTime.timetuple()), priority=1, action=print, argument=(brewTime,))
        startThread = threading.Thread(target=timeScheduler.run)
        startThread.start()

        timeDiff = brewTime - datetime.now()
        if timeDiff < timedelta(minutes=5):
            return render_template('inProgress.html', remaining=round(timeDiff.total_seconds()))
        else:
            # Alarm Set
            return render_template('alarm.html', time=brewTime.strftime('%I:%M %p'))


@app.route('/clear')
def clear():
    db = sqlite3.connect("./times.db")
    dbcur = db.cursor()
    dbcur.execute("DELETE FROM times")
    db.commit()
    db.close()
    form = CoffeeForm()
    return render_template('index.html', form=form)
        

@app.route('/progress')
def progress():
    db = sqlite3.connect("./times.db")
    dbcur = db.cursor()
    res = dbcur.execute("SELECT * FROM times").fetchall()[0][0]
    timeDiff = datetime.fromtimestamp(res) - datetime.now()
    return str(round(timeDiff.total_seconds())) # Seconds remaining



#TODO return redirect
@app.route('/stop')
def stop():
    form = CoffeeForm()
    return render_template('index.html', form=form)

#TODO return redirect
@app.route('/brew')
def brew():
    
    return render_template('inProgress.html', remaining=300)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
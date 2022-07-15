from flask import Flask, render_template,  url_for, redirect
from form import AlarmForm
# import RPi.GPIO as GPIO


pin = 18

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(pin, GPIO.OUT)
# GPIO.output(pin, GPIO.LOW)

light_on = False

@app.route('/', methods=('GET', 'POST'))
def index():
    templateData = {'status': 'on'}
    form = AlarmForm()
    return render_template('index.html', form=form,  **templateData)

@app.route('/<action>')
def changeState(action):
    if action == 'off':
        # GPIO.output(pin, GPIO.LOW)
        templateData = {'status': 'on'}
    else:
        # GPIO.output(pin, GPIO.HIGH)
        templateData = {'status': 'off'}
    form = AlarmForm()
    return render_template('index.html', form=form, **templateData)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
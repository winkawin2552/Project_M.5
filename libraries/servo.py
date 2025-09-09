from RPi.GPIO import *
import time

setmode(BCM)

class Servo:
    def __init__(self, pin):
        self.pin = pin
        setwarnings(False)
        setup(self.pin, OUT)
        self.pwm = PWM(self.pin, 50)
        self.pwm.start(0)

    def write(self, angle):
        duty = (angle / 18.0) + 2.5
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        self.pwm.ChangeDutyCycle(0)

    def stop(self):
        self.pwm.stop()

if __name__ == '__main__':
    myservo = Servo(25)
    try:
        while True:
            myservo.write(180)
            time.sleep(1)
            myservo.write(90)
            time.sleep(1)
            myservo.write(0)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        myservo.stop()
        cleanup()

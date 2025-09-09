from RPi.GPIO import *
setmode(BCM)

class L298N:
    def __init__(self, lis):
        setup(lis[0:3], OUT)
        output(lis[0:2], LOW)
        self.in1 = lis[0]
        self.in2 = lis[1]
        self.pwm = PWM(lis[2], 1000)
        self.pwm.start(0)
    
    def setSpeed(self, speed, bool = True):
        self.pwm.ChangeDutyCycle(speed)
        if bool:
            output(self.in1, 1)
            output(self.in2, 0)
        else:
            output(self.in1, 0)
            output(self.in2, 1)

    def stop(self):
        self.pwm.ChangeDutyCycle(0)
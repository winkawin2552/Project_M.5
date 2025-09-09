from RPi.GPIO import *
import time
setmode(BCM)
def measure(trig = 23, echo = 24, temp = 25):
    
    trig = trig
    echo = echo
    temp = temp
    setup(trig, OUT)
    setup(echo, IN)
    temp = 25

    output(trig, False)
    time.sleep(0.05)
    
    output(trig, True)
    time.sleep(10 ** (-5))
    output(trig, False)
    
    while input(echo) == 0:
        pulse_start = time.time()



    
    while input(echo) == 1:
        pulse_end = time.time()



    
    duration = pulse_end - pulse_start
    
    dist = duration * (331 + 0.6 * temp)/2 * 100
    dist =  round(dist, 2)
    return(dist)

if __name__ == '__main__' :
    try:
        while 1:
            dist = measure()
            print(f'Distance: {dist} cm')
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stop by User')


        cleanup()
    finally:
        cleanup()
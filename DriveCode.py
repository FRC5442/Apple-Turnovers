
'''---------------------------------

    Team A

    Code Setup

---------------------------------'''

from PCA9685 import PCA9685
import Gamepad
import RPi.GPIO as GPIO
import time



pwm = PCA9685(0x40)
pwm.setPWMFreq(50)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)



if Gamepad.available():
    gamepad = Gamepad.smx()
else:
    print("Controller not connected")

gamepad.startBackgroundUpdates()



'''---------------------------------

    Define Variables

---------------------------------'''
###     Constants

leftMotor = 0
rightMotor = 1
shooter = 2
shooterSingulation = 3
LASER_1 = 21
LASER_2 = 20

servoLoaderPositionEngaged = 110       #the engaged position for the loader
servoLoaderPositionRest = 70            #The rest position for the loader

servo2PositionEngaged = 0       #the engaged position for servo 2
servo2PositionRest = 90         #The rest position for servo 2

enableLED = 18                  #Pin to connect the enable LED to

DRIVE_POWER = 0.8               #Adjust limts of pwm range for drive (percentage)
SLOW_DRIVE_POWER = .25          #Adjust for limit on pwm range for drive when moving slower (precentage)
centerAdj = 80                  #Adjust center of pwm range for drive

SHOOTER_STANDARD_CHANGE = 0.05      #Adjust for shooter speed increments
SHOOTER_SMALL_CHANGE = 0.01         #Adjust for smaller shooter speed increments

SHOOTER_MIN = 0.2
SHOOTER_MAX = 0.95


###     Other

controllerEnabled = False   #Value to change when controller is being disabled

reverseHead = False         #Boolean value to determine head reversed
shooterEnabled = False      #Boolean value to determine shooter enabled
yHeld = False               #Boolean value to determine if y is held


powerAdj = DRIVE_POWER      #setting changable powerAdj to 
shooterPowerAdj = 0.37       #Default power precentage for shooter motor


GPIO.setup(enableLED, GPIO.OUT)     #Setting up enable LED for output
GPIO.setup(LASER_1, GPIO.OUT)
GPIO.setup(LASER_2, GPIO.OUT)

'''---------------------------------

    Generic Methods

---------------------------------'''

def remapServoPosition(oldValue):
    #Method to remap input of 0 to 180 degrees to output of PWM range for servo positioning
    oldMin = 0
    oldMax = 180
    oldRange = oldMax - oldMin

    newMin = 500
    newMax = 2500
    newRange = newMax - newMin

    value = (((oldValue - oldMin) * newRange) / oldRange) + newMin
    return value


def remapShooter(rawInput, cntAdj, pwrAdj):
    #Method to remap shooter motor PWM value
    value = 1500 + cntAdj + (500 * pwrAdj * rawInput)
    return value

def remapDrive(rawInput, centAdj, pwrAdj):
    #Method to remap drive motors to PWM values
    value = 1500 + centAdj + (500 * pwrAdj * rawInput)
    return value

def exitProc():
    #Method to disconnect controller and end program
    print("---Controller Disconnected---")
    gamepad.disconnect()

def enableHandlers():
    #Method to standardize enabling event handlers
    #Add all event handlers here
    gamepad.addButtonPressedHandler("A", pressA)
    gamepad.addButtonPressedHandler("B", pressB)
    gamepad.addButtonPressedHandler("X", pressX)
    gamepad.addButtonPressedHandler("Y", pressY)

    gamepad.addButtonPressedHandler("LB", pressLB)
    gamepad.addButtonPressedHandler("RB", pressRB)
    gamepad.addButtonPressedHandler("LT", pressLT)
    gamepad.addButtonPressedHandler("RT", pressRT)

    gamepad.addButtonReleasedHandler("LT", releaseLT)
    gamepad.addButtonReleasedHandler("X", releaseX)
    gamepad.addButtonReleasedHandler("B", releaseB)
    gamepad.addButtonReleasedHandler("Y", releaseY)

    gamepad.addAxisMovedHandler("LEFT-Y", moveLeftY)
    gamepad.addAxisMovedHandler("RIGHT-Y", moveRightY)
    gamepad.addAxisMovedHandler("DPAD-Y", moveStraight)
    gamepad.addAxisMovedHandler("DPAD-X", autoCode)

def enableGenearicHandlers():
    #Method to enable necessary event handlers
    #Add all necessary event handlers here
    gamepad.addButtonPressedHandler("START", pressSTART)
    gamepad.addButtonPressedHandler("BACK", exitProc)



'''---------------------------------

    Button Press Methods

---------------------------------'''

###    Buttons

def pressA():
    #when pressed, turn shooter motor on or off
    global shooterEnabled
    if shooterEnabled == False:
        #Turn shooter on if off
        pwm.setServoPulse(shooter, remapShooter(-1, centerAdj, shooterPowerAdj))
        print("Motor: ON   Output:", remapShooter(-1, centerAdj, shooterPowerAdj), "    Precentage:", round(shooterPowerAdj, 2))
        shooterEnabled = True
    else:
        #Turn shooter off if on
        pwm.setServoPulse(shooter, remapShooter(0, centerAdj, shooterPowerAdj))
        print("Motor: OFF")
        shooterEnabled = False


def pressB():
    #when pressed, load new ball
    global servoLoaderPositionEngaged
    pwm.setServoPulse(shooterSingulation, remapServoPosition(servoLoaderPositionEngaged))
    print("pressed B, shooter loader moved to:", servoLoaderPositionEngaged)

def releaseB():
    #When released, return singulation to normal
    global servoLoaderPositionRest
    pwm.setServoPulse(shooterSingulation, remapServoPosition(servoLoaderPositionRest))
    print("B released, shooter loader moved to: ", servoLoaderPositionRest)


def pressX():
    #when pressed, turn servo
    print("Pressed X: Lasers ON")
    GPIO.output(LASER_1, GPIO.HIGH)
    GPIO.output(LASER_2, GPIO.HIGH)

def releaseX():
    #when released, reset servo
    print("Released X: Lasers OFF")
    GPIO.output(LASER_1, GPIO.LOW)
    GPIO.output(LASER_2, GPIO.LOW)

def pressY():
    global yHeld
    yHeld = True
def releaseY():
    global yHeld
    yHeld = False



def pressSTART():
    #When pressed, toggle controller enabled
    global controllerEnabled
    if controllerEnabled == False:
        controllerEnabled = True
        print("Pressed Y, Controller:    Enabled")
        GPIO.output(enableLED, GPIO.HIGH)
        enableHandlers()

    else:
        controllerEnabled = False
        print("Pressed Y, Controller:    Disabled")
        GPIO.output(enableLED, GPIO.LOW)
        gamepad.removeAllEventHandlers()
        enableGenearicHandlers()
        
    

###
###    Triggers
###

def pressLB():
    #When pressed, decrease shooter speed range
    global shooterPowerAdj
    global shooterEnabled
    global SHOOTER_STANDARD_CHANGE
    global yHeld
    global SHOOTER_MIN

    if yHeld == True:
        if shooterPowerAdj <= SHOOTER_MIN:
            print("range is minimized")
        else:
            shooterPowerAdj -= SHOOTER_SMALL_CHANGE
            print("range decreased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))
    else:
        if shooterPowerAdj <= SHOOTER_MIN:
            print("range is minimized")
        else:
            shooterPowerAdj -= SHOOTER_STANDARD_CHANGE
            print("range decreased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))
    
    if shooterEnabled == True:
        pwm.setServoPulse(shooter, remapShooter(-1, centerAdj, shooterPowerAdj))
        print("Motor: ON   Output:", remapShooter(-1, centerAdj, shooterPowerAdj), "    Precentage:", round(shooterPowerAdj, 2))

def pressRB():
    #When pressed, increase shooter speed range
    global shooterPowerAdj
    global shooterEnabled
    global SHOOTER_STANDARD_CHANGE
    global yHeld
    global SHOOTER_MAX

    if yHeld == True:
        if shooterPowerAdj >= SHOOTER_MAX:
            print("range is maxed")
        else:
            shooterPowerAdj += SHOOTER_SMALL_CHANGE
            print("range increased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))
    else:
        if shooterPowerAdj >= SHOOTER_MAX:
            print("range is maxed")
        else:
            shooterPowerAdj += SHOOTER_STANDARD_CHANGE
            print("range increased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))

    if shooterEnabled == True:
        pwm.setServoPulse(shooter, remapShooter(-1, centerAdj, shooterPowerAdj))
        print("Motor: ON   Output:", remapShooter(-1, centerAdj, shooterPowerAdj), "    Precentage:", round(shooterPowerAdj, 2))

def pressLT():
    #When pressed, speed range decreased for more accurate positioning
    global powerAdj
    global SLOW_DRIVE_POWER

    powerAdj = SLOW_DRIVE_POWER
    print("Trigger pressed")

def releaseLT():
    #When released, speed range returned to normal
    global powerAdj
    global DRIVE_POWER

    powerAdj = DRIVE_POWER
    print("Trigger released")

def pressRT():
    #When pressed, change the head (switch the front of the robot)
    global reverseHead
    if reverseHead == False:
        reverseHead = True
        print("Pressed RT: Head reversed = true")
    else:
        reverseHead = False
        print("Pressed RT: Head reversed = false")



'''---------------------------------

    Axis Methods

---------------------------------'''

### Drive

def moveLeftY(position):
    #Map the left y joystick value to the left motor PWM output

    global reverseHead      #Check to see if head is reversed
    if reverseHead == True:
        #print("position reversed: left joystick")
        #position = -position        #Invert position values to change head
        pwm.setServoPulse(rightMotor, remapDrive(-position, centerAdj, powerAdj))
        print("Right Motor", round(remapDrive(-position, centerAdj, powerAdj)), "     Joystick Position: ", round(-position, 3))
    else:
        pwm.setServoPulse(leftMotor, remapDrive(-position, centerAdj, powerAdj))
        print("Left Motor", round(remapDrive(-position, centerAdj, powerAdj)), "     Joystick Position: ", round(-position, 3))

def moveRightY(position):
    #Map the right y joystick value to the right motor PWM output

    global reverseHead      #Check to see if head is reversed
    if reverseHead == True:
        #position = -position
        #print("position reversed")        #Invert position values to change head
        pwm.setServoPulse(leftMotor, remapDrive(position, centerAdj, powerAdj))
        print("Left Motor", round(remapDrive(position, centerAdj, powerAdj)), "     Joystick Position: ", round(position, 3))
    else:
        pwm.setServoPulse(rightMotor, remapDrive(position, centerAdj, powerAdj))
        print("Right Motor", round(remapDrive(position, centerAdj, powerAdj)), "     Joystick Position: ", round(position, 3))

def moveStraight(position):
    global reverseHead
    if reverseHead == True:
        pwm.setServoPulse(leftMotor, remapDrive(position, centerAdj, .25))
        pwm.setServoPulse(rightMotor, remapDrive(-position, centerAdj, .25))
        print("Moving straight")
    else:
        pwm.setServoPulse(leftMotor, remapDrive(-position, centerAdj, .25))
        pwm.setServoPulse(rightMotor, remapDrive(position, centerAdj, .25))
        print("Moving straight")

def autoCode(position):
    pwm.setServoPulse(shooter, remapShooter(-1, centerAdj, 0.97))
    time.sleep(.05)
    pressB()
    time.sleep(0.5)
    releaseB()
    time.sleep(0.5)
    pressB()
    time.sleep(0.5)
    releaseB()
    time.sleep(1)
    pwm.setServoPulse(shooter, remapShooter(0, centerAdj, 0.97))

    
    
    print("AutoCode Enabled")



'''---------------------------------

    Gamepad Handlers

---------------------------------'''

gamepad.removeAllEventHandlers()
enableGenearicHandlers()


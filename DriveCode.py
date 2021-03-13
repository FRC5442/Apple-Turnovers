
'''---------------------------------

    Code Setup

---------------------------------'''

import sys
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
    sys.exit(0)

gamepad.startBackgroundUpdates()



'''---------------------------------

    Define Variables

---------------------------------'''

controllerEnabled = False
reverseHead = False
shooterEnabled = False

fenceUp = True

center = 1500
shooterRange = 1000
shooterMin = 1000

centerAdj = 0 #Adjust center of pwm range for drive
powerAdj = 0.5 #Adjust limts of pwm range for drive (percentage)

shooterPowerAdj = 0.5

leftMotor = 0
rightMotor = 1
shooter = 2
manip = 3
fenceLeft = 4
fenceRight = 5

enableLED = 18

GPIO.setup(enableLED, GPIO.OUT)


'''---------------------------------

    Generic Methods

---------------------------------'''

def remapServoPosition(oldValue):
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
    value = 1500 + centAdj + (500 * pwrAdj * rawInput)
    return value

def exitProc():
    #method to disconnect controller and end program
    print("---Controller Disconnected---")
    pwm.setServoPulse(leftMotor, remapDrive(0, centerAdj, powerAdj))
    pwm.setServoPulse(rightMotor, remapDrive(0, centerAdj, powerAdj))
    pwm.setServoPulse(shooter, remapDrive(0, centerAdj, powerAdj))
    GPIO.output(enableLED, GPIO.LOW)    
    gamepad.disconnect()

def enableHandlers():
    gamepad.addButtonPressedHandler("A", loadBall)
    gamepad.addButtonPressedHandler("B", toggleShooter)
    gamepad.addButtonPressedHandler("X", switchHead)
    gamepad.addButtonPressedHandler("Y", toggleManip)

    gamepad.addButtonPressedHandler("LB", decreaseShooter)
    gamepad.addButtonPressedHandler("RB", increaseShooter)
    gamepad.addButtonPressedHandler("LT", toggleFence)
    gamepad.addButtonPressedHandler("RT", limitDrive)

    gamepad.addButtonReleasedHandler("RT", unlimitDrive)

    gamepad.addAxisMovedHandler("LEFT-Y", moveLeftY)
    gamepad.addAxisMovedHandler("RIGHT-Y", moveRightY)
    gamepad.addAxisMovedHandler("DPAD-Y", moveStraight)

def enableGenearicHandlers():
    gamepad.addButtonPressedHandler("START", toggleEnable)
    gamepad.addButtonPressedHandler("BACK", exitProc)


'''---------------------------------

    Button Press Methods

---------------------------------'''

###    Buttons

def loadBall():
    pwm.setServoPulse(shooter, remapShooter(1, centerAdj, 0.6))
    print("Loading Shooter")
    time.sleep(2.5)
    print("Done Loading")
    pwm.setServoPulse(shooter, remapShooter(0, centerAdj, 0))

def toggleShooter():
    #when pressed, turn shooter motor on
    global shooterEnabled

    if shooterEnabled == False:
        pwm.setServoPulse(shooter, remapShooter(1, centerAdj, shooterPowerAdj))
        print("Motor: ON   Output:", remapShooter(1, centerAdj, shooterPowerAdj), "    Precentage:", shooterPowerAdj)
        shooterEnabled = True
    else:
        pwm.setServoPulse(shooter, remapShooter(0, centerAdj, shooterPowerAdj))
        print("Shooter: OFF")
        shooterEnabled = False

def toggleFence():
    #when pressed, drop fence or raise fence
    global fenceUp

    print("Fence Toggled")

    if not fenceUp:
        pwm.setServoPulse(fenceLeft, remapServoPosition(85))
        pwm.setServoPulse(fenceRight, remapServoPosition(95))
        fenceUp = True
    else:
        pwm.setServoPulse(fenceLeft, remapServoPosition(0))
        pwm.setServoPulse(fenceRight, remapServoPosition(180))
        fenceUp = False
    print("Pressed B, Fence State: ", not fenceUp)

def toggleManip():
    #When pressed, print pressed

    print("Manipulator Toggled")

    pwm.setServoPulse(manip, remapServoPosition(25))
    time.sleep(0.5)
    pwm.setServoPulse(manip, remapServoPosition(180))
    print("Pressed Y")

def toggleEnable():
    #When pressed, toggle disable controller
    global controllerEnabled
    if controllerEnabled == False:
        controllerEnabled = True
        print("Pressed START, Controller:    Enabled")
        GPIO.output(enableLED, GPIO.HIGH)
        enableHandlers()

    else:
        controllerEnabled = False
        print("Pressed START, Controller:    Disabled")
        GPIO.output(enableLED, GPIO.LOW)
        gamepad.removeAllEventHandlers()
        enableGenearicHandlers()

def decreaseShooter():
    #When pressed, decrease shooter speed range
    global shooterPowerAdj
    global shooterEnabled
    if shooterPowerAdj <= 0.3:
        print("range is minimized")
    else:
        shooterPowerAdj -= 0.05
        print("range decreased, new shooterPowerAdj = ", shooterPowerAdj)

    if shooterEnabled == True:
        pwm.setServoPulse(shooter, remapShooter(1, centerAdj, shooterPowerAdj))
        print("Shooter speed DECREASED. New Speed: ", remapShooter(1, centerAdj, shooterPowerAdj))

def increaseShooter():
    #When pressed, increase shooter speed range
    global shooterPowerAdj
    if shooterPowerAdj >= 0.9:
        print("range is maxed")
    else:
        shooterPowerAdj += 0.05
        print("range increased, new shooterPowerAdj = ", shooterPowerAdj)

    if shooterEnabled == True:
        pwm.setServoPulse(shooter, remapShooter(1, centerAdj, shooterPowerAdj))
        print("Shooter speed INCREASED. New Speed: ", remapShooter(1, centerAdj, shooterPowerAdj))

def limitDrive():
    #When pressed, speed range decreased for more accurate positioning
    global powerAdj

    powerAdj = 0.25
    print("Drive Limit")

def unlimitDrive():
    #When released, speed range returned to normal
    global powerAdj

    powerAdj = 0.5
    print("Drive Unlimited")

def switchHead():
    #When pressed, toggle head reverse
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
    global reverseHead

    if reverseHead == True:
        pwm.setServoPulse(rightMotor, remapDrive(-position, centerAdj, powerAdj))
        print("Left Motor", remapDrive(-position, centerAdj, powerAdj))
        print("Joystick Position: ", -position)
    else:
        pwm.setServoPulse(leftMotor, remapDrive(-position, centerAdj, powerAdj))
        print("Left Motor", remapDrive(-position, centerAdj, powerAdj))
        print("Joystick Position: ", -position)

def moveRightY(position):
    #Map the right y joystick value to the right motor PWM output
    global reverseHead
    if reverseHead == True:
        pwm.setServoPulse(leftMotor, remapDrive(position, centerAdj, powerAdj))
        print("Right Motor", remapDrive(position, centerAdj, powerAdj))
        print("Joystick Position: ", position)
    else:
        pwm.setServoPulse(rightMotor, remapDrive(position, centerAdj, powerAdj))
        print("Right Motor", remapDrive(position, centerAdj, powerAdj))
        print("Joystick Position: ", position)

def moveStraight(position):
    global reverseHead
    if reverseHead == True:
        pwm.setServoPulse(rightMotor, remapDrive(-position, centerAdj, powerAdj))
        pwm.setServoPulse(leftMotor, remapDrive(position, centerAdj, powerAdj))
    else:
        pwm.setServoPulse(rightMotor, remapDrive(position, centerAdj, powerAdj))
        pwm.setServoPulse(leftMotor, remapDrive(-position, centerAdj, powerAdj))
        print("Moving Straight")

'''---------------------------------

    Gamepad Handlers

---------------------------------'''

gamepad.removeAllEventHandlers()
enableGenearicHandlers()

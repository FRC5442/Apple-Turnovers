
'''---------------------------------

    Code Setup

---------------------------------'''

import sys
from PCA9685 import PCA9685
import Gamepad
import time

pwm = PCA9685(0x40)
pwm.setPWMFreq(50)

if Gamepad.available():
    gamepad = Gamepad.smx()
else:
    print("Controller not connected")

gamepad.startBackgroundUpdates()



'''---------------------------------

    Define Variables

---------------------------------'''
controllerEnabled = True  #Value to change when controller is being disabled

reverseHead = False
shooterEnabled = False

center = 1500
shooterRange = 1000
shooterMin = 1000

centerAdj = 80 #Adjust center of pwm range for drive
powerAdj = 0.5 #Adjust limts of pwm range for drive (percentage)

shooterPowerAdj = 0.5

leftMotor = 0
rightMotor = 1
shooter = 2
shooterSingulation = 3
pusherServo = 4



'''---------------------------------

    Generic Methods

---------------------------------'''

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
    gamepad.disconnect()

def enableHandlers():
    gamepad.addButtonPressedHandler("A", pressA)
    gamepad.addButtonPressedHandler("B", pressB)
    gamepad.addButtonPressedHandler("X", pressX)

    gamepad.addButtonPressedHandler("LB", pressLB)
    gamepad.addButtonPressedHandler("RB", pressRB)
    gamepad.addButtonPressedHandler("LT", pressLT)
    gamepad.addButtonPressedHandler("RT", pressRT)

    gamepad.addButtonReleasedHandler("LT", releaseLT)
    gamepad.addButtonReleasedHandler("X", releaseX)
    gamepad.addButtonReleasedHandler("B", releaseB)

    gamepad.addAxisMovedHandler("LEFT-Y", moveLeftY)
    gamepad.addAxisMovedHandler("RIGHT-Y", moveRightY)

def enableGenearicHandlers():
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
    pwm.setServoPulse(shooterSingulation, 1300)
    print("pressed B, shooter loader moved")

def releaseB():
    #When released, return singulation to normal
    pwm.setServoPulse(shooterSingulation, 1500)
    print("B released, shooter loader moved")

def pressX():
    #when pressed, turn servo
    pwm.setServoPulse(pusherServo, 1500)
    print("Pressed X: Servo set to 90 deg")

def releaseX():
    #when released, reset servo
    pwm.setServoPulse(pusherServo, 500)
    print("Released X: Servo set to 0 deg")

def pressSTART():
    #When pressed, disable controller
    global controllerEnabled
    if controllerEnabled == False:
        controllerEnabled = True
        print("Pressed Y, Controller:    Enabled")
        enableHandlers()

    else:
        controllerEnabled = False
        print("Pressed Y, Controller:    Disabled")
        gamepad.removeAllEventHandlers()
        enableGenearicHandlers()
        
    


###    Triggers

def pressLB():
    #When pressed, decrease shooter speed range
    global shooterPowerAdj
    if shooterPowerAdj <= 0.3:
        print("range is minimized")
    else:
        shooterPowerAdj -= 0.05
        print("range decreased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))

def pressRB():
    #When pressed, increase shooter speed range
    global shooterPowerAdj
    if shooterPowerAdj >= 0.9:
        print("range is maxed")
    else:
        shooterPowerAdj += 0.05
        print("range increased, new shooterPowerAdj = ", round(shooterPowerAdj, 2))

def pressLT():
    #When pressed, speed range decreased for more accurate positioning
    global powerAdj

    powerAdj = 0.25
    print("Trigger pressed")

def releaseLT():
    #When released, speed range returned to normal
    global powerAdj

    powerAdj = 0.5
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
        #print("position reversed")
        position = -position        #Invert position values to change head
    
    pwm.setServoPulse(leftMotor, remapDrive(-position, centerAdj, powerAdj))
    print("Left Motor", round(remapDrive(-position, centerAdj, powerAdj)), "     Joystick Position: ", round(-position, 3))

def moveRightY(position):
    #Map the right y joystick value to the right motor PWM output

    global reverseHead      #Check to see if head is reversed
    if reverseHead == True:
        position = -position
        #print("position reversed")        #Invert position values to change head

    pwm.setServoPulse(rightMotor, remapDrive(position, centerAdj, powerAdj))
    print("Right Motor", round(remapDrive(position, centerAdj, powerAdj)), "     Joystick Position: ", round(position, 3))





'''---------------------------------

    Gamepad Handlers

---------------------------------'''

enableGenearicHandlers()
enableHandlers()


"""Defines the rotating base of the scanner"""
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import itertools
import scanner_limit_switch


class ScannerBase(object):
    """The base of the 3d scanner (controls rotation via stepper motor).
    Attributes:
        motor_hat: default adafruit motor hat object
        stepper: the stepper motor
    """

    def __init__(self, stepper_steps_per_rev=None, stepper_motor_port=None, switch=None):
        """Return a ScannerBase object
        :param steps_per_rev: the number of steps per revolution
        :param motor_port:  the motor port #
        """
        # default to 400 steps/rev, motor port #1
        if stepper_steps_per_rev is None:
            stepper_steps_per_rev = 400
        if stepper_motor_port is None:
            stepper_motor_port = 2
        if switch is None:
            switch = scanner_limit_switch.LimitSwitch()

        # create a default object, no changes to I2C address or frequency
        self.motor_hat = Adafruit_MotorHAT()
        self.stepper = self.motor_hat.getStepper(
            stepper_steps_per_rev, stepper_motor_port)

        # note the limit switch
        self.switch = switch

        atexit.register(self.turn_off_motors)

    def move_steps(self, num_steps=None):
        """Moves the stepper motor the specified number of steps
        :param num_steps: # of steps to move, defaults to 1
        """
        if num_steps is None:
            num_steps = 1
        if num_steps < 0:
            num_steps = abs(num_steps)
            direction = Adafruit_MotorHAT.FORWARD
        else:
            direction = Adafruit_MotorHAT.BACKWARD

        for _ in itertools.repeat(None, num_steps):
            self.stepper.oneStep(direction, Adafruit_MotorHAT.MICROSTEP)

    def move_degrees(self, num_deg=None):
        """Moves the stepper motor by the specified num_deg, as close as step resolution permits.
        :param num_deg: angle to move in degrees, defaults to 1 degree
        """
        if num_deg is None:
            num_deg = 1
        self.move_steps(int(round(num_deg * self.get_steps_per_deg())))

    def get_num_steps_per_rev(self):
        """Returns the number of micro-steps in a full rotation"""
        return 400 * 8  # 400 steps/rev * 8 microsteps/step

    def get_steps_per_deg(self):
        """Returns the number of steps per degree"""
        return 1.0 * self.get_num_steps_per_rev() / 360.0

    def reset(self):
        """Resets the base angle."""

        # print 'Returning home quickly...'

        # check that the switch is not already pressed (ie: edge case where a
        # rising edge event won't occur)
        if not self.switch.is_pressed():
            # Move quickly backward to home angle, until hitting the limit
            # switch.
            self.switch.setup_event_detect()
            while not self.switch.check_for_press():
                self.stepper.oneStep(Adafruit_MotorHAT.FORWARD,
                                     Adafruit_MotorHAT.SINGLE)
                time.sleep(.1)
            self.switch.destroy()

        # print 'Hit limit switch...'

        # Move forward off the switch
        self.move_degrees(12)
        time.sleep(1.5)

        # print 'Returning home slowly...'

        # check that the switch is not already pressed (ie: edge case where a
        # rising edge event won't occur)
        if not self.switch.is_pressed():
            self.switch.setup_event_detect()
            # Move slowly backward to home angle, until just hitting the limit
            # switch
            while not self.switch.check_for_press():
                self.move_degrees(-1)
                time.sleep(.2)
            self.switch.destroy()

    def turn_off_motors(self):
        """Turns off stepper motor, recommended for auto-disabling motors on shutdown!"""
        self.motor_hat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def test_demo():
    """Performs a small test demo (reset, and move base 90 degrees)"""
    base = ScannerBase()
    base.reset()
    for _ in itertools.repeat(None, 90):
        base.move_degrees(1)
        time.sleep(.1)  # sleep for 100 ms


def main():
    """Creates a base and moves it 90 degrees"""
    test_demo()


if __name__ == '__main__':
    main()

Tutorial
========

How to run the program
-------------------------------
> python qtsimiam.py

or

> ./qtsimiam.py


Week 2: Unicycle to Differential Transformation
===============================================
Week one is about download and familiarization. So onward...

Part 1: Unicycle to Differential
--------------------------------

1. Navigate to ./pysimiam/supervisors/khepera3.py and open it in an editor

2. Find the function labeled `uni2diff` in the khepera3.K3Supervisor class.

def uni2diff(uni)
    (v,w) = uni

    #Insert Week 2 Assignment Code Here

    #End Week 2 Assignment Code

    return (vl, vr)

`uni` is a python tuple with two values. To get those values out of the variable simple apply a statement like this:

(v, w) = uni

Your job is to assign values to vl and vr such that the velocity and omega unicycle input correspond to the velocity-left and velocity right.

Recall that the equations for unicycle model are:

.. math::
    \frac{dx}{dt} = v*cos(\phi)

.. math::
    \frac{dy}{dt} = v*sin(\phi)

.. math::
    \frac{d\phi}{dt} = \omega

And the differential model is:

.. math::
    \frac{dx}{dt} = \frac{R}{2}*(v_r + v_l)*cos(\phi)

.. math::
    \frac{dy}{dt} = \frac{R}{2}*(v_r + v_l)*cos(\phi)

.. math::
    \frac{d\phi}{dt} = \frac{R}{L}*(v_r - v_l)

Part 2: Odometry 
-----------------------------------------------------------

1. Open ./pysimiam/supevisors/khepera3.py in an editor.

2. Scoll to the `estimate_pose` function and enter you code in the noted area. 

You are given these variables:

- self.robot.wheels.radius (float)

- self.robot.wheels.base_lenght (float)

- self.robot.wheels.ticks_per_rev (integer)

- self.robot.wheels.left_ticks (integer)

- self.robot.wheels.right_ticks (integer)


self.robot.wheels.left_ticks and .right_ticks are real integers representing the tick numbering of the encoder (not elapsed ticks... you have to calculate that). 


You will need to implement a memory variable to store previous values. One example of how to do this might be:

prev_right_ticks = self.robot.wheels.right_ticks

prev_left_ticks = self.robot.wheels.left_ticks


Your objective is to solve for the change in x, y, and theta and from those values update the variables x_new, y_new, and theta_new. The values x_new, y_new, and theta_new will be used to update the estimated pose for the supervisor. 


Part 3: IR Distance calculation (in meters) 
-----------------------------------------------------------

1. Open ./pysimiam/supervisors/khepera3.py in a text editor.

2. Find the `get_ir_distances` function.

3. Insert your code into the indicated area.

You are provided with the variable:

- self.robot.ir_sensors.readings (float)

Knowing that the sensitive range of distance is 0.02 meters to 0.2 meters and that the intensity as a function of distance is given by:

.. math::
    :nowrap:

    f(\delta) = \{\begin{eqnarray}
        3960 & \quad 0m <  \delta  < 0.02m\\ 
        3960e^{-30(\delta-0.02)} & \quad 0.02m <  \delta  < 0.2m
    \end{eqnarray}

Convert to distances for the sensors and assign them to a list called ir_distances. 

Week 3: Go To Goal Controller
=============================
1. Open ./pysimiam/controllers/gotogoal.py in an editor.
2. Find the execute function in the controller with the appropriate label for week 3.

Given the following variables:

- state.goal.x

- state.pose  (the robot's pose)

To use the pose data, use a command like this:

(x, y, theta) = state.pose


3. Calculate the bearing (angle) to the goal (state.goal.x and state.goal.y)
4. Calculate the error from the present heading (theta) and the bearing.
5. Calculate proportional, integral, and differential terms of the PID.


Week 4: Avoid Obstacles Controller
==================================

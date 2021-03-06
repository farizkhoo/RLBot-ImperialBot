import math
import time
import numpy as np

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

class Vector3:
    def __init__(self,data):
        self.data = data
    def __sub__(self,value):
        return Vector3([self.data[0]-value.data[0],self.data[1]-value.data[1],self.data[2]-value.data[2]])
    def __mul__(self,value):
        return (self.data[0]*value.data[0] + self.data[1]*value.data[1] + self.data[2]*value.data[2])

class obj:
    def __init__(self):
        self.location = Vector3([0,0,0])
        self.velocity = Vector3([0,0,0])
        self.rotation = Vector3([0,0,0])
        self.rvelocity = Vector3([0,0,0])
        self.team = 0

        self.local_location = Vector3([0,0,0])

class exampleATBA:
    def __init__(self):
        self.expired = False
    def execute(self,agent):
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball,agent.me)/1.5)
        angle = shooting_angle2D(agent.ball, agent.human)
        print(angle)

        return agent.exampleController(target_location, target_speed)

class shooting_one:
    def __init__(self):
        self.expired = False
    def execute(self,agent):
        target_location = agent.ball
        angle = shooting_angle2D(agent.ball,agent.human)

        return agent.shootingController(target_location, taget_speed)

class FrizzBot(BaseAgent):
    def initialize_agent(self):
        self.me = obj()
        self.human = obj()
        self.ball = obj()
        self.start = time.time()

        self.state = exampleATBA()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()
        # print(packet.game_ball.physics.velocity.x)
        self.preprocess(packet)

        return self.state.execute(self)

    def preprocess(self,packet):
        self.me.location.data = [packet.game_cars[self.index].physics.location.x, packet.game_cars[self.index].physics.location.y, packet.game_cars[self.index].physics.location.z]
        self.me.velocity.data = [packet.game_cars[self.index].physics.velocity.x, packet.game_cars[self.index].physics.velocity.y, packet.game_cars[self.index].physics.velocity.z]
        self.me.rotation.data = [packet.game_cars[self.index].physics.rotation.pitch, packet.game_cars[self.index].physics.rotation.yaw, packet.game_cars[self.index].physics.rotation.roll]
        self.me.rvelocity.data = [packet.game_cars[self.index].physics.angular_velocity.x, packet.game_cars[self.index].physics.angular_velocity.y, packet.game_cars[self.index].physics.angular_velocity.z]
        self.me.matrix = rotator_to_matrix(self.me)
        self.me.boost = packet.game_cars[self.index].boost
        self.me.team = packet.game_cars[self.index].team

        self.human.location.data = [packet.game_cars[0].physics.location.x, packet.game_cars[0].physics.location.y, packet.game_cars[0].physics.location.z]
        self.human.velocity.data = [packet.game_cars[0].physics.velocity.x, packet.game_cars[0].physics.velocity.y, packet.game_cars[0].physics.velocity.z]
        self.human.rotation.data = [packet.game_cars[0].physics.rotation.pitch, packet.game_cars[0].physics.rotation.yaw, packet.game_cars[0].physics.rotation.roll]
        self.human.rvelocity.data = [packet.game_cars[0].physics.angular_velocity.x, packet.game_cars[0].physics.angular_velocity.y, packet.game_cars[0].physics.angular_velocity.z]
        self.human.matrix = rotator_to_matrix(self.human)
        self.human.boost = packet.game_cars[0].boost
        self.human.team = packet.game_cars[0].team

        
        self.ball.location.data = [packet.game_ball.physics.location.x, packet.game_ball.physics.location.y, packet.game_ball.physics.location.z]
        self.ball.velocity.data = [packet.game_ball.physics.velocity.x, packet.game_ball.physics.velocity.y, packet.game_ball.physics.velocity.z]
        self.ball.rotation.data = [packet.game_ball.physics.rotation.pitch, packet.game_ball.physics.rotation.yaw, packet.game_ball.physics.rotation.roll]
        self.ball.rvelocity.data = [packet.game_ball.physics.angular_velocity.x, packet.game_ball.physics.angular_velocity.y, packet.game_ball.physics.angular_velocity.z]

        # self.ball.local_location.data = to_local(self.ball, self.me)
        self.ball.local_location.data = to_local(self.ball, self.human)

        # print(self.ball.local_location.data[1])

    def exampleController(self,target_object,target_speed):
        location = target_object.local_location
        controller_state = SimpleControllerState()
        angle_to_ball = math.atan2(location.data[1],location.data[0])

        current_speed = velocity2D(self.me)
        #steering
        # if angle_to_ball > 0.1:
        #     controller_state.steer = controller_state.yaw = 1
        # elif angle_to_ball < -0.1:
        #     controller_state.steer = controller_state.yaw = -1
        # else:
        #     controller_state.steer = controller_state.yaw = 0

        #throttle
        if target_speed > current_speed:
            controller_state.throttle = 0
            # if target_speed > 1400 and self.start > 2.2 and current_speed < 2250:
                # controller_state.boost = True
        elif target_speed < current_speed:
            controller_state.throttle = 0

        #dodging
        time_difference = time.time() - self.start
        if time_difference > 2.5:
            self.start = time.time()
        elif time_difference <= 0.1:
            controller_state.jump = True
            controller_state.pitch = -1
        elif time_difference >= 0.1 and time_difference <= 0.15:
            controller_state.jump = False
            controller_state.pitch = -1
        elif time_difference > 0.15 and time_difference < 1:
            controller_state.jump = True
            controller_state.yaw = controller_state.steer
            controller_state.pitch = -1
        return controller_state

    def shootingController(self,target_object,target_speed):
        controller_state = SimpleControllerState()

        return controller_state


def to_local(target_object,our_object):
    x = (target_object.location - our_object.location) * our_object.matrix[0]
    y = (target_object.location - our_object.location) * our_object.matrix[1]
    z = (target_object.location - our_object.location) * our_object.matrix[2]
    return [x,y,z]

def rotator_to_matrix(our_object):
    r = our_object.rotation.data
    CR = math.cos(r[2])
    SR = math.sin(r[2])
    CP = math.cos(r[0])
    SP = math.sin(r[0])
    CY = math.cos(r[1])
    SY = math.sin(r[1])

    matrix = []
    matrix.append(Vector3([CP*CY, CP*SY, SP]))
    matrix.append(Vector3([CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR]))
    matrix.append(Vector3([-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR]))
    return matrix

def velocity2D(target_object):
    return math.sqrt(target_object.velocity.data[0]**2 + target_object.velocity.data[1]**2)

def distance2D(target_object, our_object):
    if isinstance(target_object, Vector3):
        difference = target_object - our_object
    else:
        difference = target_object.location - our_object.location
    return math.sqrt(difference.data[0]**2 + difference.data[1]**2)

def shooting_angle2D(target_object, our_object):
    if our_object.team == 0: #blue team
        goal_loc_bl = Vector3([-892.755, 5120, 0])
        goal_loc_tl = Vector3([-892.755, 5120, 642.775])
        goal_loc_br = Vector3([892.755, 5120, 0])
        goal_loc_tr = Vector3([892.755, 5120, 642.775])
        goal_loc_c = Vector3([0, 5120, 321])
    else:
        goal_loc_bl = Vector3([-892.755, -5120, 0])
        goal_loc_tl = Vector3([-892.755, -5120, 642.775])
        goal_loc_br = Vector3([892.755, -5120, 0])
        goal_loc_tr = Vector3([892.755, -5120, 642.775])
        goal_loc_c = Vector3([0, -5120, 321])
    
    carball_vector3 = target_object.location - our_object.location
    carball_varray = v3_to_array(carball_vector3)
    ballgoal_vector3_c = goal_loc_c - target_object.location
    ballgoal_varray = v3_to_array(ballgoal_vector3_c)

    return angle_between(carball_varray, ballgoal_varray)

def v3_to_array(vector3):
    array = [vector3.data[0], vector3.data[1], vector3.data[2]]

    return array

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


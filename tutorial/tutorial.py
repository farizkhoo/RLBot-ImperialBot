import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

class Vector3:
    def __init__(self,data):
        self.data = data

class obj:
    def __init__(self):
        self.location = Vector3([0,0,0])
        self.velocity = Vector3([0,0,0])
        self.rotation = Vector3([0,0,0])
        self.rvelocity = Vector3([0,0,0])

        self.local_Location = Vector3([0,0,0])

class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        # Game values
        self.bot_pos = None
        self.bot_yaw = None

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location

        ball_pos = packet.game_ball.physics.location
        self.aim(ball_pos.x, ball_pos.y)

        ball_distance = self.distance_from_ball(ball_pos.x, ball_pos.y)
        if ball_distance < 100:
            self.controller.throttle = -0.5
        elif ball_distance < 1000:
            self.controller.throttle = 0.5
        else:
            self.controller.boost = True
            self.controller.throttle = 1
        
        if packet.game_cars[self.index].jumped:
            self.controller.jump = True
        else:
            self.controller.jump = False

        return self.controller

    def distance_from_ball(self, ball_pos_x, ball_pos_y):
    	distance = math.hypot(ball_pos_x - self.bot_pos.x, ball_pos_y - self.bot_pos.y)

    	return distance

	
    
import pygame
import math
import time
import os
from utility import *
pygame.font.init()

#game pictures
GRASS = scale_image(pygame.image.load(os.path.join("imgs","grass.jpg")),2.5)
TRACK = scale_image(pygame.image.load(os.path.join("imgs","track.png")),0.85)

TRACK_BORDER = scale_image(pygame.image.load(os.path.join("imgs","track-border.png")),0.85)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

#PLAYER CAR 
RED_CAR = scale_image(pygame.image.load(os.path.join("imgs","red-car.png")),0.65)
#COMPUTER OPPONENT
GREEN_CAR = scale_image(pygame.image.load(os.path.join("imgs","green-car.png")),0.65)
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

#FINISHING LINE
FINISH = pygame.image.load(os.path.join("imgs","finish.png"))
FINISH_POSITION = (130 , 270)
FINISH_MASK = pygame.mask.from_surface(FINISH)

#screen variables
WIDTH,HEIGHT = TRACK.get_width()  , TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("CAR RACING GAME!")

FPS = 60

#font variables
MAIN_FONT = pygame.font.SysFont("Arial Black", 30)
OTHER_FONT = pygame.font.SysFont("Arial Black", 20)

#OOP IMPLEMENTATION OF CAR RACING GAME!
class GameInfo :
	LEVELS = 10 
	def __init__(self , level = 1):
		self.level = level
		self.started = False
		self.level_start_time = 0
	def next_level(self):
		self.level +=1
		self.started = False
	def reset(self):
		self.level = 1
		self.started = False
		self.level_start_time = 0
	def game_finished(self):
		return self.level >self.LEVELS
	def start_level(self):
		self.started = True 
		self.level_start_time = time.time()
	def get_level_time(self):
		if not self.started:
			return 0 
		return round(time.time() - self.level_start_time)

#super class for PLAYER AND COMPUTER 
class AbstractCar:
	def __init__(self,max_vel, rotation_vel):
		self.img = self.IMG 
		self.max_vel =max_vel
		self.vel = 0
		self.rotation_vel = rotation_vel
		self.angle = 0 
		self.x,self.y = self.STARTPOS 
		self.acceleration = 0.2

	def rotate(self,left_move = False, right_move = False):
		if left_move:
			self.angle += self.rotation_vel
		elif right_move:
			self.angle -= self.rotation_vel

		 
	def draw(self,win):
		blit_rotate_centre(win , self.img, (self.x,self.y) , self.angle)

	def move(self):
		radians = math.radians(self.angle)
		vertical = math.cos(radians) * self.vel 
		horizontal = math.sin(radians) * self.vel 

		self.y -= vertical
		self.x -= horizontal

	def move_up_down(self , up = False, down = False):
		if up:
			self.vel = min(self.vel + self.acceleration,self.max_vel)
			self.move()
		elif down:
			self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
			self.move()

	def collide(self,mask, x= 0 ,y = 0):
		car_mask = pygame.mask.from_surface(self.img)
		offset = (int(self.x - x),int(self.y -y))
		point_of_intersection = mask.overlap(car_mask , offset)

		return point_of_intersection

	def reduce_speed(self):
		self.vel = max(self.vel - self.acceleration/2, 0)
		radians = math.radians(self.angle)
		vertical = math.cos(radians) * self.vel 
		horizontal = math.sin(radians) * self.vel 

		self.y -= vertical
		self.x -= horizontal


class PlayerCar(AbstractCar):
	IMG = RED_CAR
	STARTPOS = (170,200)
	def bouncer(self):
		self.vel = -self.vel
		self.move()
	def reset(self):
		self.x,self.y = self.STARTPOS
		self.vel = 0
		self.angle = 0

class ComputerCar(AbstractCar):
	IMG = GREEN_CAR
	STARTPOS = (140,200)
	def __init__(self, max_vel , rotation_vel , path):
		super().__init__(max_vel , rotation_vel)
		self.current_point = 0
		self.vel = max_vel
		self.path = path
	def draw(self,win):
		super().draw(win)

	def calculate_angle(self):
		target_x , target_y = self.path[self.current_point]
		x_diff = self.x - target_x
		y_diff = self.y - target_y
		if y_diff ==0:
			desired_radian = math.pi /2
		else:
			desired_radian = math.atan(x_diff / y_diff)

		if target_y > self.y:
			desired_radian +=math.pi

		difference_in_angle = self.angle - math.degrees(desired_radian)
		if difference_in_angle> 180:
			difference_in_angle -=360 
		if difference_in_angle>0:
			self.angle -=min(self.rotation_vel,abs(difference_in_angle))
		else:
			self.angle +=min(self.rotation_vel,abs(difference_in_angle))

	def update_path(self):
		target = self.path[self.current_point]
		rect = pygame.Rect(self.x ,self.y , self.img.get_width() , self.img.get_height())
		if rect.collidepoint(*target):
			self.current_point +=1

	def move(self):
		if self.current_point >= len(self.path) :
			return 
		else:
			self.calculate_angle()
			self.update_path()
			super().move()
	def reset(self ,max_vel = 2):
		self.x ,self.y = self.STARTPOS
		self.current_point = 0
		self.vel = max_vel	
		self.angle = 0	

def draw(win, images,player_car,computer_car, game_info):
	for img,pos in images:
		win.blit(img,pos)
	level_text = OTHER_FONT.render(f"LEVEL {game_info.level}",1, (255,255,255))
	win.blit(level_text, (10, HEIGHT- level_text.get_height()-150))

	time_text = OTHER_FONT.render(f"TIME {game_info.get_level_time()} s",1, (255,255,255))
	win.blit(time_text, (10, HEIGHT- time_text.get_height()-120))

	vel_text = OTHER_FONT.render(f"VEL : {round(player_car.vel * 3.6 *5  ,5)} km/h",1, (255,255,255))
	win.blit(vel_text, (10, HEIGHT- vel_text.get_height()-90))
	
	player_car.draw(win)
	computer_car.draw(win)
	pygame.display.update()

def main():
	run = True
	clock = pygame.time.Clock()
	images = [(GRASS, (0, 0)) ,(TRACK, (0, 0)), (FINISH, FINISH_POSITION) , (TRACK_BORDER,(0,0))]
	player_car = PlayerCar(3.5,4)
	computer_car = ComputerCar(2.5,4,PATH)
	game_info = GameInfo()

	#mainloop for the game 
	while run:
		clock.tick(FPS)
		draw(WIN,images, player_car,computer_car, game_info)
		while not game_info.started:
			blit_text_center(WIN, MAIN_FONT ,f"PRESS ANY KEY TO START LEVEL {game_info.level}!")
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				if event.type == pygame.KEYDOWN:
					game_info.start_level()
			pygame.display.update()

		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break

		#MOVING THE COMPUTER CAR
		computer_car.move()

		#COMMANDING KEYS FOR MOVING THE PLAYER
		keys = pygame.key.get_pressed()
		moved = False

		if keys[pygame.K_LEFT]:
			player_car.rotate(left_move = True)
		if keys[pygame.K_RIGHT]:
			player_car.rotate(right_move = True)
		if keys[pygame.K_UP]:
			player_car.move_up_down(up = True)
			moved = True
		if keys[pygame.K_DOWN]:
			player_car.move_up_down(down = True)
			moved = True

		if not moved:
			player_car.reduce_speed()

		if player_car.collide(TRACK_BORDER_MASK) != None:
			if player_car.collide(TRACK_BORDER_MASK) != None:
				player_car.bouncer()
		finish_line_point_of_intersection = player_car.collide(FINISH_MASK, *FINISH_POSITION)

		if computer_car.collide(FINISH_MASK,*FINISH_POSITION):
			computer_car.reset(computer_car.max_vel)
			player_car.reset()
			game_info.started = False	

		if finish_line_point_of_intersection != None :
			if finish_line_point_of_intersection[1] == 0:
				player_car.bouncer()
			else:
				computer_car.reset(computer_car.max_vel+0.1)
				player_car.reset()
				game_info.next_level()
			
		if game_info.game_finished():
			blit_text_center(WIN, MAIN_FONT, "You won the game!")
			pygame.time.wait(5000)
			game_info.reset()
			player_car.reset()
			computer_car.reset()
			computer_car.current_point = len(PATH)

	pygame.quit()

if __name__ == '__main__':
	main()
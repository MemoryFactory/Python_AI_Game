import pygame
from pygame.locals import *
import random

class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y):
		super().__init__() #运行父类初始化
		self.images = [] #由3张图片组成小鸟飞行动画
		self.index = 0 #用来选取存在images里的不同图片
		self.counter = 0 #用于帧数累加计算，用来控制小鸟图片变化的时间，使翅膀扇动频率变慢
		self.vel = 0
		self.cap = 10
		self.flying = False
		self.failed = False
		'''
		flying failed
		0      0       游戏开始，小鸟处于准备飞行状态
		1      0       游戏进行，小鸟处于飞行状态
		1      1       碰撞导致游戏失败，小鸟处于掉落状态
		0      1       游戏失败停止，小鸟落到地面
		'''
		self.clicked = False #用来判断是否被单击过，避免按住不放
		for num in range (1, 4):
			img = pygame.image.load(f"resources/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.wing = pygame.mixer.Sound('resources/wing.wav')

	def handle_input(self):
		if pygame.mouse.get_pressed()[0] == 1 and not self.clicked : #鼠标左键被单击，并且之前没被单击过
			self.clicked = True
			self.vel = -1 * self.cap #速度变量设为-10，使小鸟向上移动
			self.wing.play()
		if pygame.mouse.get_pressed()[0] == 0: #鼠标左键被松开
			self.clicked = False

	def animation(self): #实现小鸟扇动翅膀和上升时仰头、下降时低头的动画
		flap_cooldown = 5
		self.counter += 1
		if self.counter > flap_cooldown: #每5帧更换一次图片
			self.counter = 0
			self.index = (self.index + 1) % 3
			self.image = self.images[self.index]
		self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2) #第二个参数为旋转角度，利用速度变量来算出角度

	def touch_ground(self):
		return self.rect.bottom >= Game.ground_y

	def update(self):
		if self.flying : 
			self.handle_input()
			self.vel += 0.5 #增加向下的速度变量模拟重力加速度
			if self.vel > 8:
				self.vel = 8
			if not self.touch_ground():
				self.rect.y += int(self.vel) #没有碰到地面就更新小鸟的纵坐标

		if not self.failed:
			self.animation()
		else:
			#point the bird at the ground
			self.image = pygame.transform.rotate(self.images[self.index], -90)



class Pipe(pygame.sprite.Sprite):
	scroll_speed = 4 #钢管移动速度
	pipe_gap = 180 #上下钢管间的空隙

	def __init__(self, x, y, is_top):
		super().__init__()
		self.passed = False #钢管是否被小鸟穿越
		self.is_top = is_top #判断是否为上方钢管
		self.image = pygame.image.load("resources/pipe.png")
		self.rect = self.image.get_rect()

		if is_top :
			self.image = pygame.transform.flip(self.image, False, True) #沿y轴反转钢管图片
			self.rect.bottomleft = [x, y - Pipe.pipe_gap // 2]
		else:
			self.rect.topleft = [x, y + Pipe.pipe_gap // 2]

	def update(self):
		self.rect.x -= Pipe.scroll_speed
		if self.rect.right < 0:
			self.kill() #超出左边界删除这个钢管对象

class Button:

	def __init__(self, x, y):
		self.image = pygame.image.load('resources/restart.png')
		self.rect = self.image.get_rect(centerx=x,centery=y)

	def pressed(self, event):
		pressed = False
		if event.type == MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(pos): #判断坐标值是否在边框内部
				pressed = True
		return pressed
 
	def draw(self,surface):
		surface.blit(self.image, self.rect)

class Game():
	ground_y = 650
	
	def __init__(self,Width=600,Height=800):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.ground_x = 0
		self.score = 0
		self.pipe_counter = 0 #生成钢管时间间隔计数
		self.observed = dict() #创建字典，用来保存没有被小鸟穿越且最靠近小鸟的右侧钢管的间隙坐标
		self.Clock = pygame.time.Clock()
		self.fps = 60
		self.font = pygame.font.Font('resources/LuckiestGuy-Regular.ttf', 28)
		self.images = self.loadImages() #字典，保持背景图片、大地图片
		self.sounds = self.loadSounds() #字典，保存碰撞音效、得分音效
		self.pipe_group = pygame.sprite.Group() #保存一组管道角色
		self.bird_group = pygame.sprite.Group() #保存一组小鸟角色（实际只存了一个）
		self.flappy = Bird(100, self.ground_y // 2)
		self.bird_group.add(self.flappy)
		self.new_pipes(time=0) #此时设置time为0是为了立刻生成一组钢管
		self.button = Button(self.Win_width//2 , self.Win_height//2 )
		pygame.display.set_caption('Flappy Bird')
		pygame.mixer.music.load('resources/BGMUSIC.mp3')
		pygame.mixer.music.play(-1)
	
	def loadImages(self):
		background = pygame.image.load('resources/bg.png')
		ground = pygame.image.load('resources/ground.png')
		return {'bg':background, 'ground':ground}
	
	def loadSounds(self):
		hit = pygame.mixer.Sound('resources/hit.wav')
		point = pygame.mixer.Sound('resources/point.wav')
		return {'hit':hit, 'point':point}

	def reset_game(self):
		self.pipe_group.empty()
		self.new_pipes(time=0)
		self.bird_group.empty()
		self.flappy = Bird(100, self.ground_y // 2)
		self.bird_group.add(self.flappy)
		self.score = 0
		self.observed = dict()
		pygame.mixer.music.play(-1)

	def start_flying(self,event):
		if (event.type == pygame.MOUSEBUTTONDOWN 
			and not self.flappy.flying
			and not self.flappy.failed): #判断处于等待游戏开始状态再设置小鸟处于飞的状态
			self.flappy.flying = True

	def game_restart(self,event):
		if (self.flappy.failed 
			and self.button.pressed(event)): #处于游戏失败，且点击了restart按键，重置游戏
				self.reset_game()	

	def handle_collision(self):
		if (pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False) #组碰撞，两个角色组里任何角色碰撞返回真
			or self.flappy.rect.top < 0 
			or self.flappy.rect.bottom >= Game.ground_y):
			self.flappy.failed = True
			self.sounds['hit'].play()
			pygame.mixer.music.stop()

	def ground_update(self):
		self.ground_x -= Pipe.scroll_speed
		if abs(self.ground_x) > 35:
			self.ground_x = 0

	def new_pipes(self, time = 90):
		self.pipe_counter += 1
		if self.pipe_counter >= time: #计数超过90，生成一组钢管
			pipe_height = random.randint(-150, 150)
			top_pipe = Pipe(self.Win_width,  self.ground_y // 2 + pipe_height, True)
			btm_pipe = Pipe(self.Win_width, self.ground_y // 2 + pipe_height, False)
			self.pipe_group.add(top_pipe)
			self.pipe_group.add(btm_pipe)
			self.pipe_counter = 0

	def get_pipe_dist(self): #用于计算、保持passed的观测值，passed用来记录当前钢管是否被小鸟穿越，False为没有穿越
		pipe_2 = [pipe for pipe in self.pipe_group.sprites() if pipe.passed==False][:2] #取当前处于小鸟右侧钢管最靠近小鸟的前两根
		for pipe in pipe_2: #获取改组钢管的中间间隙的右侧上下坐标
			if pipe.is_top:
				self.observed['pipe_dist_right'] = pipe.rect.right 
				self.observed['pipe_dist_top'] = pipe.rect.bottom
			else:
				self.observed['pipe_dist_bottom'] = pipe.rect.top
			
	def check_pipe_pass(self):
		if self.flappy.rect.left >= self.observed['pipe_dist_right']:
			self.score += 1
			self.pipe_group.sprites()[0].passed = True
			self.pipe_group.sprites()[1].passed = True
			self.sounds['point'].play()

	def pipe_update(self):
		self.new_pipes()
		self.pipe_group.update()
		if len(self.pipe_group)>0:
			self.get_pipe_dist()
			self.check_pipe_pass()

	def draw_text(self,text,color,x,y):
		img = self.font.render(text, True, color)
		self.surface.blit(img,(x,y))

	def draw(self):
		self.surface.blit(self.images['bg'],(0,0))
		self.pipe_group.draw(self.surface) #绘制钢管组角色
		self.bird_group.draw(self.surface) #绘制小鸟组角色
		self.surface.blit(self.images['ground'],(self.ground_x,self.ground_y))
		self.draw_text(f'score: {self.score}', (255, 255, 255), 20, 20)	

	def check_failed(self):
		if self.flappy.failed:
			pygame.mixer.music.stop()
			if self.flappy.touch_ground():
				self.button.draw(self.surface)
				self.flappy.flying = False

	def play_step(self):
		game_over = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_over = True
			self.start_flying(event)
			self.game_restart(event)
		self.bird_group.update()
		if not self.flappy.failed and self.flappy.flying:
			self.handle_collision()
			self.pipe_update()
			self.ground_update()
		self.draw()
		self.check_failed()
		pygame.display.update()
		self.Clock.tick(self.fps)
		return game_over, self.score 

if __name__ == '__main__':
	game = Game()
	while True:
		game_over, score  = game.play_step()
		if game_over == True:
			break

	print('Final Score', score)
	pygame.quit()

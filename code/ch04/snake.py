import pygame
import random
from collections import namedtuple
from pygame.locals import K_RIGHT,K_LEFT,K_UP,K_DOWN,QUIT

Position = namedtuple('Point', 'x, y') #定义带名字的元组，方便用.x和.y来使用坐标值

class Direction: #不需要实例，直接使用类属性
    right = 0
    left = 1
    up = 2
    down = 3

class Snake:

    def __init__(self,block_size):
        self.blocks=[] #用列表储存蛇头蛇身坐标
        self.blocks.append(Position(20,15)) #放蛇头
        self.blocks.append(Position(19,15)) #放一个蛇身
        self.block_size = block_size
        self.current_direction = Direction.right #记录当前移动方向
        self.image = pygame.image.load('snake.png')
    
    def move(self):
        if (self.current_direction == Direction.right):
            movesize = (1, 0)
        elif (self.current_direction == Direction.left):
            movesize = (-1, 0)
        elif (self.current_direction == Direction.up):
            movesize = (0, -1)
        else:
            movesize = (0, 1)
        head = self.blocks[0]
        new_head = Position(head.x + movesize[0], head.y + movesize[1]) #当前蛇头坐标朝移动方向增加1，获得新的坐标
        self.blocks.insert(0,new_head) #在移动方向增加一个新蛇头，相当于移动一格


    def handle_input(self):
        keys = pygame.key.get_pressed()      
        if (keys[K_RIGHT] and self.current_direction != Direction.left):
            self.current_direction = Direction.right
        elif (keys[K_LEFT] and self.current_direction != Direction.right):
            self.current_direction = Direction.left
        elif(keys[K_UP] and self.current_direction != Direction.down):
            self.current_direction = Direction.up
        elif(keys[K_DOWN] and self.current_direction != Direction.up):
            self.current_direction = Direction.down
        self.move()

    def draw(self,surface,frame):
        for index, block in enumerate(self.blocks):
            positon = (block.x * self.block_size, 
                    block.y * self.block_size) #计算绘图的位置坐标，格子数×格子边长的像素数
            if index == 0:
                src = (((self.current_direction * 2) + frame) * self.block_size,
                         0, self.block_size, self.block_size) #通过current_direction来选择对应方向的蛇头小图片，frame用来切换蛇头张嘴和闭嘴的小图片
            else:
                src = (8 * self.block_size, 0, self.block_size, self.block_size)
            surface.blit(self.image, positon, src) #第三个参数src用来切割源图片的切割坐标（左上角横坐标，左上角纵坐标，长尺寸，宽尺寸）


class Berry:

    def __init__(self,block_size):
        self.block_size = block_size
        self.image = pygame.image.load('berry.png')
        self.position = Position(1, 1)     

    def draw(self,surface):
        rect = self.image.get_rect()
        rect.left = self.position.x * self.block_size
        rect.top = self.position.y * self.block_size
        surface.blit(self.image, rect)


class Wall:

    def __init__(self,block_size):
        self.block_size = block_size
        self.map = self.load_map('map.txt') #map.txt用数字来描述地图，1代表放置墙，其他数字代表不放
        self.image = pygame.image.load('wall.png')

    def load_map(self,fileName):
        with open(fileName,'r') as map_file:
            content = map_file.readlines()
            content =  [list(line.strip()) for line in content] #嵌套列表[[行1],[行2],...,[行n]]
            # print(content)
        return content  

    def draw(self,surface):
        for row, line in enumerate(self.map):
            for col, char in enumerate(line):
                if char == '1':
                    position = (col*self.block_size,row*self.block_size)
                    surface.blit(self.image, position)     


class Game:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    def __init__(self,Width=640, Height=480):
        pygame.init()
        self.block_size = 16
        self.Win_width , self.Win_height = (Width, Height)
        self.Space_width = self.Win_width//self.block_size-2 #格子的宽度数
        self.Space_height = self.Win_height//self.block_size-2 #格子的高度数
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.score = 0
        self.frame = 0
        self.running = True
        self.Clock = pygame.time.Clock()
        self.fps = 10
        self.font = pygame.font.Font(None, 32)
        self.snake = Snake(self.block_size)
        self.berry = Berry(self.block_size)
        self.wall = Wall(self.block_size)
        self.position_berry()

    def position_berry(self): #在格子里随机放置果子
        bx = random.randint(1, self.Space_width)
        by = random.randint(1, self.Space_height)
        self.berry.position = Position(bx, by)
        if self.berry.position in self.snake.blocks:
            self.position_berry()

    # handle collision
    def berry_collision(self):
        head = self.snake.blocks[0]
        if (head.x == self.berry.position.x and
            head.y == self.berry.position.y): #碰到果子，重新随机放置一个果子，分数加1
            self.position_berry()
            self.score += 1
        else:
            self.snake.blocks.pop() #没碰到果子，蛇尾减1个

    def head_hit_body(self):
        head = self.snake.blocks[0]
        if head in self.snake.blocks[1:]:
            return True 
        return False

    def head_hit_wall(self):
        head = self.snake.blocks[0]
        if (self.wall.map[head.y][head.x] == '1'):
            return True
        return False


    def draw_data(self):
        text = "score = {0}".format(self.score)
        text_img = self.font.render(text, 1, Game.WHITE)
        text_rect = text_img.get_rect(centerx=self.surface.get_width()/2, top=32)
        self.surface.blit(text_img, text_rect)
    
    
    def draw(self):
        self.surface.fill(Game.BLACK)
        self.wall.draw(self.surface)
        self.berry.draw(self.surface)
        self.snake.draw(self.surface,self.frame)
        self.draw_data()
        pygame.display.update()

    # main loop 
    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            self.frame = (self.frame + 1) % 2 #通过0、1变化来控制蛇头张嘴闭嘴动画
            self.snake.handle_input()   #蛇头方向
            self.berry_collision()
            if self.head_hit_wall() or self.head_hit_body():
                print('Final Score', self.score)
                self.running = False

            self.draw()
            self.Clock.tick(self.fps)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.play()

import pygame
from pygame.locals import *
import random
from  math import radians, sin, cos, asin

class Bat:
    def __init__(self,playerY=540):
        self.image = pygame.image.load('bat.png')
        self.rect = self.image.get_rect()
        self.mousey = playerY

    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def update(self,win_width):
        mousex, _ = pygame.mouse.get_pos()
        if (mousex > win_width - self.rect.width): #横坐标为左上角，如果左上角到右边框距离小于球拍的宽度就需要把横坐标设置为到右边框一个拍长距离的位置
            mousex = win_width - self.rect.width
        self.rect.topleft = (mousex, self.mousey)


# ball init
class Ball:
    
    def __init__(self,win_width):
        self.image = pygame.image.load('ball.png')
        self.rect = self.image.get_rect()
        self.reset(win_width)

    def reset(self,win_width,startY=220,speed=5, degree=45):
        self.served = False #表示球是否移动，False为静止
        self.positionX = random.randint(0,win_width)
        self.positionY = startY
        self.rect.topleft = (self.positionX, self.positionY)
        self.speed = speed
        self.speedX = self.speed * sin(radians(degree)) #横轴移动分量
        self.speedY = self.speed * cos(radians(degree)) #纵轴移动分量
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self,win_width):
        if self.served:    
            self.positionX += self.speedX
            self.positionY += self.speedY
            self.rect.topleft = (self.positionX, self.positionY)

            if (self.positionY <= 0):
                self.positionY = 0
                self.speedY *= -1

            if (self.positionX <= 0):
                self.positionX = 0
                self.speedX *= -1

            if (self.positionX >=win_width - self.rect.width):
                self.positionX = win_width - self.rect.width
                self.speedX *= -1


class Bricks:

    def __init__(self,row=5, col=12):
        self.image = pygame.image.load('brick.png')
        self.rect = self.image.get_rect()
        self.contains = [] #用列表存储每块砖的坐标和尺寸
        for y in range(row):
            brickY = (y * 24) + 100
            for x in range(col):
                brickX = (x * 31) + 214
                rect = Rect(brickX, brickY, self.rect.width, self.rect.height)
                self.contains.append(rect)

    def draw(self, surface):
        for rect in self.contains:
            surface.blit(self.image, rect)


class Game:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self, Width=800,Height=600):
        pygame.init()
        self.Win_width , self.Win_height = (Width, Height)
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.bat = Bat()
        self.ball = Ball(self.Win_width) 
        self.bricks = Bricks() 
        self.font = pygame.font.SysFont('microsoftyahei',26)
        self.score = 0
        self.Clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        pygame.display.set_caption('Bricks')
        

    def bat_collision(self): #球和球板的碰撞检测
        if self.ball.rect.colliderect(self.bat.rect):
            self.ball.rect.bottom = self.bat.mousey #把球置于球板上方，避免球板侧面与球碰撞情况时异常
            self.ball.speed += 0.1
            diff_x = self.ball.rect.centerx - self.bat.rect.centerx #球中心到球板中心的横向距离
            diff_ratio = min(0.95,abs(diff_x)/(0.5*self.bat.rect.width)) #计算比例，为避免侧面碰撞时出现大于1的情况，最多取到0.95
            theta = asin(diff_ratio) #反正弦函数获取角度值，diff_ratio越小则角度值越小
            self.ball.speedX = self.ball.speed * sin(theta)
            self.ball.speedY = self.ball.speed * cos(theta)
            self.ball.speedY *= -1 #球转向上飞
            if (diff_x<0 and self.ball.speedX>0) or (diff_x>0 and self.ball.speedX<0): #控制球反弹方向，碰到球板左侧往左反弹，右侧往右反弹
                self.ball.speedX *= -1
  
    def bricks_collision(self): #球和砖块的碰撞检测
        brickHitIndex = self.ball.rect.collidelist(self.bricks.contains) #collidelist函数用来检测一个rect对象和一组rect对象之间的碰撞，没有碰撞返回-1，发生碰撞返回列表索引
        if brickHitIndex >= 0:
            brick = self.bricks.contains[brickHitIndex]
            if (self.ball.rect.centerx > brick.right or 
                self.ball.rect.centerx < brick.left):
                self.ball.speedX *= -1 #左右侧碰撞则球横坐标反转
            else:
                self.ball.speedY *= -1 #上下侧碰撞则球横坐标反转
            del (self.bricks.contains[brickHitIndex]) #从contains里删除碰撞的砖块
            self.score +=1
            if len(self.bricks.contains)==0:
                self.running = False 
    
    def check_failed(self):
        if self.ball.rect.bottom >= self.Win_height:
            self.ball.reset(self.Win_width)
            self.score = 0

    def draw_data(self): #绘制分数
        score_text = "得分：{score}".format(score=self.score)
        score_img = self.font.render(score_text, 1, Game.WHITE)
        score_rect = score_img.get_rect(centerx=self.Win_width//2, top=5)
        self.surface.blit(score_img, score_rect)

    def draw(self): #绘制所有元素
        self.surface.fill(Game.BLACK)
        self.draw_data()
        self.bricks.draw(self.surface)
        self.bat.draw(self.surface)
        self.ball.draw(self.surface)
        pygame.display.update()


    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                if event.type == MOUSEBUTTONUP and not self.ball.served:
                    self.ball.served = True

            self.bat.update(self.Win_width)
            self.ball.update(self.Win_width)
            self.check_failed()
            self.bat_collision()
            self.bricks_collision()
            self.draw()
            self.Clock.tick(self.fps)

        pygame.quit()
        print('Good Job! Final Score:', self.score)


if __name__ == '__main__':
    game = Game()
    game.play()

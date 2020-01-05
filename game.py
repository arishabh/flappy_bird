import pygame
import time
import random

blue = (0,0,255)
green = (0,205,0)
yellow = (255,255,0)
back = (175, 238, 238)

class Bird:
    acc = 1
    def __init__(self, x=100, y=300):
        self.x = x
        self.y = int(y)
        self.vel = 0
        self.size = 40
        self.img = pygame.transform.scale(pygame.image.load('bird.png'), (50,37))
        
    def draw(self, screen):
        img = self.img
        if self.vel < -1:
            img = pygame.transform.rotate(self.img, 45)
        elif self.vel > 1:
            img = pygame.transform.rotate(self.img, -45)
        center = img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        screen.blit(img, center)

    def tick(self):
        self.vel += self.acc
        self.y += int(self.vel)

    def jump(self):
        self.vel = -10

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    def __init__(self, y=768, rand=768):
        self.x = 576
        self.width = 85
        self.height = min(random.randint(140, rand), 527)
        self.y = self.height-y
        self.img = pygame.transform.scale(pygame.image.load('pipe.png'), (93, 527))

    def draw(self, screen):
        img = self.img
        if(self.y > 0):
            img = pygame.transform.flip(self.img, True, True)
        screen.blit(img, (self.x, self.y))

    def tick(self):
        self.x -= 5

    def collided(self, b):
        # if(b.x+b.size>self.x and b.x-b.size<self.x+self.width):
        #     if(self.y > 0  and b.y+b.size > self.y):
        #         return True
        #     if(self.y <= 0 and b.y-b.size<self.y+self.height):
        #         return True
        bird_mask = b.get_mask()
        pipe_mask = pygame.mask.from_surface(self.img)
        
        offset = (self.x - b.x, self.y-b.y)
        point = bird_mask.overlap(pipe_mask, offset)

        return point != None
        

class PipePair:
    dist = 100
    min_len = 100
    def __init__(self):
        self.top_pipe = Pipe(y=527, rand=(768-(self.min_len+self.dist)))
        self.bot_pipe = Pipe()
        self.bot_pipe.height = 768-(self.top_pipe.height+self.dist)
        self.bot_pipe.y = 768-self.bot_pipe.height

    def draw(self, screen):
        self.top_pipe.draw(screen)
        self.bot_pipe.draw(screen)

    def tick(self):
        self.top_pipe.tick()
        self.bot_pipe.tick()

    def collided(self, p):
        return self.top_pipe.collided(p) or self.bot_pipe.collided(p)

pygame.init()

quit = False
dead = False
size = [576, 768]

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()
bird = Bird(y=size[1]/2)
ticks = 0
score = 0
highscore = 0
pipes = []
dead_pipes = []
back = pygame.transform.scale2x(pygame.image.load('back.png'))

def show_score(score, hightscore):
    font = pygame.font.Font('dpcomic.ttf', 50)
    mes = font.render(str(score), True, (0,0,0))
    screen.blit(mes, [40, 40])
    mes = font.render(str(highscore), True, (0,0,0))
    screen.blit(mes, [40, 80])

def dead_mes():
    font = pygame.font.Font('dpcomic.ttf', 45)
    mes = font.render("You died, hit SPACE to continue", True, (255,255,255))
    screen.blit(mes, [20, 384])

while not quit:
    for pipe in pipes:
        if(pipe.collided(bird) or bird.y >= size[1]):
            dead_mes()
            pygame.display.update()
            time.sleep(0.4)
            dead = True
    if(ticks%75 == 0):
        pipes.append(PipePair())
        counted = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                quit = True
            if event.key == pygame.K_SPACE:
                if dead:
                    bird = Bird()
                    ticks = -1
                    highscore = max(score, highscore)
                    score = 0
                    pipes = []
                    dead = False
                bird.jump()

    if dead: continue
    bird.tick()
    screen.blit(back, (0,0))
    for pipe in pipes: 
        pipe.tick()
        pipe.draw(screen)
        if(pipe.top_pipe.x < -100): dead_pipes.append(pipe)
    for pipe in dead_pipes:
        if pipe in pipes: pipes.remove(pipe)
    if(len(pipes)>1 and pipes[-2].top_pipe.x+pipes[-2].top_pipe.width < bird.x and not counted):
        score += 1
        counted = True
    show_score(score, highscore)
    bird.draw(screen)
    pygame.display.update()
    ticks += 1
    clock.tick(30)


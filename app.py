import pygame
import neat
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

def show_score(score, highscore, screen):
    font = pygame.font.Font('dpcomic.ttf', 50)
    mes = font.render(str(score), True, (0,0,0))
    screen.blit(mes, [40, 40])
    mes = font.render(str(highscore), True, (0,0,0))
    screen.blit(mes, [40, 80])

def game(genomes, config):
    quit = False
    nets = []
    ge = []
    birds = []
    ticks = 0
    score = 0
    highscore = 0
    pipes = [PipePair()]
    dead_pipes = []
    
    pygame.init()
    size = [576, 768]
    back = pygame.transform.scale2x(pygame.image.load('back.png'))
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Flappy Bird")

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(y=size[1]/2))
        g.fitness = 0
        ge.append(g)

    clock = pygame.time.Clock()
    while not quit:
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].top_pipe.x+pipes[0].top_pipe.width:
                pipe_ind = 1
        
        else:
            quit = True
            break

        for x,bird in enumerate(birds):
            bird.tick()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y-pipes[pipe_ind].top_pipe.height), abs(bird.y-pipes[pipe_ind].bot_pipe.y)))    

            if output[0] > 0.5:
                bird.jump()
        
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if(pipe.collided(bird) or bird.y >= size[1] or bird.y <= 0):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                add_pipe = pipe.top_pipe.x+pipe.top_pipe.width < bird.x and not add_pipe

        if add_pipe:
            pipes.append(PipePair())
            score += 1
            for g in ge:
                g.fitness += 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit = True
                if event.key == pygame.K_SPACE:
                    bird.jump()

        screen.blit(back, (0,0))
        for pipe in pipes: 
            pipe.tick()
            pipe.draw(screen)
            if(pipe.top_pipe.x + pipe.top_pipe.width < 0): dead_pipes.append(pipe)
        for pipe in dead_pipes:
            if pipe in pipes: pipes.remove(pipe)
        show_score(score, highscore, screen)
        for bird in birds:
            bird.draw(screen)
        pygame.display.update()
        ticks += 1
        clock.tick(100)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(game,50)


if __name__ =='__main__':
    config_path = "config.txt"
    run(config_path)

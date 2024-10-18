import pygame as pg
import random
import math

pg.init()

# screen dimension constants
WIDTH, HEIGHT = 800, 700
CENTER_X, CENTER_Y = (WIDTH / 2), (HEIGHT / 2)

#color constants
WHITE = ((235, 235, 235))
RED = ((186, 13, 13))
BLUE = ((13, 42, 186))

#other constants
INIT_SPEED = 4
PADDLE_HEIGHT = 110
PADDLE_WIDTH = 20
HALF_PADDLE_HEIGHT = PADDLE_HEIGHT/ 2
DISCO_TICK = 20 #every ___ frames, color changes while disco

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Pong")

FPS = 60
clock = pg.time.Clock()

player_score = 0
computer_score = 0


class paddle:
    def __init__(self, x_pos, y_pos, color=WHITE, speed=12, height=PADDLE_HEIGHT, width=PADDLE_WIDTH, is_player=False):
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.speed = speed
        self.height = height
        self.width = width
        self.is_player = is_player

        # rectangle/drawing objects
        self.rect = pg.Rect(x_pos, y_pos, width, height)
        self.rect_draw = pg.draw.rect(screen, self.color, self.rect)
    
    def set_speed(self, s):
        self.speed = s
    
    def get_x(self):
        return self.x_pos
    
    def get_y(self):
        return self.y_pos
    
    def get_rect(self):
        return self.rect_draw

    def move_toward(self, target_y):
        y = self.y_pos + HALF_PADDLE_HEIGHT #vertical center of paddle
        y_mod = 0

        #move down
        if (y < target_y):
            y_mod = 1

        #if ball is close to center of paddle, try to move less
        #than speed so the paddle doesn't overshoot
        elif(y <= target_y + 10 and y >= target_y - 10): 
            if (y == target_y):
                y_mod = 0
            else:
                y_mod = (target_y - y)/self.speed
    
        #move up
        else: 
            y_mod = -1

        self.update(y_mod)

    
    def display(self):
        self.rect_draw = pg.draw.rect(screen, self.color, self.rect)

    def update(self, y_mod):
        self.y_pos += self.speed*y_mod
            
        # prevent from leaving bounds
        if(self.y_pos < 0):
            self.y_pos = 0
        elif (self.y_pos + self.height >= HEIGHT):
            self.y_pos = HEIGHT - self.height

        # update self rectangle
        self.rect = (self.x_pos, self.y_pos, self.width, self.height)


player_paddle = paddle(0, CENTER_Y - HALF_PADDLE_HEIGHT, speed = 10, is_player=True)
computer_paddle = paddle(WIDTH - 20, CENTER_Y - HALF_PADDLE_HEIGHT, speed = 8)


class ball:
    def __init__(self, sz, x, y, c = RED, sp = INIT_SPEED):
        self.size = sz
        self.speed_base = sp
        self.x_pos = x
        self.y_pos = y
        self.color = c
        self.disco = False

        #allow for change of direction
        self.x_speed = 1
        self.y_speed = 1

        # rectangle/draw objects
        self.rect = pg.Rect(x, y, sz, sz)
        self.rect_draw = pg.draw.rect(screen, self.color, self.rect)

    def get_y(self):
        return self.y_pos
    
    def get_rect(self):
        return self.rect_draw
    
    def inc_speed(self):
        cos_ratio = self.speed_base / self.x_speed
        sin_ratio = self.speed_base / self.y_speed

        self.speed_base += 1
        self.x_speed = self.speed_base / cos_ratio
        self.y_speed = self.speed_base / sin_ratio
    
    def bounce(self):
        self.x_speed = -self.x_speed
        
        #randomize bouncing within 20%, otherwise it's very predictable
        #I acknowledge physics doesn't work like this 
        if (self.x_speed > 0):
            self.x_speed = random.uniform(self.x_speed*0.80, self.x_speed*1.20)
        else:
            self.x_speed = random.uniform(self.x_speed*1.20, self.x_speed*0.80)

    def reset(self):
        self.x_pos = WIDTH/2 - self.size
        self.y_pos = HEIGHT/2 - self.size
        self.speed_base = INIT_SPEED

        #time for trigonometry!!
        #full explanation just in case:
            
        #for speed to remain constant while the
        #direction changes randomly. Imagine
        #the speed as the hypotenuse of a right 
        #triangle where the ball is at one end
        #of the hypotenuse. to keep the hypotenuse
        #the same length while randomly changing
        #the triangle, we can randomly generate
        #the x value of the speed and then 
        #derive the y value from that to keep
        #the size of the hypotenuse constant. 

        #x should be > y so ball bounces more or less
        #toward one of the paddles
        self.x_speed = random.uniform(self.speed_base*0.6, self.speed_base)

        #set x direction
        x_dir = random.randint(1, 2)
        if (x_dir == 2):
            x_dir = -1

        self.x_speed *= x_dir    
    
        if (self.x_speed == 0 or self.x_speed == self.speed_base or self.x_speed == -self.speed_base): #can't be a right triangle if one of the sides l = 0 or l = hypotenuse
            self.reset()

        #a = sqrt(c^2 - b^2)
        self.y_speed = math.sqrt(math.pow(self.speed_base, 2) - math.pow(self.x_speed, 2))
        
        #randomize y direction, since by sqrt the generated
        #value will only ever be positive
        y_dir = random.randint(1, 2)
        if (y_dir == 2):
            y_dir = -1

        self.y_speed *= y_dir

    def display(self):
        self.rect_draw = pg.draw.rect(screen, self.color, self.rect)

    def update(self):
        global player_score, computer_score

        self.x_pos += self.x_speed
        self.y_pos += self.y_speed

        #border hit conditions & reverse direction to bounce

        #if ball is on left border, computer scores
        if(self.x_pos <= 0):
           computer_score += 1
           pg.time.wait(300)
           self.reset()
           print("COM: " + str(computer_score) + "  PLY:" + str(player_score))
        #if ball is on right border, player score
        if (self.x_pos >= WIDTH - self.size):
            player_score += 1
            pg.time.wait(300)
            self.reset()
            print("COM: " + str(computer_score) + "  PLY:" + str(player_score))
        #if ball is heading offscreen vertically, reverse its direction
        if ((self.y_pos <= 0 and self.y_speed <= 0) or (self.y_pos >= HEIGHT - self.size and self.y_speed >= 1)):
            self.y_speed = -self.y_speed


        self.rect = pg.Rect(self.x_pos, self.y_pos, self.size, self.size)

    def get_disco(self):
        return self.disco

    def toggle_disco(self):
            self.disco = not self.disco
            if(not self.disco):
                self.color = WHITE
    #randomizes color with random RGB values
    def disco_time(self):
        new_red = random.randint(0, 255)
        new_blue = random.randint(0, 255)
        new_green = random.randint(0, 255)

        self.color = ((new_red, new_blue, new_green))


game_ball = ball(20, CENTER_X - 20, CENTER_Y - 20)

def display_score(p_score, c_score):
    game_font = pg.font.SysFont("arial", 45, bold=True)
    font_surface = game_font.render((str(p_score) + " | " + str(c_score)), True, BLUE)
    text_rect = font_surface.get_rect()
    text_rect.center = (WIDTH/2, 30)
    screen.blit(font_surface, text_rect)

#contains game logic
def game_loop():

    running = True
    #outside of main loop to provide a few milliseconds
    #for user to process screen before game beings 
    screen.fill((0, 0, 0))
    player_paddle.display()
    computer_paddle.display() 
    game_ball.reset()  
    game_ball.display()         
    pg.display.update()
    pg.time.wait(700)
    disco_count = 0

    while(running):
        #black background
        screen.fill((0, 0, 0))

        #handle quit
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        y_mod = 0

        #handle disco color change
        if (game_ball.get_disco()):
            if (disco_count == DISCO_TICK):
                game_ball.disco_time()
                disco_count = 0
            else:
                disco_count += 1

        
        #handle keypress, supports arrows and WASD
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] or keys[pg.K_w]:
            y_mod = -1
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            y_mod = 1

        if event.type == pg.KEYUP:
            if event.key == pg.K_c:
                disco_count = DISCO_TICK / 2
                game_ball.toggle_disco()

        #computer paddle follows ball
        computer_paddle.move_toward(game_ball.get_y() + 10)

        #collision detection
        if (pg.Rect.colliderect(game_ball.get_rect(), computer_paddle.get_rect())):
            game_ball.inc_speed()
            game_ball.bounce()

        elif (pg.Rect.colliderect(game_ball.get_rect(), player_paddle.get_rect())):
            game_ball.inc_speed()
            game_ball.bounce()

        #update graphics
        player_paddle.update(y_mod)
        game_ball.update()
        display_score(player_score, computer_score)
        player_paddle.display()
        computer_paddle.display()   
        game_ball.display()         
        pg.display.update()
        clock.tick(FPS)
            
game_loop()

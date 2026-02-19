import random
from turtle import color
import pygame
import math
pygame.init()
time_scale = 1
WIDTH, HEIGHT = 800, 600
running = True
wall_angle=0
build_mode = False
build_type="wall"
dragging_ball=None
prev_mouse_pos=(0,0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
Gravity = 0.5
Bounce = 0.7
ramp_angle=0
balls = []
walls = []
ramps = []
ball_spawners=[]
Gui = True
slider=False
spawn_buttons=False
font = pygame.font.SysFont(None, 36)
gui_text = font.render("start game", True, (255, 255, 255))
ball_button_text = font.render("spawn balls", True, (255, 255, 255))    
pygame.display.set_caption("Ball Simulation")
clear_balls_button = pygame.Rect(0,100, 150, 100)
ball_button = pygame.Rect(0, 0, 150, 100)
GuiButton = pygame.Rect(270, 200, 250, 150)
class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.label = label
        self.dragging = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            percent = (mouse_x - self.rect.x) / self.rect.width
            percent = max(0, min(1, percent))
            self.value=self.min_val + (self.max_val - self.min_val) * percent
    def draw(self, screen, font):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        percent=(self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x=self.rect.x + percent * self.rect.width
        pygame.draw.circle(screen,(255,100,100),(int(knob_x), self.rect.centery), 10)
        label_text=font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))
gravity_slider=Slider(590, 200, 200, 0, 2, 0.5, "Gravity")
bounce_slider=Slider(590, 300, 200, 0, 1, 0.7, "Bounce")   
class Wall:
    def __init__(self, x, y,width=20,height=120,angle=0):
        self.x = x
        self.y = y
        self.width=width
        self.height=height
        self.angle = angle
    def points(self):
        base=[(0,0),(self.width,0),(self.width,self.height),(0,self.height)]
        points=[]
        for px,py in base:
            rotated_x=px*math.cos(math.radians(self.angle))-py*math.sin(math.radians(self.angle))
            rotated_y=px*math.sin(math.radians(self.angle))+py*math.cos(math.radians(self.angle))
            points.append((self.x + rotated_x, self.y + rotated_y))
        return points
    def draw(self, screen):
        pygame.draw.polygon(screen, (100, 100, 100), self.points())
class Ramp:
    def __init__(self, x, y,angle=0):
        self.x=x
        self.y=y
        self.angle=angle
    def points(self):
        base=[(0,0),(120,0),(120,-60)]
        points=[]
        for px,py in base:
            rotated_x=px*math.cos(math.radians(self.angle))-py*math.sin(math.radians(self.angle))
            rotated_y=px*math.sin(math.radians(self.angle))+py*math.cos(math.radians(self.angle))
            points.append((self.x + rotated_x, self.y + rotated_y))
        return points
    def draw(self, screen):
        pygame.draw.polygon(screen, (120, 80, 50), self.points())

class Ball:
    def __init__(self, x, y, radius,color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_y=0
        self.vel_x=0
        self.mass=self.radius
    def update(self):
        self.vel_y += Gravity *time_scale
        self.y += self.vel_y*time_scale
        self.x += self.vel_x*time_scale
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vel_y *= -Bounce
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vel_x *= -Bounce
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vel_x *= -Bounce
        self.vel_x *= 0.999
        self.vel_y *= 0.999
        for wall in walls:
            pts = wall.points()
            edges = [
                (pts[0], pts[1]),
                (pts[1], pts[2]),
                (pts[2], pts[3]),
                (pts[3], pts[0])
            ]
            
            collided = False
            for (x1,y1),(x2,y2) in edges:
                ex = x2 - x1
                ey = y2 - y1
                length = math.hypot(ex,ey)
                if length == 0: 
                    continue
                tx = ex/length
                ty = ey/length
                nx = -ty
                ny = tx
                bx = self.x - x1
                by = self.y - y1
                proj = bx*tx + by*ty
                proj = max(0, min(length, proj))
                closest_x = x1 + tx*proj
                closest_y = y1 + ty*proj
                dx = self.x - closest_x
                dy = self.y - closest_y
                dist = math.hypot(dx, dy)
                if dist < self.radius:
                    collided = True
                    if dist == 0: 
                        continue
                    nx = dx / dist
                    ny = dy / dist
                    overlap = self.radius - dist
                    self.x += nx*overlap
                    self.y += ny*overlap
                    vn = self.vel_x*nx + self.vel_y*ny
                    if vn < 0:
                        self.vel_x -= 2*vn*nx
                        self.vel_y -= 2*vn*ny
                    self.vel_x *= 0.9
                    self.vel_y *= Bounce

            
        for ramp in ramps:
            points = ramp.points()
            for i in range(len(points)):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % len(points)]
                ex = x2 - x1
                ey = y2 - y1
                length=math.hypot(ex, ey)
                if length == 0:
                    continue
                tx=ex / length
                ty=ey / length
                nx=-ty
                ny=tx
                bx=self.x - x1
                by=self.y - y1
                proj=bx * tx + by * ty
                proj= max(0, min(length, proj))
                closest_x = x1 + proj * tx
                closest_y = y1 + proj * ty
                
                dx=self.x - closest_x
                dy=self.y - closest_y
                dist=math.hypot(dx, dy)
                if dist < self.radius:
                    overlap=self.radius - dist
                    self.x+= nx*overlap
                    self.y+= ny*overlap
                    vn = self.vel_x * nx + self.vel_y * ny
                    if vn < 0:
                        self.vel_x -= vn * nx 
                        self.vel_y -= vn * ny 
                    gravity_along=Gravity*ty
                    self.vel_x += gravity_along*tx*time_scale
                    self.vel_y += gravity_along*ty*time_scale
                    self.vel_x *= 0.99
                    self.vel_y *= 0.99
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
class BallSpawner:
    def __init__(self, x, y, rate=1):
        self.x = x
        self.y = y

        self.rate = rate
        self.timer=0
    def update(self,dt):
        self.timer += dt
        if self.timer >= 1/self.rate:
            balls.append(Ball(self.x, self.y, 20, (random.randint(0,255), random.randint(0,255), random.randint(0,255))))

            self.timer=0
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), 15)
def clear_balls():
    balls.clear()
def check_collisions(balls):
    for i in range (len(balls)):
        for j in range(i + 1, len(balls)):
            b1=balls[i]
            b2=balls[j]
            dx=b2.x - b1.x
            dy=b2.y - b1.y
            distance=math.hypot(dx, dy)
            if distance == 0:
                continue
            if distance <b1.radius +b2.radius:
                overlap=(b1.radius + b2.radius) - distance
                nx = dx / distance
                ny = dy / distance
                b1.x -= nx * overlap / 2
                b1.y -= ny * overlap / 2
                b2.x += nx * overlap / 2
                b2.y += ny * overlap / 2
                rvx = b2.vel_x - b1.vel_x
                rvy = b2.vel_y - b1.vel_y
                vel_along_normal = rvx * nx + rvy * ny
                if vel_along_normal > 0:
                    continue   
                restitution = 0.8
                impulse = -(1 + restitution) * vel_along_normal
                impulse /= (1 / b1.mass) + (1 / b2.mass)
                impulse_x = impulse * nx
                impulse_y = impulse * ny
                b1.vel_x -= impulse_x / b1.mass
                b1.vel_y -= impulse_y / b1.mass
                b2.vel_x += impulse_x / b2.mass
                b2.vel_y += impulse_y / b2.mass
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        gravity_slider.handle_event(event)
        bounce_slider.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 :
                if Gui:
                    if GuiButton.collidepoint(event.pos):
                        Gui = not Gui
                else:


                    if ball_button.collidepoint(event.pos):
                        
                        spawn_buttons=not spawn_buttons
                if clear_balls_button.collidepoint(event.pos):
                    clear_balls()
        if event.type == pygame.MOUSEWHEEL and build_mode and build_type=="ramp":
            ramp_angle += event.y * 10
        elif event.type == pygame.MOUSEWHEEL and build_mode and build_type=="wall":
            wall_angle += event.y * 10
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1 and build_mode:
            x,y=event.pos
            if build_type=="wall":
                walls.append(Wall(x,y,20,120,wall_angle))
            elif build_type=="ramp":
                ramps.append(Ramp(x,y,ramp_angle))
            elif build_type=="ball_spawner":
                ball_spawners.append(BallSpawner(x,y,rate=1))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx,my=pygame.mouse.get_pos()
            for ball in balls:
                dx=ball.x - mx
                dy=ball.y - my
                if math.hypot(dx, dy) < ball.radius:
                    dragging_ball=ball
                    break
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging_ball:
                mx,my=pygame.mouse.get_pos()
                vx=mx - prev_mouse_pos[0]
                vy=my - prev_mouse_pos[1]
                dragging_ball.vel_x=vx*0.5
                dragging_ball.vel_y=vy*0.5
                dragging_ball=None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx,my=pygame.mouse.get_pos()
            for ball in balls:
                dx=ball.x - mx
                dy=ball.y - my
                if math.hypot(dx, dy) < ball.radius:
                    balls.remove(ball)
                    break  
            for wall in walls:
                pts = wall.points()
                if pygame.draw.polygon(screen, (0, 0, 0), pts).collidepoint(mx, my):
                    walls.remove(wall)
                    break
            for ramp in ramps:
                pts = ramp.points()
                if pygame.draw.polygon(screen, (0, 0, 0), pts).collidepoint(mx, my):
                    ramps.remove(ramp)
                    break
            for spawner in ball_spawners:
                if math.hypot(spawner.x - mx, spawner.y - my) < 15:
                    ball_spawners.remove(spawner)
                    break
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and spawn_buttons:
            
            x, y = pygame.mouse.get_pos()
            balls.append(Ball(x, y, 20, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                time_scale = .3
            if event.key == pygame.K_p:
                time_scale = 0
            if event.key == pygame.K_b:
                build_mode = not build_mode
            if event.key == pygame.K_1:
                build_type = "wall"
            if event.key == pygame.K_2:
                build_type = "ramp"
            if event.key == pygame.K_3:
                build_type = "ball_spawner"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                time_scale = 1
            if event.key == pygame.K_p:
                time_scale = 1
   

    
    if dragging_ball:
        dragging_ball.x, dragging_ball.y = mx,my
        prev_mouse_pos=(mx,my)    
    
                        
    screen.fill((255, 255, 255))
    for ball in balls:
        if ball!=dragging_ball:
            ball.update()

    check_collisions(balls)
    for ball in balls:
        ball.draw(screen)

    for wall in walls:
        wall.draw(screen)
    
    for ramp in ramps:
        ramp.draw(screen)

    dt=clock.get_time()/1000
    for spawner in ball_spawners:
        spawner.update(dt)
        spawner.draw(screen)

    if Gui==False:
        Bounce=bounce_slider.value
        Gravity=gravity_slider.value        
        gravity_slider.draw(screen,font)
        bounce_slider.draw(screen,font)
        
    if Gui:
        pygame.draw.rect(screen, (0, 255, 0), GuiButton)
    
        screen.blit(gui_text, (GuiButton.x + 20, GuiButton.y + 50))
    if spawn_buttons and not Gui:
        pygame.draw.rect(screen, 'green', clear_balls_button)
        screen.blit(font.render("clear balls", True, (255, 255, 255)), (clear_balls_button.x + 20, clear_balls_button.y + 50))
        pygame.draw.rect(screen, 'green', ball_button)
        screen.blit(ball_button_text, (ball_button.x + 20, ball_button.y + 50))
    elif not spawn_buttons and not Gui:
        pygame.draw.rect(screen, 'green', clear_balls_button)
        screen.blit(font.render("clear balls", True, (255, 255, 255)), (clear_balls_button.x + 20, clear_balls_button.y + 50))
        pygame.draw.rect(screen, 'red', ball_button)
        screen.blit(ball_button_text, (ball_button.x + 20, ball_button.y + 50))
    value_text= font.render(f"Gravity: {Gravity:.2f} Bounce: {Bounce:.2f}", True, 'black')

    screen.blit(value_text, (WIDTH - value_text.get_width() - 10, 10))
    mx,my=pygame.mouse.get_pos()
    if build_mode:
        screen.blit(font.render(f"Building: {build_type}", True, 'black'), (500, 500))

        if build_type=="wall":
            base = [(0, 0), (20, 0), (20, 120), (0, 120)]
            preview=[]
            for px,py in base:
                rotated_x=px*math.cos(math.radians(wall_angle))-py*math.sin(math.radians(wall_angle))
                rotated_y=px*math.sin(math.radians(wall_angle))+py*math.cos(math.radians(wall_angle))
                preview.append((mx + rotated_x, my + rotated_y))
            pygame.draw.polygon(screen, (150,150, 150, 100), preview,2)        
        elif build_type=="ramp":
            base = [(0, 0), (120, 0), (120, -60)]
            preview=[]
            for px,py in base:
                rotated_x=px*math.cos(math.radians(ramp_angle))-py*math.sin(math.radians(ramp_angle))
                rotated_y=px*math.sin(math.radians(ramp_angle))+py*math.cos(math.radians(ramp_angle))
                preview.append((mx + rotated_x, my + rotated_y))
            pygame.draw.polygon(screen, (150, 150, 100), preview,2)
        elif build_type=="ball_spawner":
            mx,my=pygame.mouse.get_pos()
            pygame.draw.circle(screen, (0, 255, 0), (int(mx), int(my)), 15)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
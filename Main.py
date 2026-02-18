import pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
running = True
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
Gravity = 0.5
Bounce = 0.7
balls = []
Gui = True
font = pygame.font.SysFont(None, 36)
gui_text = font.render("start game", True, (255, 255, 255))
pygame.display.set_caption("Ball Simulation")
GuiButton = pygame.Rect(270, 200, 250, 150)
class Ball:
    def __init__(self, x, y, radius,color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_y=0
    def update(self):
        self.vel_y += Gravity
        self.y += self.vel_y
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vel_y *= -Bounce
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and Gui:
                if GuiButton.collidepoint(event.pos):
                    Gui = not Gui
            else:
                x, y = pygame.mouse.get_pos()
                balls.append(Ball(x, y, 20, (255, 0, 0)))
    screen.fill((255, 255, 255))
    for ball in balls:
        ball.update()
        ball.draw(screen)
    if Gui:
        pygame.draw.rect(screen, (0, 255, 0), GuiButton)
    
        screen.blit(gui_text, (GuiButton.x + 20, GuiButton.y + 50))
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
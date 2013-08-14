import python.engines.trajectory as tj
import pygame

clock = pygame.time.Clock()
Phys = tj.Physics()
C = tj.Cannonball(Phys)
R = tj.RPG(Phys)
H = tj.Homing(Phys)
cannons = [C, R, H]
for cannon in cannons:
    cannon.set_initial_conditions([0,0,0], 0, 3.14/4, 40)
    cannon.calculate_trajectory()

pygame.init()
screen = pygame.display.set_mode((640, 480))
canvas = pygame.Surface(screen.get_size())
canvas.fill((0,0,0))
screen.blit(canvas, (0,0))
colors = [(255,0,0), (0,255,0), (0,0,255)]
while True:
    color_index = 0
    for cannon in cannons:
        cannon.frame_step()
        if cannon.hit_status == False:
            pygame.draw.circle(canvas, colors[color_index], [int(cannon.get_current_frame()[0,0]), 480 - int(cannon.get_current_frame()[0,2])], 5)
        color_index += 1
    screen.blit(canvas, (0,0))
    pygame.display.flip()
    clock.tick(60)


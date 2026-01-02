############################################################
#                                                          #
# Name: Safiya                                             #
# Date: May 13th, 2025                                     #
# Description: Main File for 8 ball Video Game Culminating #
#              - Use Mouse/Trackpad to Control             #
#              - Hold Mouse to Power Up                    #
############################################################

# ============================== #
#         IMPORT & INIT          #
# ============================== #

import pygame
import pymunk
import pymunk.pygame_util  # allows combining both modules visually
import ball8_sprites
import math

# ============================== #
#            DISPLAY             #
# ============================== #

screen_w = 1200
screen_h = 678
bottom_p = 80  # Extra space for bottom panel
screen = pygame.display.set_mode((screen_w, screen_h + bottom_p))
pygame.display.set_caption("8 Ball Pool")

# ============================== #
#     BACKGROUND ENTITIES        #
# ============================== #

background = pygame.Surface(screen.get_size())
background.fill((139, 134, 128))

# ============================== #
#            SOUND               #
# ============================== #

pygame.mixer.init()
pygame.init()

# Background Music

pygame.mixer.music.load("background_music.mp3")  # Load background music
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)                      # Loop the music

# Sound Effects - when shot
shotSound = pygame.mixer.Sound("shot.mp3")
shotSound.set_volume(0.2)

# Sound Effects - when a normal ball is potted
pottedSound = pygame.mixer.Sound("potted.mp3")
pottedSound.set_volume(1.0)

# ============================== #
#            ENTITIES            #
# ============================== #

# Create the physics simulation space
space = pymunk.Space()
static_body = space.static_body  # Required to attach static objects (like cushions)
drawing = pymunk.pygame_util.DrawOptions(screen)

# Table setup
table = ball8_sprites.PoolTable()
allSpritesTable = pygame.sprite.Group(table)

# Cushion setup (adds to physics space)
cushions = []
for c_n in range(6):
    cushions.append(ball8_sprites.Cushions(c_n, space))

# Bottom Panel setup
bottom_p = ball8_sprites.BottomPanel(screen_w, bottom_p, screen_h)
allSpritesBottomPanel = pygame.sprite.Group(bottom_p)

# ============================== #
#             BALLS              #
# ============================== #

ball_dia = 36  # Diameter of each ball

balls = []
rows = 5
imageOfBall = 1

# Arrange 15 balls in a triangular rack

for col in range(5):

    for row in range(rows):

        """
        To calculate the position of each ball in the rack:
        - The x position starts at 250 from the left,
          then moves right by (ball diameter + 1) for each column,
          spacing balls evenly horizontally

        - The y position starts at 267 from the top,
          moves down by (ball diameter + 1) pixels for each ball in the current column (row number),
          and then shifts down by half a ball diameter times the column number,
          which staggers the balls vertically to create the triangular rack shape
        """

        pos = (250 + (col * (ball_dia + 1)), 267 + (row * (ball_dia + 1)) + (col * (ball_dia / 2)))

        """
        Create a new Ball instance/object at the calculated position with given radius,
        space and image number
        """

        n_ball = ball8_sprites.Ball(ball_dia / 2, pos, space, static_body, imageOfBall)

        """
        Adds the new ball to the list of ball
        """
        balls.append(n_ball)

        """

        Increases image index for the next ball to assign the correct ball image.

        """

        imageOfBall += 1

    """

    Decreases the number of balls in the next column by one,
    so the rack forms a triangle shape (5 balls in first column,
    then 4, then 3, ...)

    """

    rows -= 1

# Cue ball setup (white ball)

cueBallPos = (888, (678 / 2))

c_ball = ball8_sprites.Ball(ball_dia / 2, cueBallPos, space, static_body, 16)

balls.append(c_ball)

allSpritesBalls = pygame.sprite.Group(balls)

# Cue setup
cue = ball8_sprites.Cue((balls[-1].get_position()))

# Power bar setup
powerBar = ball8_sprites.PowerBar()

# ============================== #
#         POTTING CHECK          #
# ============================== #

potted_balls = []             # Track names of potted balls for bottom bar
potted_balls_sprites = []     # Track sprites of potted balls
allSpritesPottedBalls = []    # Sprite group placeholder
pockets = ball8_sprites.Pockets(pottedSound, screen_h)  # Handles pocket detection

# ============================== #
#        LABELS / LIVES          #
# ============================== #

pos = ((screen.get_width() / 2), 738)
label1 = ball8_sprites.Label(5, pos)
allSpritesLabels = pygame.sprite.Group(label1)

# ============================== #
#         START SCREEN           #
# ============================== #

start_screen = True
start_background = pygame.image.load("start_screen.png")
start_background = pygame.transform.scale(start_background, (1200, 758))

while start_screen:

    screen.blit(start_background, (0, 0))
    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start_screen = False

# ============================== #
#        GAME VARIABLES          #
# ============================== #

clock = pygame.time.Clock()
keepGoing = True
shot = True              # True if no balls are moving
force = 0
power = False
cue_angle = 0
cueball_ispotted = False
lives = 5
over = False

# ============================== #
#         MAIN GAME LOOP         #
# ============================== #

while keepGoing:

    if not over:

        clock.tick(120)
        space.step(1 / 120)  # Physics engine
        screen.fill((50, 50, 50))
        screen.blit(background, (0, 0))

        allSpritesTable.update()
        allSpritesTable.draw(screen)

        # Game Over condition check
        if (label1.get_lives()) == 0 or len(balls) == 1:
            over = True

        for event in pygame.event.get():
            shot = True  # balls are stationary

        # Pocket detection for all balls

        cueball_ispotted = pockets.if_potted(
            balls, space, potted_balls,
            allSpritesBalls, cueball_ispotted,
            potted_balls_sprites, allSpritesPottedBalls
        ) # uses sprites

        # Check if any ball is moving

        for b in balls:

            if abs(b.get_body().velocity[0]) > 0.1 or abs(b.get_body().velocity[1]) > 0.1:
                shot = False  # Ball is moving

            # Quit event
            if event.type == pygame.QUIT:
                keepGoing = False

            # Cue rotation based on mouse movement
            if event.type == pygame.MOUSEMOTION:

                mouse_pos = pygame.mouse.get_pos()

                cueBall_pos = balls[-1].get_position()

                cue_angle = cue.update(mouse_pos, cueBall_pos) # updates the image of the cue so that it rotates

            # Start charging power when mouse pressed

            if event.type == pygame.MOUSEBUTTONDOWN and shot:

                power = True

                cue.increase_force()

                # Draw power bars based on force

                for force in range(math.ceil(cue.get_force() / 2000)):
                    screen.blit(
                        powerBar.image,
                        (balls[-1].get_position()[0] - 30 + (force * 15),
                         balls[-1].get_position()[1] + 30)
                    )

            # Release shot when mouse released

            if event.type == pygame.MOUSEBUTTONUP and power and shot:
                shotSound.play()
                power = False
                balls[-1].apply_impulse(cue.get_force(), cue_angle)
                cue.force_zero()
                cue.change_force_direction()
                label1.increase_score()

        # Draw all balls
        allSpritesBalls.update()
        allSpritesBalls.draw(screen)

        if shot:
            if cueball_ispotted:
                # Reset cue ball position after being potted
                balls[-1].set_body_position((888, screen_h // 2))
                cueball_ispotted = False
                label1.decrease_lives()
            cue.draw(screen)

        # Bottom Panel
        allSpritesBottomPanel.clear(screen, background)
        allSpritesBottomPanel.update()
        allSpritesBottomPanel.draw(screen)

        # Potted balls bar
        allSpritesPottedBalls = pygame.sprite.Group(potted_balls_sprites)
        allSpritesPottedBalls.clear(screen, background)
        allSpritesPottedBalls.update()
        allSpritesPottedBalls.draw(screen)

        # Labels
        allSpritesLabels.clear(screen, background)
        allSpritesLabels.update()
        allSpritesLabels.draw(screen)

    else:

        # ==============================
        #         GAME OVER SCREEN
        # ==============================

        pygame.mixer.music.fadeout(1)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    keepGoing = False

        if len(balls) == 1:
            background = pygame.image.load("gameWin.png")
            background = pygame.transform.scale(background, (1200, 678))
            screen.blit(background, (0, 0))

        elif label1.get_lives() == 0:
            background = pygame.image.load("gameOver.png")
            background = pygame.transform.scale(background, (1200, 678))
            screen.blit(background, (0, 0))

    pygame.display.flip()

pygame.display.quit()
pygame.quit()






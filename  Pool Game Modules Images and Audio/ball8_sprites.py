"""
===================================================================================================================
|  Name: Safiya                                                                                                    |
|  Date: May 13th, 2025                                                                                            |
|  Description: Sprite File for 8-Ball Video Game                                                                  |
|               Contains classes:                                                                                  |
|               Ball, PoolTable, Cushions, Cue, powerBar, BottomBarBalls, BottomPanel, and Label                   |
===================================================================================================================
"""

# =========================================== IMPORTS AND INITIALIZATION ===========================================

import pygame
import pymunk
import pymunk.pygame_util  # allows you to use features that will link the two libraries together
import math
pygame.mixer.init()
pygame.init()


# ================================================== BALL CLASS ====================================================

class Ball(pygame.sprite.Sprite):

    """
    Represents a ball that interacts with each other using Pymunk physics
    """

    def __init__(self, radius, pos, space, static_body, imageOfBall):
        pygame.sprite.Sprite.__init__(self)

        # Create physical body and attach shape with elasticity
        self.__body = pymunk.Body()
        self.__body.position = pos

        self.__shape = pymunk.Circle(self.__body, radius)
        self.__shape.mass = 5
        self.__shape.elasticity = 0.9

        # Attach pivot joint to simulate table friction and restrict unwanted rotation
        self.__pivot = pymunk.PivotJoint(static_body, self.__body, (0, 0), (0, 0))
        self.__pivot.max_bias = 0
        self.__pivot.max_force = 10000

        self.__imageName = ("ball_{}.png".format(imageOfBall))
        self.image = pygame.image.load(self.__imageName).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.__body.position

        # Add body, shape, and constraint to space
        space.add(self.__body, self.__shape, self.__pivot)

    def apply_impulse(self, force, cue_angle):

        """
        Applies an impulse to the ball based on force and cue stick angle
        """

        # Convert cue angle to directional impulse
        self.__x_direction_impulse = -math.cos(math.radians(cue_angle))
        self.__y_direction_impulse = math.sin(math.radians(cue_angle))
        self.__impulse = (self.__x_direction_impulse * force, self.__y_direction_impulse * force) # tuple of x, y direction impulse
        self.__point = (0, 0)
        self.__body.apply_impulse_at_local_point(self.__impulse, self.__point)

    # === Getters ===

    def get_position(self):
        return self.__body.position

    def get_body(self):
        return self.__body

    def get_image_name(self):
        return self.__imageName

    def get_shape(self):
        return self.__shape

    def get_pivot(self):
        return self.__pivot

    # === Setters ===
    def set_body_position(self, pos):
        self.__body.position = pos

    def set_body_velocity(self, v):

        self.__body.velocity = v  # Unconventional, consider using `self.__body.velocity = v`

    def update(self):
        # Sync sprite position with physics position
        self.rect.center = self.__body.position


# ================================================ POOL TABLE ======================================================

class PoolTable(pygame.sprite.Sprite):

    """
    Displays the background pool table image
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("table.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def update(self):
        pass


# ================================================= CUSHIONS =======================================================

class Cushions(pygame.sprite.Sprite):

    """
    Represents the walls of the pool table using polygon pygame shapes/bodies for collision
    """

    def __init__(self, c_n, space):

        pygame.sprite.Sprite.__init__(self)
        self.__body = pymunk.Body(body_type=pymunk.Body.STATIC)

        # Vertex coordinates for all six cushion shapes
        self.__vPolyDims = [
            [(88, 56), (109, 77), (555, 77), (564, 56)],
            [(621, 56), (630, 77), (1081, 77), (1102, 56)],
            [(89, 621), (110, 600), (556, 600), (564, 621)],
            [(622, 621), (630, 600), (1081, 600), (1102, 621)],
            [(56, 96), (77, 117), (77, 560), (56, 581)],
            [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
        ]

        self.__body.position = (0, 0)
        self.__shape = pymunk.Poly(self.__body, self.__vPolyDims[c_n])
        self.__shape.elasticity = 0.9

        space.add(self.__body, self.__shape)

    def update(self):
        pass


# =================================================== CUE =========================================================

class Cue(pygame.sprite.Sprite):

    """
    Controls the cue stick, its angle, and applied force.
    """

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.__angle = 0
        self.__ogImage = pygame.image.load("cue.png")
        self.image = pygame.transform.rotate(self.__ogImage, self.__angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.__force = 0
        self.__max_force = 20000
        self.__force_direction = 1

    def update(self, mouse_pos, cueBall_pos):
        self.rect.center = cueBall_pos
        self.__x_dist = cueBall_pos[0] - mouse_pos[0]
        self.__y_dist = -(cueBall_pos[1] - mouse_pos[1])
        self.__angle = math.degrees(math.atan2(self.__y_dist, self.__x_dist))
        return self.__angle

    def increase_force(self):
        self.__force += 75 * self.__force_direction
        if self.__force >= self.__max_force or self.__force <= 0:
            self.__force_direction *= -1

    def change_force_direction(self):
        self.__force_direction = 1

    def force_zero(self):
        self.__force = 0

    def get_force(self):
        return self.__force

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.__ogImage, self.__angle)
        surface.blit(
            self.image,
            (
                self.rect.centerx - self.image.get_width() / 2,
                self.rect.centery - self.image.get_height() / 2
            ),
        )


# ================================================ POWER BAR =======================================================

class PowerBar(pygame.sprite.Sprite):

    """
    Displays a red power bar rectangle (for visualizing cue power).
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))


# ================================================= POCKETS =======================================================

class Pockets():

    """
    Contains logic for detecting when balls fall into pockets.
    """

    def __init__(self, sound, screen_h):
        self.__pocket_diameter = 66
        self.__pockets = [
            (55, 63), (592, 48), (1134, 64),
            (55, 616), (592, 629), (1134, 616)
        ]
        self.__potted_sound_effect = sound
        self.__screen_h = screen_h
        self.__i = 0

    def if_potted(self, balls, space, potted_balls, allSpritesBalls, cueball_ispotted, potted_balls_sprites, allSpritesPottedBalls):
        self.__balls_to_remove = []
        for b, ball in enumerate(balls):
            for pocket in self.__pockets:
                self.__ball_x_dist = abs(ball.get_position()[0] - pocket[0])
                self.__ball_y_dist = abs(ball.get_position()[1] - pocket[1])
                self.__ball_dist = math.sqrt((self.__ball_x_dist ** 2) + (self.__ball_y_dist ** 2))
                if self.__ball_dist <= self.__pocket_diameter / 2:
                    if (b == len(balls) - 1):
                        cueball_ispotted = True
                        ball.set_body_position((-10000000, -10000000))
                        ball.set_body_velocity((0.0, 0.0))
                    else:
                        self.__potted_sound_effect.play()
                        self.__balls_to_remove.append(ball)
                        p_ball = BottomBarBalls(self.__i, ball.get_image_name(), self.__screen_h)
                        potted_balls_sprites.append(p_ball)
                        allSpritesPottedBalls = pygame.sprite.Group(potted_balls_sprites)
                        self.__i += 1
        for ball in self.__balls_to_remove:
            if ball in balls:
                space.remove(ball.get_body(), ball.get_shape(), ball.get_pivot())
                allSpritesBalls.remove(ball)
                balls.remove(ball)
                potted_balls.append(ball.get_image_name())
        return cueball_ispotted


# ============================================= BOTTOM BAR BALLS ===================================================

class BottomBarBalls(pygame.sprite.Sprite):

    """
    Displays small versions of potted balls along the bottom bar.
    """
    def __init__(self, i, ball, screen_h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(ball).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = ((10 + (i * 50)), screen_h + 10)

    def update(self):
        pass


# ============================================== BOTTOM PANEL =====================================================

class BottomPanel(pygame.sprite.Sprite):

    """
    Displays the grey bar under the pool table for potted ball tracking.
    """
    def __init__(self, screen_w, bottom_p, screen_h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((screen_w, bottom_p))
        self.image.fill((139, 134, 128))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, screen_h)

    def update(self):
        pass


# ================================================== LABEL ========================================================

class Label(pygame.sprite.Sprite):

    """
    Displays score and lives text on screen.
    """
    def __init__(self, lives, pos):
        pygame.sprite.Sprite.__init__(self)
        self.__font = pygame.font.SysFont("georgia", 25)
        self.__score = 0
        self.__lives = lives
        self.__pos = pos
        self.__message = ""

    def increase_score(self):
        self.__score += 1

    def decrease_lives(self):
        if self.__lives != 0:
            self.__lives -= 1

    def winorlose(self, block_hit):
        if self.__lives == 0:
            return True

    def get_score(self):
        return self.__score

    def get_lives(self):
        return self.__lives

    def update(self):
        self.__message = "Lives: %d        Score: %d" % (self.__lives, self.__score)
        self.image = self.__font.render(self.__message, 1, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.__pos






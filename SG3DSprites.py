import pygame
from SG3DSets import *
from collections import deque

class Sprites:
    def __init__(self):
        self.spriteParms = {
            'mineral': {
                'sprite': pygame.image.load('img/sprite/mineral/mineral.png').convert_alpha(),
                'static': True,
                'shift': 1.8,
                'scale': 0.3,
                'blocked': False,
            },
            'kwiw': {
                'sprite': pygame.image.load('img/sprite/kwiw/kwiw.png').convert_alpha(),
                'static': True,
                'shift': 0.6,
                'scale': 1, 
                'blocked': True,
            },
            'saul': {
                'sprite': pygame.image.load('img/sprite/sg3d/sg3d.png').convert_alpha(),
                'static': True,
                'shift': 0,
                'scale': 0.8,
                'blocked': True,
            },
        }
        self.objectList = [
            SpriteObject(self.spriteParms['mineral'], (7.2, 2)),
            SpriteObject(self.spriteParms['mineral'], (3.2, 6)),
            SpriteObject(self.spriteParms['kwiw'], (5, 6.2)),
            SpriteObject(self.spriteParms['saul'], (10.5, 4.5))
        ]

    @property
    def spriteShot(self):
        return min([obj.isOnFire for obj in self.objectList], default=(float('inf'), 0))


class SpriteObject:
    def __init__(self, parameters, pos):
        self.object = parameters['sprite']
        self.static = parameters['static']
        self.shift = parameters['shift']
        self.scale = parameters['scale']
        self.blocked = parameters['blocked']
        self.side = 30
        self.x, self.y = pos[0] * TILE, pos[1] * TILE
        

    @property 
    def isOnFire(self):
        if CENTERAY - self.side // 2 < self.curRay < CENTERAY + self.side // 2 and self.blocked:
            return self.distanceToSprite, self.projHeight
        return float('inf'), None

    @property
    def pos(self):
        return (self.x - self.side // 2, self.y - self.side // 2)

    def objectLocate(self, player):

        dx, dy = self.x - player.x, self.y - player.y
        self.distanceToSprite = math.sqrt(dx ** 2 + dy ** 2)

        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += TWOPI

        deltaRays = int(gamma / DELTANGEL)
        self.curRay = CENTERAY + deltaRays
        self.distanceToSprite *= math.cos(HALFOV - self.curRay * DELTANGEL)

        fakeRay = self.curRay + FAKERAYS
        if 0 <= fakeRay <= FAKERAYSRANGE and self.distanceToSprite > 30:
            self.projHeight = min(int(PROJCOEF / self.distanceToSprite * self.scale), DOUBLEHEIGHT)
            halfProjHeight = self.projHeight // 2
            shift = halfProjHeight * self.shift

            #if not self.static:

            spritePos = (self.curRay * SCALE - halfProjHeight, HALFHEIGHT - halfProjHeight + shift)
            sprite = pygame.transform.scale(self.object, (self.projHeight, self.projHeight))
            return (self.distanceToSprite, sprite, spritePos)
        else:
            return (False,)
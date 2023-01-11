from SG3DSets import *
import pygame
import math
from SG3DMap import collisionWall


class Player:
    def __init__(self, sprites):
        self.x, self.y = playerPos
        self.sprites = sprites
        self.angle = playerAngle
        self.sensitivity = 0.003
        self.side = 50
        self.rect = pygame.Rect(*playerPos, self.side, self.side)
        self.spriteCollis = [pygame.Rect(*obj.pos, obj.side, obj.side) for obj in 
                             self.sprites.objectList if obj.blocked]
        self.listCollis = collisionWall + self.spriteCollis

        self.shot = False

    @property
    def getPos(self):
        return (self.x, self.y)

    def detectCollis(self, dx, dy):
        nextRect = self.rect.copy()
        nextRect.move_ip(dx, dy)
        hitIndexes = nextRect.collidelistall(self.listCollis)

        if len(hitIndexes):
            deltaX, deltaY = 0, 0
            for hitIndex in hitIndexes:
                hitRect = self.listCollis[hitIndex]
                if dx > 0:
                    deltaX += nextRect.right - hitRect.left
                else: 
                    deltaX += hitRect.right - nextRect.left 
                if dy > 0:
                    deltaY += nextRect.bottom - hitRect.top
                else: 
                    deltaY += hitRect.bottom - nextRect.top
            if abs(deltaX - deltaY) < 10:
                dx, dy = 0, 0
            elif deltaX > deltaY:
                dy = 0
            elif deltaY > deltaX:
                dx = 0

        self.x += dx 
        self.y += dy    

    def movement(self):
        self.keysControl()
        self.mouseControl()
        self.rect.center = self.x, self.y
        self.angle %= TWOPI

    def keysControl(self):
        sinA = math.sin(self.angle)
        cosA = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit()
        if keys[pygame.K_w]:
            dx = playerSpeed * cosA
            dy = playerSpeed * sinA
            self.detectCollis(dx, dy)
        if keys[pygame.K_s]:
            dx = -playerSpeed * cosA
            dy = -playerSpeed * sinA
            self.detectCollis(dx, dy)
        if keys[pygame.K_a]:
            dx = playerSpeed * sinA
            dy = -playerSpeed * cosA
            self.detectCollis(dx, dy)
        if keys[pygame.K_d]:
            dx = -playerSpeed * sinA
            dy = playerSpeed * cosA
            self.detectCollis(dx, dy)
        if keys[pygame.K_LEFT]:
            self.angle -= 0.025
        if keys[pygame.K_RIGHT]:
            self.angle += 0.025
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.shot:
                    self.shot = True

    def mouseControl(self):
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - HALFWIDTH
            pygame.mouse.set_pos((HALFWIDTH, HALFHEIGHT))
            self.angle += difference * self.sensitivity

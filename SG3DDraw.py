import pygame
from SG3DSets import *
from SG3DRC import rayCast
from SG3DMap import miniMap
from collections import deque

class Drawing:
    def __init__(self, scene, minMap, player):
        self.scene = scene
        self.minMap = minMap
        self.player = player
        self.font = pygame.font.SysFont('Bahnschrift', 33, bold=True)
        self.textures = {
            '1': pygame.image.load('img/saul.png').convert(),
            '2': pygame.image.load('img/finger.png').convert(),
            'S': pygame.image.load('img/sky.png').convert(),
        }
        self.weaponBaseSprite = pygame.image.load('sprite/weapon/shotgun/0.png').convert_alpha()
        self.weaponShotAnimation = deque([pygame.image.load(f'sprite/weapon/shotgun/shot/{i}.png').convert_alpha()
                                         for i in range(20)])
        self.weaponRect = self.weaponBaseSprite.get_rect()
        self.weaponPos = (HALFWIDTH - self.weaponRect.width // 2, HEIGHT - self.weaponRect.height)
        self.shotLen = len(self.weaponShotAnimation)
        self.shotLenCount = 0
        self.shotAnimationSpeed = 3
        self.shotAnimationCount = 0 
        self.shotAnimationTrigger = True
        self.shotSound = pygame.mixer.Sound('hitsound.wav')

        self.sfx = deque([pygame.image.load(f'sprite/weapon/shotgun/sfx/{i}.png').convert_alpha()
                                         for i in range(9)])
        self.sfxLenCount = 0
        self.sfxLen = len(self.sfx)

    def bg(self, angle):
        skyOffset = -5 * math.degrees(angle) % WIDTH
        self.scene.blit(self.textures['S'], (skyOffset,0))
        self.scene.blit(self.textures['S'], (skyOffset - WIDTH, 0))
        self.scene.blit(self.textures['S'], (skyOffset + WIDTH, 0))
        pygame.draw.rect(self.scene, GRAY, (0, HALFHEIGHT, WIDTH, HALFHEIGHT))

    def drawWorld(self, worldObj):
        for obj in sorted(worldObj, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, objectPos = obj
                self.scene.blit(object, objectPos)

    def fps(self, clock):
        showFPS = str(int(clock.get_fps()))
        renderFPS = self.font.render(showFPS, 0, RED)
        self.scene.blit(renderFPS, FPSPOS)

    def miniMapMaker(self, player):
        self.minMap.fill(BLACK)
        mapX, mapY = player.x // MINIMAPSCALE, player.y // MINIMAPSCALE
        pygame.draw.line(self.minMap, YELLOW, (mapX, mapY), (mapX + 12 * math.cos(player.angle),
                                                             mapY + 12 * math.sin(player.angle)), 2)
        pygame.draw.circle(self.minMap, RED, (int(mapX), int(mapY)), 5)
        for x, y in miniMap:
            pygame.draw.rect(self.minMap, GREEN, (x, y, MINIMAPTILE, MINIMAPTILE), 2)
        self.scene.blit(self.minMap, MINIMAPPOS)

    def playWeapon(self, shots):
        if self.player.shot:
            if not self.shotLenCount:
                self.shotSound.play()
            self.shotProj = min(shots)[1]//2
            self.bulletSfx()
            shotSprite = self.weaponShotAnimation[0]
            self.scene.blit(shotSprite, self.weaponPos)
            self.shotAnimationCount += 1
            if self.shotAnimationCount == self.shotAnimationSpeed:
                self.weaponShotAnimation.rotate(-1)
                self.shotAnimationCount = 0
                self.shotLenCount += 1
                self.shotAnimationTrigger = False
            if self.shotLenCount == self.shotLen:
                self.player.shot = False
                self.shotLenCount = 0
                self.sfxLenCount = 0
                self.shotAnimationTrigger = True
        else:
            self.scene.blit(self.weaponBaseSprite, self.weaponPos)

    def bulletSfx(self):
        if self.sfxLenCount < self.sfxLen:
            sfx = pygame.transform.scale(self.sfx[0], (self.shotProj, self.shotProj))
            sfxRect = sfx.get_rect()
            self.scene.blit(sfx, (HALFWIDTH - sfxRect.w // 2, HALFHEIGHT - sfxRect.h // 2))
            self.sfxLenCount += 1
            self.sfx.rotate(-1)
import pygame
from SG3DSets import *
from SG3DMap import worldMap

def mapping(a, b):
    return (a // TILE) * TILE, (b // TILE) * TILE

def rayCast(playerPos, playerAngle, worldMap):
    castedWalls = []
    ox, oy = playerPos
    textureV, textureH = 1, 1
    xm, ym = mapping(ox, oy)
    curAngle = playerAngle - HALFOV
    for ray in range(NUMRAYS):
        sinA = math.sin(curAngle)
        sinA = sinA if sinA else 0.000001
        cosA = math.cos(curAngle)
        cosA = cosA if cosA else 0.000001

        # verticals
        x, dx = (xm + TILE, 1) if cosA >= 0 else (xm, -1)
        for i in range(0, WIDTH, TILE):
            depthV = (x - ox) / cosA
            yv = oy + depthV * sinA
            tileV = mapping(x + dx, yv)
            if tileV in worldMap:
                textureV = worldMap[tileV]
                break
            x += dx * TILE

        # horizontals
        y, dy = (ym + TILE, 1) if sinA >= 0 else (ym, -1)
        for i in range(0, HEIGHT, TILE):
            depthH = (y - oy) / sinA
            xh = ox + depthH * cosA
            tileH = mapping(xh, y + dy)
            if tileH in worldMap:
                textureH = worldMap[tileH]
                break
            y += dy * TILE

        # projection
        depth, offset, texture = (depthV, yv, textureV) if depthV < depthH else (depthH, xh, textureH)
        offset = int(offset) % TILE
        depth *= math.cos(playerAngle - curAngle)
        depth = max(depth, 0.00001)
        projHeight = int(PROJCOEF / depth)

        castedWalls.append((depth, offset, projHeight, texture))
        curAngle += DELTANGEL
    return castedWalls

def rayCastWalls(player, textures):
    castedWalls = rayCast(player.getPos, player.angle, worldMap)
    wallShot = castedWalls[CENTERAY][0], castedWalls[CENTERAY][2]
    walls = []
    for ray, castedValues in enumerate(castedWalls):
        depth, offset, projHeight, texture = castedValues
        if projHeight > HEIGHT:
            coef = projHeight / HEIGHT
            textureHeight = THEIGHT / coef
            wallColumn = textures[texture].subsurface(offset * TSCALE,
                                                       HTHEIGHT - textureHeight // 2,
                                                       TSCALE, textureHeight)
            wallColumn = pygame.transform.scale(wallColumn, (SCALE, HEIGHT))
            wallPos = (ray * SCALE, 0)
        else:
            wallColumn = textures[texture].subsurface(offset * TSCALE, 0, TSCALE, THEIGHT)
            wallColumn = pygame.transform.scale(wallColumn, (SCALE, projHeight))
            wallPos = (ray * SCALE, HALFHEIGHT - projHeight // 2)

        walls.append((depth, wallColumn, wallPos))
    return walls, wallShot
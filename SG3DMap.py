from SG3DSets import *
import pygame

textMap = [
    '111111111111',
    '1..........1',
    '1.2.....2..1',
    '1.2.....2..1',
    '1.2......2.1',
    '1......22..1',
    '1..........1',
    '111111111111'
]

worldMap = {}
miniMap = set()
collisionWall = []
for j, row in enumerate(textMap):
    for i, char in enumerate(row):
        if char != '.':
            miniMap.add((i * MINIMAPTILE, j * MINIMAPTILE))
            collisionWall.append(pygame.Rect(i * TILE, j * TILE, TILE, TILE))
            if char == '1':
                worldMap[(i * TILE, j * TILE)] = '1'
            elif char == '2':
                worldMap[(i * TILE, j * TILE)] = '2'
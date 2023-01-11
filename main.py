import pygame
from tkinter import *
from tkinter import ttk
from random import shuffle
import random
from tkinter.messagebox import showinfo, showerror
from copy import deepcopy
from SG3DSets import *
from SG3DPlayer import Player
import math
from SG3DMap import worldMap
from SG3DRC import rayCastWalls
from SG3DDraw import Drawing
from SG3DSprites import *


colors = {
    1: 'blue',
    2: 'green',
    3: 'red',
    4: '#d05fca',
    5: '#ffa100',
    6: '#ffa4f7',
    7: '#00e8ff',
    8: '#890101'
}             

class GameButton(Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(GameButton, self).__init__(master, width=3, font='Bahnschrift 12 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.isMine = False 
        self.bombCount = 0
        self.isOpen = False

class GameMines():

    miner = Tk()
    miner.title('Сапёр')
    miner.withdraw()
    ROWS = 9
    COLUMNS = 9
    MINES = 15
    GAME_IS_DEAD = False
    IS_FIRST_CLICK = True

    def __init__(self):
        self.minerTheme = pygame.mixer.Sound('minerTheme.wav')
        self.channel = pygame.mixer.Channel(0)
        self.gamefield = []
        for i in range (GameMines.ROWS+2):
            tmp = []
            for j in range(GameMines.COLUMNS+2):
                btn = GameButton(GameMines.miner, x=i, y=j)
                btn.config(command=lambda butt=btn: self.click(butt))
                btn.bind("<Button-3>", self.rightClick)
                tmp.append(btn)
            self.gamefield.append(tmp)

    def click(self, clickButton: GameButton):

        if GameMines.GAME_IS_DEAD:
            return None

        if GameMines.IS_FIRST_CLICK:
            self.pootisMinesHere(clickButton.number)
            self.countMines()
            GameMines.IS_FIRST_CLICK = False

        if clickButton.isMine:
            clickButton.config(text="БУМ", disabledforeground='black')
            clickButton.isOpen = True
            GameMines.GAME_IS_DEAD = True
            showinfo('YOU ARE DEAD', 'Вы проиграли!')
            for i in range(1, GameMines.ROWS + 1):
                for j in range(1, GameMines.COLUMNS + 1):
                    btn = self.gamefield[i][j]
                    if btn.isMine:
                        btn['text'] = 'БУМ'
        else:
            color = colors.get(clickButton.bombCount, 'black')
            if clickButton.bombCount:
                clickButton.config(text=clickButton.bombCount, disabledforeground=color)
                clickButton.isOpen = True
            else:
                self.emptySearcher(clickButton)
        clickButton.config(state='disabled', relief=SUNKEN)

    def rightClick(self, event: GameButton):
        if GameMines.GAME_IS_DEAD:
            return 
        curBut = event.widget
        if curBut['state'] == 'normal':
            curBut['state'] = 'disabled'
            curBut['text'] = '🚩'
        elif curBut['text'] == '🚩':
            curBut['text'] = ''
            curBut['state'] = 'normal'

    def emptySearcher(self, btn: GameButton):

        queue = [btn]
        while queue:

            currentButton = queue.pop()
            color = colors.get(currentButton.bombCount, 'black')
            if currentButton.bombCount:
                currentButton.config(text=currentButton.bombCount, disabledforeground=color)
            else:
                currentButton.config(text='', disabledforeground=color)
            currentButton.isOpen = True
            currentButton.config(state='disabled', relief=SUNKEN)

            if currentButton.bombCount == 0:
                x, y = currentButton.x, currentButton.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nextBut = self.gamefield[x+dx][y+dy]
                        if not nextBut.isOpen and 1<=nextBut.x<=GameMines.ROWS and \
                        1<=nextBut.y<=GameMines.COLUMNS and next not in queue:
                            queue.append(nextBut)


    def reload(self):
        [child.destroy() for child in self.miner.winfo_children()]
        self.__init__()
        self.newField()
        GameMines.IS_FIRST_CLICK = True
        GameMines.GAME_IS_DEAD = False

    def setsWindow(self):
        winSets = Toplevel(self.miner)
        winSets.wm_title('Настройки')
        Label(winSets, text="Строки: ").grid(row=0, column=0)
        Label(winSets, text="Колонки: ").grid(row=1, column=0)
        Label(winSets, text="Мины: ").grid(row=2, column=0)
        rowEntry = Entry(winSets)
        rowEntry.insert(0, GameMines.ROWS)
        rowEntry.grid(row=0, column=1, padx=15, pady=15)
        columnEntry = Entry(winSets)
        columnEntry.insert(0, GameMines.COLUMNS)
        columnEntry.grid(row=1, column=1, padx=15, pady=15)
        minesEntry = Entry(winSets)
        minesEntry.insert(0, GameMines.MINES)
        minesEntry.grid(row=2, column=1, padx=15, pady=15)
        saveSets = Button(winSets, text='Применить', 
        command=lambda: self.applySets(rowEntry, columnEntry, minesEntry))
        saveSets.grid(row=3, column=0, columnspan=2, padx=15, pady=15)

    def applySets(self, row: Entry, column: Entry, mines: Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильные значения')
            return
        GameMines.ROWS = int(row.get())
        GameMines.COLUMNS = int(column.get())
        GameMines.MINES = int(mines.get())
        self.reload()

    def newField(self):

        mb = Menu(self.miner)
        self.miner.config(menu=mb)

        setsMenu = Menu(mb, tearoff=0)
        setsMenu.add_command(label="Играть", command=self.reload)
        setsMenu.add_command(label="Настройки",command=self.setsWindow)
        setsMenu.add_command(label="Выход", command=self.destroyMiner)

        mb.add_cascade(label='Файл', menu=setsMenu)

        count = 1
        for i in range(1, GameMines.ROWS + 1):
            for j in range(1, GameMines.COLUMNS + 1):
                btn = self.gamefield[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='nwes')
                count += 1

        for i in range(1, GameMines.ROWS + 1):
            Grid.rowconfigure(self.miner, i, weight=1) 

        for i in range(1, GameMines.COLUMNS+ 1):
            Grid.columnconfigure(self.miner, i, weight=1)


    def destroyMiner(self):
        self.miner.withdraw()
        self.channel.stop()
        mainChannel.play(mainTheme, loops=-1)
        mainWin.deiconify()

    def minerOnClosing(self):
        GameMines.miner.destroy()
        mainWin.destroy()

    def startMiner(self):
        GameMines.miner.deiconify()
        self.channel.play(self.minerTheme, loops=-1)
        self.newField()
        GameMines.miner.protocol("WM_DELETE_WINDOW", onClosing)
        GameMines.miner.mainloop()

    def pootisMinesHere(self, number: int):
        mineSpaces = self.getMinesSpaces(number)
        for i in range(1, GameMines.ROWS + 1):
            for j in range(1, GameMines.COLUMNS + 1):
                btn = self.gamefield[i][j]
                if btn.number in mineSpaces:
                    btn.isMine = True

    def countMines(self):
        for i in range(1, GameMines.ROWS + 1):
            for j in range(1, GameMines.COLUMNS + 1):
                bomb = self.gamefield[i][j]
                bombCount = 0
                if not bomb.isMine:
                    for rowDx in [-1, 0, 1]:
                        for colDx in [-1, 0, 1]:
                            nearBomb =  self.gamefield[i+rowDx][j+colDx]
                            if nearBomb.isMine:
                                bombCount += 1 
                bomb.bombCount = bombCount

    @staticmethod
    def getMinesSpaces(excludenNumber: int):
        minesList = list(range(1, GameMines.COLUMNS * GameMines.ROWS + 1))
        minesList.remove(excludenNumber)
        shuffle(minesList)
        return minesList[:GameMines.MINES]    

def createMiner():
    mainWin.withdraw()
    mainChannel.stop()
    Mines = GameMines()
    Mines.reload()
    Mines.startMiner()

def createTetris():

    mainWin.withdraw()
    mainChannel.stop()

    WIDTH = 10
    HEIGHT = 20
    TILE = 45
    GAMERES = WIDTH * TILE, HEIGHT * TILE
    MAINRES = 750, 940
    FPS = 60 

    tetris = pygame
    tetris.init()
    tetris.display.set_caption('Тетрис с Тору!')
    tetrisTheme = tetris.mixer.Sound('tetrisTheme.wav')
    tetrisChannel = tetris.mixer.Channel(2)
    
    tetrisChannel.play(tetrisTheme, loops=-1)

    scene = tetris.display.set_mode(MAINRES)
    gameScene = tetris.Surface(GAMERES)
    clock = tetris.time.Clock()

    grid = [tetris.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(WIDTH) for y in range(HEIGHT)]

    figurePositions = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                       [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                       [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                       [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, 0)]]

    figures = [[tetris.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in figPositions] \
        for figPositions in figurePositions]
    figuresRect = tetris.Rect(0, 0, TILE - 2, TILE - 2)
    gameField = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    
    animCount, animSpeed, animLimit = 0, 60, 2000
    figure, nextFigure = deepcopy(random.choice(figures)), deepcopy(random.choice(figures))

    backGround = tetris.image.load('Tohru.PNG').convert()
    gameGround = tetris.image.load('Tohru2.png').convert()

    mainFont = tetris.font.Font('Pixeboy.ttf', 64)
    justFont = tetris.font.Font('Pixeboy.ttf', 42)

    tetrisTitle = mainFont.render('TETRIS', True, tetris.Color('darkorange'))
    tetrisScore = mainFont.render('Score:', True, tetris.Color('red'))
    tetrisRecord = mainFont.render('Record: ', True , tetris.Color('purple'))

    getColor = lambda: (random.randrange(50, 256), random.randrange(50, 256), 
                        random.randrange(50, 256))

    color, nextColor = getColor(), getColor() 

    score, madeLines = 0, 0
    scores = {0: 0, 1:100, 2:300, 3:700, 4:1500}                   

    def borderCheck():
        if figure[i].x < 0 or figure[i].x > WIDTH - 1:
            return False
        elif figure[i].y > HEIGHT - 1 or gameField[figure[i].y][figure[i].x]:
            return False
        return True

    def getRecord():
        try:
            with open('record') as f:
                return f.readline()
        except FileNotFoundError:
            with open('record', 'w') as f:
                f.write('0')

    def setRecord(record, score):
        rec = max(int(record), score)
        with open('record', 'w') as f:
            f.write(str(rec))


    while True:
        record = getRecord()
        dx, rotate = 0, False
        scene.blit(backGround, (0, 0))
        scene.blit(gameScene, (20, 20))
        gameScene.blit(gameGround, (0, 0))

        for i in range(madeLines):
            tetris.time.wait(213)

        for event in tetris.event.get():
            if event.type == tetris.QUIT:
                exit()
            if event.type == tetris.KEYDOWN:
                if event.key == tetris.K_LEFT:
                    dx = -1
                elif event.key == tetris.K_RIGHT:
                    dx = 1
                elif event.key == tetris.K_DOWN:
                    animLimit = 100
                elif event.key == tetris.K_UP:
                    rotate = True
        
        oldFigure = deepcopy(figure)
        for i in range (4):
            figure[i].x += dx
            if not borderCheck():
                figure = deepcopy(oldFigure)
                break

        animCount += animSpeed
        if animCount > animLimit:
            animCount = 0
            oldFigure = deepcopy(figure)
            for i in range (4):
                figure[i].y += 1
                if not borderCheck():
                    for i in range(4):
                        gameField[oldFigure[i].y][oldFigure[i].x] = color
                    figure, color = nextFigure, nextColor
                    nextColor, nextFigure = getColor(), deepcopy(random.choice(figures))
                    animLimit = 2000
                    break

        center = figure[0]
        oldFigure = deepcopy(figure)
        if rotate:
            for i in range (4):
                x = figure[i].y - center.y
                y = figure[i].x - center.x
                figure[i].x = center.x - x
                figure[i].y = center.y + y
                if not borderCheck():
                    figure = deepcopy(oldFigure)
                    break

        endLine, madeLines = HEIGHT - 1, 0
        for row in range(HEIGHT - 1, -1, -1):
            count = 0
            for i in range(WIDTH):
                if gameField[row][i]:
                    count += 1
                gameField[endLine][i] = gameField[row][i]
            if count < WIDTH:
                endLine -= 1
            else:
                animSpeed += 3
                madeLines += 1

        score += scores[madeLines] 

        [tetris.draw.rect(gameScene, (40, 40, 40), iRect, 1) for iRect in grid]

        for i in range(4):
            figuresRect.x = figure[i].x * TILE
            figuresRect.y = figure[i].y * TILE
            tetris.draw.rect(gameScene, color, figuresRect)

        for y, raw in enumerate(gameField):
            for x, col in enumerate(raw):
                if col:
                    figuresRect.x, figuresRect.y  = x * TILE, y * TILE
                    tetris.draw.rect(gameScene, col, figuresRect) 

        for i in range(4):
            figuresRect.x = nextFigure[i].x * TILE + 380
            figuresRect.y = nextFigure[i].y * TILE + 185
            tetris.draw.rect(scene, nextColor, figuresRect)  

        scene.blit(tetrisTitle, (495, 20))
        scene.blit(tetrisScore, (495, 600))
        scene.blit(justFont.render(str(score), True, tetris.Color('white')), (495, 640))
        scene.blit(tetrisRecord, (495, 800))
        scene.blit(justFont.render(str(record), True, tetris.Color('white')), (495, 840))

        for i in range(WIDTH):
            if gameField[0][i]:
                setRecord(record, score)
                gameField = [[0 for i in range(WIDTH)] for i in range(HEIGHT)]
                animCount, animSpeed, animLimit = 0, 60, 2000
                score = 0
                for i_rect in grid:
                    tetris.draw.rect(gameScene, getColor(), i_rect)
                    scene.blit(gameScene, (20, 20))
                    tetris.display.flip()
                    clock.tick(200)

        tetris.display.flip()
        clock.tick(FPS)

def SaulGoodman3d():

    mainChannel.stop()

    saulTheme = pygame.mixer.Sound('SaulGoodman.wav')
    saulChannel = pygame.mixer.Channel(2)
    saulChannel.play(saulTheme, loops=-1)

    SaulGoodman = pygame
    SaulGoodman.init()

    scene = SaulGoodman.display.set_mode((WIDTH, HEIGHT))
    SaulGoodman.mouse.set_visible(False)
    miniMap = SaulGoodman.Surface((WIDTH // MINIMAPSCALE, HEIGHT // MINIMAPSCALE))

    sprites = Sprites()
    clock = SaulGoodman.time.Clock()
    JMM =  Player(sprites)
    drawer = Drawing(scene, miniMap, JMM)
    
    while True:
        JMM.movement()

        drawer.bg(JMM.angle)
        walls, wallShot = rayCastWalls(JMM, drawer.textures)
        drawer.drawWorld(walls + [obj.objectLocate(JMM) for obj in sprites.objectList])
        drawer.fps(clock)
        drawer.miniMapMaker(JMM)
        drawer.playWeapon([wallShot, sprites.spriteShot])

        #SaulGoodman.draw.circle(scene, GREEN, (int(JMM.x), int(JMM.y)), 12)
        #SaulGoodman.draw.line(scene, GREEN, JMM.getPos, (JMM.x + WIDTH  * math.cos(JMM.angle), 
                                                         #JMM.y + WIDTH  * math.sin(JMM.angle)))

        #for x,y in worldMap:
        #    SaulGoodman.draw.rect(scene, GRAY, (x, y, TILE, TILE), 2)

        SaulGoodman.display.flip()
        clock.tick(FPS)

def onClosing():
    mainWin.destroy()
    GameMines.miner.destroy()


mainWin = Tk()
mainWin.resizable(False, False)
mainWin.title('Главное меню')
mainWin.geometry("400x200")

pygame.mixer.init()
mainTheme = pygame.mixer.Sound('mainTheme.wav')
mainChannel = pygame.mixer.Channel(1)
mainChannel.play(mainTheme, loops=-1)

hiLabel = Label(mainWin, text='Сборник мини-игр by VerSun!', font='Bahnschrift 15 bold')
hiLabel.pack()

minerBtn = Button(mainWin, text='Сапер', font='Bahnschrift 12', command=createMiner)
tetrisBtn = Button(mainWin, text='Тетрис с Тору!', font='Bahnschrift 12', command=createTetris)
SaulGoodmanBtn = Button(mainWin, text='Сол Гудман', font='Bahnschrift 12', command=SaulGoodman3d)
exiter = Button(mainWin, text='Выйти', font='Bahnschrift 12', command=onClosing)

minerBtn.pack()
tetrisBtn.pack()
SaulGoodmanBtn.pack()
exiter.pack()

mainWin.protocol("WM_DELETE_WINDOW", onClosing)
mainWin.mainloop()
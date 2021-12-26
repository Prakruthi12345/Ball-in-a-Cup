from cmu_112_graphics import *  # cmu_112_graphics taken from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html)
from widgets import *
from tkinter import *
from PIL import Image
import random
import time
import math
import copy

class BICPlayer(object):
    def __init__(self, mode, x, y):
        self.mode = mode
        self.x = x
        self.y = y
        self.timer = 0
        url = "https://i.pinimg.com/originals/22/e7/8d/22e78db9710bd583eb647cf471a6c49c.png"
        self.player = self.mode.loadImage(url)
        self.sprites = []
        for i in range(7):
            sprite = self.player.crop((10 +50*i, 100, 55 + 50*i, 220))
            sprite = self.mode.scaleImage(sprite, 6/4)
            self.sprites.append(sprite)
        sprite = self.player.crop((450, 140, 25 + 500, 210))
        sprite = self.mode.scaleImage(sprite, 6/4)
        self.sprites.append(sprite)

    def draw(self, canvas):
        canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(
                                    self.sprites[self.timer]))


class BICTable(object):
    def __init__(self, mode, x, y):
        self.mode = mode
        self.x = x
        self.y = y
        url = "https://comps.canstockphoto.com/cartoon-wood-table-eps-vectors_csp49105335.jpg"
        self.spritestrip = self.mode.loadImage(url)
        self.spritestrip = self.mode.scaleImage(self.spritestrip, 1/5)

    def draw(self,canvas):
        canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(self.spritestrip))

class BICCup(object):
    def __init__(self,mode, x, y):
        self.mode = mode
        self.x = x
        self.y = y
        self.cupDepth = 16
        url = "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcQtFK5DJZr_P4iDQCIBPwR9sWzWFkSBqbTaOeTdvkz9S4xsFL0rLwdEE12khu6bHfrWgRKIc9gfNhzEbZOOWD2KNdwCk8t6X9BkSiFwKdpkIac5GGQS192X&usqp=CAc"
        self.spritestrip = self.mode.loadImage(url)
        self.spritestrip = self.mode.scaleImage(self.spritestrip, 1/5)

    def isBallWithinCup(self, x, y):
        if ((abs(self.x - x) <= 5) and (abs(self.y - self.cupDepth - y) <= 5)):
            return True
        return False
      
    def draw(self,canvas):
        canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(self.spritestrip))

class BICBall:
    def __init__(self, mode, x, y, r, fill = "red"):
        self.mode = mode
        self.startX = x
        self.startY = y
        self.radius = r
        self.radiusSquared = r**2
        self.fillColor = fill
        self.reset()

    def reset(self):
        self.currentX = self.startX
        self.currentY = self.startY
        self.startTime = 0
        self.velocity = 0
        self.gravity = 0
        self.radians = 0

    def setLaunchParameters(self, velocity, angle, gravity = 9.81):
        self.radians = (angle * math.pi)/180
        self.velocity = velocity
        self.gravity = gravity

    def computeTrajectory(self, velocity, radians, gravity, elapsed):
        x =  velocity * math.cos(radians) * elapsed
        y = (velocity * math.sin(radians) * elapsed) - ((gravity * (elapsed**2))/2)
        return (x, y)

    def computePosition(self, delta = None):
        if (self.startTime == 0):
            self.startTime = datetime.datetime.now()
            x = 0
            y = 0
            elapsed = 0
        else:
            elapsed = \
                (datetime.datetime.now() - self.startTime).total_seconds()
            (x, y) = self.computeTrajectory(self.velocity, self.radians,
                                       self.gravity, elapsed)
            self.currentX = self.startX + x
            self.currentY = self.startY - y # since tkinter top left is (0,0)

        return (self.currentX, self.currentY)

    def isPointWithinCircle(self, x, y):
        return (((self.currentX-x)**2 + (self.currentY-y)**2) <= self.radiusSquared)

    def getPosition(self):
        return (self.currentX, self.currentY)

    def move(self, x, y):
        self.currentX = x
        self.currentY = y

    def draw(self, canvas):
        c = canvas.create_oval(self.currentX-self.radius, self.currentY-self.radius,
                           self.currentX+self.radius, self.currentY+self.radius,
                           fill=self.fillColor)
class BICArc:
    def __init__(self, mode, x, y, r, start = 0, end = 360, numSlices = 12):
        self.mode = mode
        self.centerX = x
        self.centerY = y
        self.radius = r
        self.radiusSquared = r**2
        self.startAngle = start
        self.endAngle = end
        self.numSlices = numSlices

    def isPointWithinArc(self, x, y):
        if ((((x - self.centerX)**2) + ((y - self.centerY)**2)) <= self.radiusSquared):
            return True
        return False

    def getPointAngle(self, x, y):
        return ((math.atan2(self.centerY - y, x - self.centerX) * 180)/math.pi)

    def draw(self, canvas):
        arcAngle = (self.endAngle - self.startAngle)/self.numSlices
        for i in range(self.numSlices):
            canvas.create_arc(self.centerX-self.radius, self.centerY-self.radius,
                               self.centerX+self.radius, self.centerY+self.radius,
                               start = i * arcAngle, extent = arcAngle,
                               outline = "orange", width = 5)

class BICGameMode(Mode):
    def __init__(mode, standalone = False):
        mode.standalone = standalone
        super(BICGameMode, mode).__init__()

    def redrawAll(mode, canvas):
        font = 'Arial 16 bold'
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "yellow")
        textStr = f'''
        Get the ball into at least 2 cups within 90 seconds
        The velocity of the throw can be input in the labeled box and clicking the button
        The angle of the throw can be controlled by dragging the ball to point within the
        orange guide arc. Releasing the mouse will launch the ball from the origin.
        Press any key to start the game'''
        canvas.create_text(mode.width/2, mode.height/2, text=textStr,
                           font = font)

    def keyPressed(mode, event):
        mode.app.setActiveMode(BICGameRealMode(standalone = mode.standalone))

class BICGameRealMode(Mode):
    def __init__(mode, standalone = False):
        mode.standalone = standalone
        super(BICGameRealMode, mode).__init__()

    def appStarted(mode):
        mode.app.miniWon = False

        mode.gameWon = False
        mode.numTargets = 3
        mode.minTargetsToHit = mode.numTargets - 1
        mode.targetsHit = 0
        mode.launchBall = False
        mode.minVelocity = 20
        mode.maxVelocity = 200
        mode.minAngle = 0
        mode.maxAngle = 60
        mode.arcAngle = 20
        mode.velocity = 0
        mode.angle = 0
        mode.gameOver = False
        mode.maxPlayTime = 90 # seconds
        mode.hideNonCanvasWidgets = False
        mode.switchMode = False
        mode.ballDragStarted = False
        mode.ballDragStopped = False

        playerX = 40 + random.randrange(10)
        playerY = mode.app.height//3 - random.randrange(10)
        mode.player = BICPlayer(mode, playerX, playerY)

        mode.tables = []
        x = mode.app.width/2 -50
        y = mode.app.height//3 + 50
        for i in range(mode.numTargets):
            mode.tables.append(BICTable(mode, x, y))
            x += 150

        mode.cups = []
        x = mode.app.width/2 - 50
        y = mode.app.height//3 + 15
        for i in range(mode.numTargets):
            mode.cups.append(BICCup(mode, x, y))
            x += 150

        mode.cupsToBeHit = copy.copy(mode.cups)

        mode.ballRadius = 8
        mode.arcRadius = 120
        mode.ball = BICBall(mode, playerX + 10, playerY, mode.ballRadius)
        mode.guide = BICArc(mode, playerX + 10, playerY, mode.arcRadius,
                        start = mode.minAngle, end = mode.maxAngle,
                        numSlices = (mode.maxAngle - mode.minAngle)//mode.arcAngle)

        mode.velocityButton = MyButton(mode.app,
                   f'Enter Velocity ({mode.minVelocity} - {mode.maxVelocity})',
                   mode.setVelocity, input = True)
        placement = (mode.app.width/2, mode.app.height - 225,
                     mode.app.width/12, mode.app.height/20)
        mode.velocityButton.placeButton(placement)

        mode.prompts = MyMessage(mode.app, f'Let\'s Play!!!')
        placement = (mode.app.width/4, mode.app.height - 50,
                     mode.app.width/8, mode.app.height/20)
        mode.prompts.placeMessage(placement)

        placement = (mode.app.width/4, mode.app.height/2,
                     mode.app.width/2, 30)

        if (mode.standalone == False):
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Won !!!. Press any key to return to main game",
                         fillColor = "orange")
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Lost. Press any key to return to main game",
                         fillColor = "orange")
        else:
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Won !!!. Press any key to quit",
                         fillColor = "orange")
            mode.announceLoser = \
                  CaptionBoard(mode.app, placement,
                         "You Lost. Press any key to quit",
                         fillColor = "orange")

        mode.announce = mode.announceLoser

        mode.startTime = datetime.datetime.now()
        mode.clock = MyClock(mode, (30, 350), mode.maxPlayTime)

    def setVelocity(mode):
        velocity = int(mode.velocityButton.getInput())
        if (velocity >= mode.minVelocity and velocity <= mode.maxVelocity):
            mode.velocity = velocity
        else:
            mode.prompts.displayMessage(f'Velocity out of range')

    def throwBall(mode):
        if (mode.angle > 0 and mode.velocity > 0):
            mode.ball.reset()
            mode.ball.setLaunchParameters(mode.velocity, mode.angle)
            mode.velocityButton.disable()
            mode.prompts.displayMessage(f'Launching Ball with velocity = {mode.velocity} and angle = {int(mode.angle)}')
            mode.launchBall = True
        else:
            mode.prompts.displayMessage(f'Input velocity and angle.\nClick the buttons alongside and then click Launch')

    def restartThrow(mode, promptStr = None):
        mode.ball.reset()
        mode.launchBall = False
        mode.velocityButton.enable()
        if (promptStr == None):
            mode.prompts.displayMessage(
                    f'Try with different velocity and/or angle')
        else:
            mode.prompts.displayMessage(promptStr)

    def mousePressed(mode, event):
        if ((mode.ballDragStarted == False) and (mode.launchBall == False) and
            (mode.ball.isPointWithinCircle(event.x, event.y))):
            if (mode.velocity == 0):
                mode.prompts.displayMessage(f'Set launch velocity first')
                return
            mode.ballDragStarted = True

    def mouseReleased(mode, event):
        if ((mode.ballDragStarted == True) and
            (mode.ballDragStopped == False) and (mode.launchBall == False)):
            if ((event.x <= mode.guide.centerX) or (event.y >= mode.guide.centerY)):
                mode.prompts.displayMessage(f'Drag ball to a point within the guide arc')
                mode.ballDragStarted = False
                mode.ball.reset()
                return
            mode.angle = 0
            if (mode.guide.isPointWithinArc(event.x, event.y) == True):
                angle = mode.guide.getPointAngle(event.x, event.y)
                if ((angle >= mode.minAngle) and (angle <= mode.maxAngle)):
                     mode.angle = angle
                     mode.ball.move(event.x, event.y)
                     mode.ballDragStopped = True
            if (mode.angle == 0):
                mode.prompts.displayMessage(f'Drag ball to a point within the guide arc')
                mode.ballDragStarted = False
                mode.ball.reset()

    def timerFired(mode):
        if (mode.gameOver == True):
            return
        mode.clock.tick()
        if (mode.clock.remaining() == 0):
            mode.gameOver = True
            mode.prompts.displayMessage(f'Sorry, time\'s up')
            return

        if mode.launchBall == True:
            x, y = mode.ball.computePosition()
            if (x < 0 or x > mode.app.width or y < 0 or y > mode.app.height):
                mode.restartThrow()

    def keyPressed(mode, event):
        if (mode.switchMode == True):
            if (mode.standalone == True):
                quit()
            mode.app.miniWon = mode.gameWon
            mode.app.setActiveMode(mode.app.prevMode)

    def redrawAll(mode, canvas):
        if (mode.gameOver == True):
            mode.hideNonCanvasWidgets = True
        font = 'Arial 20 bold'
        canvas.create_rectangle(0, 0, mode.width, mode.height)
        canvas.create_text(mode.width//2, 80, text='Ball in a Cup!', font=font)
        mode.player.draw(canvas)
        for table in mode.tables:
            table.draw(canvas)
        for cup in mode.cupsToBeHit:
            cup.draw(canvas)
        mode.velocityButton.drawButton(canvas, mode.hideNonCanvasWidgets)
        mode.prompts.drawMessage(canvas, mode.hideNonCanvasWidgets)
        mode.clock.draw(canvas)

        if (mode.launchBall == True):
            mode.ball.draw(canvas)
            (ballX, ballY) = mode.ball.getPosition()
            for cup in mode.cupsToBeHit:
                if (cup.isBallWithinCup(ballX, ballY) == True):
                    mode.prompts.displayMessage(f'AWESOME!!!')
                    mode.targetsHit += 1
                    mode.cupsToBeHit.remove(cup)
                    if (mode.targetsHit >= mode.minTargetsToHit):
                        mode.gameOver = True
                        mode.gameWon = True
                        mode.announce = mode.announceWinner
                        mode.launchBall = False
                    else:
                        mode.restartThrow(f'Let\'s Play')
                    break
        elif (mode.gameOver == False):
              mode.ball.draw(canvas)
              mode.guide.draw(canvas)
              if (mode.ballDragStopped == True):
                  mode.ballDragStarted = False
                  mode.ballDragStopped = False
                  mode.throwBall()
        else:
            mode.announce.drawBoard(canvas)
            mode.switchMode = True

# these are for running the game standalone.
# uncomment runStandAlone
class BICMiniGame(ModalApp):
    
    def appStarted(app):
        app.margin = 0
        app.getRoot().resizable(0, 0)
        app.setActiveMode(BICGameMode(standalone = True))

def runStandAlone():
    BICMiniGame(width = 900, height = 600)

runStandAlone()

'''
cup1: 65, 25
cup2: 75, 25
cup3: 85, 25
'''

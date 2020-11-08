import pygame as pg
import sys
import os
import math
import numpy as np
import random 

pg.init()
print(sys.version)
random.seed(5)

#Dimensions of window
display_width = 300
display_height = 300

#Sizing information
tile_size = 25
animal_size = 10

#Volume of creatures
N = 100
foxFreq = .05
rabbitFreq = 1
FPS = 60

#Text labels
myfont = pg.font.SysFont("Arial", 8)

gameDisplay = pg.display.set_mode((display_width,display_height))
pg.display.set_caption('Ecosystem')

black = (0,0,0)

clock = pg.time.Clock()
crashed = False

#Load Animals
fish = pg.image.load(os.getcwd() + '/Animals/rabbit.png')

#Tile selector
def gen_map(width,height):
    
    #Empty map
    tileSet = np.chararray((int(width), int(height)))
    visual = ""

    verbose("w = " + str(width))
    verbose("h = " + str(height))
    verbose(str(tileSet.shape[0]) + " , " + str(tileSet.shape[1]))
    #Decide which tile would be most appropriate, weight of neighboring tables matters
    i = 1
    while i <= width:
        j = 1
        while j <= height:
            tileSet[i-1, j-1] = "x"
            rng = randInt(100, True)
            if i == 1 or j == 1 or i == width or j == height: 
                if rng <= .8:
                    #verbose("value is " + str(rng))
                    tileSet[i-1, j-1] = "w"
                else:
                    tileSet[i-1, j-1] = "g"
            else:
                #new roles for determining tile assignment
                rng_d = randInt(20,False) / 100.0
                rng_g = randInt(50,False) / 100.0
                rng_s = randInt(15,False) / 100.0
                rng_w = randInt(15,False) / 100.0

                #bonuses, tiles influences by adjacent tiles
                b_d = b_g = b_s = b_w = 0 
                if tileSet[i-2,j-1].decode('utf-8') == "d" or tileSet[i-1, j-2].decode('utf-8') == "d":
                    b_d = .05
                if tileSet[i-2,j-1].decode('utf-8') == "g" or tileSet[i-1, j-2].decode('utf-8') == "g":
                    b_g = 0
                if tileSet[i-2,j-1].decode('utf-8') == "s" or tileSet[i-1, j-2].decode('utf-8') == "s":
                    b_s = .05
                if tileSet[i-2,j-1].decode('utf-8') == "w" or tileSet[i-1, j-2].decode('utf-8') == "w" or i == width - 1 or j == height - 1:
                    b_w = .13

                verbose("Tile = (" + str(i) + "," + str(j) + ")", False)
                verbose("Tile left = " + tileSet[i-2,j-1].decode('utf-8') + ", Tile above = " + tileSet[i-1,j-2].decode('utf-8'),False)
                verbose("d= " + str(rng_d) + " " + str(b_d) + " " + str(rng_d + b_d), False)
                verbose("g= " + str(rng_g) + " " + str(b_g) + " " + str(rng_g + b_g), False)
                verbose("s= " + str(rng_s) + " " + str(b_s) + " " + str(rng_s + b_s), False)
                verbose("w= " + str(rng_w) + " " + str(b_w) + " " + str(rng_w + b_w), False)
                #Determine highest rolling tile
                if max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_d + b_d:
                    tileSet[i-1,j-1] = "d"
                    verbose("desert selected", False)
                if max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_g + b_g:
                    tileSet[i-1,j-1] = "g"
                    verbose("grassland selected", False)
                if max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_s + b_s:
                    tileSet[i-1,j-1] = "s"
                    verbose("stone selected", False)
                if max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_w + b_w:
                    tileSet[i-1,j-1] = "w"
                    verbose("water selected", False)

            #verbose("(" + str(i) + "," + str(j) + ")")
            #verbose(tileSet[i-1,j-1].decode('utf-8'))
            visual = visual + tileSet[i-1, j-1].decode('utf-8') + " "
            j = j + 1
        i = i + 1
        verbose(visual)
        visual = ""
    return(tileSet)

#Draw the tile 
def place_tile(x, y, type, tile_size):

    #Places the appropriate tile
    def desert(x,y):
        desert = pg.image.load(os.getcwd() + '/Tiles/desert.png')
        gameDisplay.blit(desert, (x,y))
    def grass(x,y):
        grass = pg.image.load(os.getcwd() + '/Tiles/grassland.png')
        gameDisplay.blit(grass, (x,y))
    def stone(x,y):
        stone = pg.image.load(os.getcwd() + '/Tiles/stone.png')
        gameDisplay.blit(stone, (x,y))
    def waterTile(x,y):
        water = pg.image.load(os.getcwd() + '/Tiles/water.png')
        gameDisplay.blit(water, (x,y))

    #Select the appropriate tile and place
    if type == "d":
        desert(x * tile_size, y * tile_size)
    elif type == "g":
        grass(x * tile_size, y * tile_size)
    elif type == "s":
        stone(x * tile_size, y * tile_size)
    elif type == "w":
        waterTile(x * tile_size,y * tile_size)
    else:
        #Do Nothing, will leave black square
        type = type

#Animal Objects (and child objects are species)
class Animal(pg.sprite.Sprite):
    def __init__(self
                ,posx = 0
                ,posy = 0
                ,health = 100 
                ,hunger = 500
                ,thirst = 200 
                ,speed = 0 
                ,img = os.getcwd() + '/Animals/rabbit.png'
                ,hungerPain = 2
                ,meal = 20
                ,thirstPain = 1
                ,quenched = 50
                ,speedMod = 0
                ):

        #assign passed parameters to object
        pg.sprite.Sprite.__init__(self)
        self.posx = posx
        self.posy = posy
        self.health = health
        self.hunger = hunger
        self.full = hunger
        self.thirst = thirst
        self.notThirst = thirst
        self.speed = speed
        self.img = img
        self.hungerPain = hungerPain
        self.meal = 25
        self.thirstPain = thirstPain
        self.quenched = quenched
        self.speedMod = speedMod
        self.swimSpeed = 0

        #Other Calculated variables
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]

    #Display the animals avatar
    def display(self):
        picture = pg.image.load(self.img)
        gameDisplay.blit(picture, (self.posx,self.posy))
        #verbose(self.img)

    #Hunger
    def hungry(self, fed = False):
        if fed:
            self.hunger = self.hunger + self.meal
            if self.hunger > self.full:
                self.hunger = self.full
        else:
            self.hunger = self.hunger - self.hungerPain

        if self.hunger <= 0:
            self.death()

        verbose(self.species + " has " + str(self.hunger) + " hunger", False)

    #Thirst
    def thirsty(self, area):

        drank = False
        if ( checkLocation(self,area) == 'w' or 
             checkSpot(self.posx + tile_size, self.posy, area) == 'w' or 
             checkSpot(self.posx, self.posy + tile_size, area) == 'w' or 
             checkSpot(self.posx - tile_size, self.posy, area) == 'w' or 
             checkSpot(self.posx, self.posy - tile_size, area) == 'w' ) :
            drank = True

        if drank:
            self.thirst = self.thirst + self.quenched   
            if self.thirst > self.notThirst:
                self.thirst = self.notThirst
        else:
            self.thirst = self.thirst - self.thirstPain

        if self.thirst <= 0:
            self.death()

    #in the event of death
    def death(self):
        verbose(self.species + " died. (" + str(self.posx) + "," + str(self.posy) + ")"
            + ", health = " + str(self.health)
            + ", hunger = " + str(self.hunger)
            + ", thirst = " + str(self.thirst), True)

    #updateHealth
    #def updateHealth(self, heal = False, eat = False, drink = False):
        #self.hungry(eat)
        #self.thirsty(drink)

    #Move toward target
    def moveTo(self):
        #Find angle to object
        try:
            A = abs(math.degrees(math.atan((self.posy-self.target.posy)/(self.posx-self.target.posx))))
        except ZeroDivisionError:
            A = 90

        verbose("Angle is " + str(A))
        verbose(self.species +" at (" + str(self.posx) + "," + str(self.posy) + ") is targeting (" + str(self.target.posx) + "," + str(self.target.posy) + ")", False)
        
        #check tile movement penalties
        self.heading(abs(math.cos(A)), abs(math.sin(A)))
        verbose(self.species + " speed = " + str(self.speed) + " mod = " + str(self.speedMod), False)
        #X and Y velocity vector scaled on speed
        xcomp = max(self.speed * abs(math.cos(A)) * self.speedMod, self.swimSpeed)
        ycomp = max(self.speed * abs(math.sin(A)) * self.speedMod, self.swimSpeed)
 
        #Make sure we're heading in the right direct for angle
        if self.target.posx < self.posx :
            xcomp = xcomp * -1.0 #to left
        if self.target.posy < self.posy :
            ycomp = ycomp * -1.0 #up
        
        xcomp = round(xcomp,3)
        ycomp = round(ycomp,3)
        verbose("xcomp= " + str(xcomp) + " ycomp " + str(ycomp), False)

        return (xcomp, ycomp)

    def moveDir(self, xMove = 99999, yMove = 99999):

        #Generate random 2D movement within their speed
        verbose(self.species + " at (" + str(self.posx) + "," + str(self.posy) + ") Speed = " + str(self.speed) + " mod = " + str(self.speedMod), False)
        if xMove == 99999:
            xMove = randInt(self.speed * self.speedMod,False)
            verbose("xMove = " + str(xMove), False)
            if randInt(2,False) > 1:
                xMove = xMove * -1 
        if yMove == 99999:
            yMove = randInt(self.speed * self.speedMod,False)
            verbose("yMove = " + str(yMove), False)
            if randInt(2, False) > 1:
                yMove = yMove * -1

        verbose("prehead 1 - " + self.species + " at (" + str(self.posx) + "," + str(self.posy) + ") is moving (" + str(xMove) + "," + str(yMove) + "), with speed = " + str(self.speed) + " and mod = " + str(self.speedMod), False)
        
        #Checks for tile penalty
        self.heading(xMove, yMove)

        xMove = xMove * self.speedMod
        yMove = yMove * self.speedMod
        verbose("prehead 2 - " + self.species + " at (" + str(self.posx) + "," + str(self.posy) + ") is moving (" + str(xMove) + "," + str(yMove) + "), with speed = " + str(self.speed) + " and mod = " + str(self.speedMod), False)

        return xMove, yMove

    #change movement penalties
    def heading(self, xMove, yMove):
        if checkSpot(self.posx + xMove, self.posy + yMove, map) == 'd':
            self.speedMod = 1.5
        elif checkSpot(self.posx + xMove, self.posy + yMove, map) == 'g':
            self.speedMod = 1
        elif checkSpot(self.posx + xMove, self.posy + yMove, map) == 's':
            self.speedMod = 1
        else:
            self.speedMod = self.swimSpeed

    #Move the animal
    def move(self):

        try:
            xMove, yMove = self.moveTo()
        except AttributeError:
            verbose("Fox at (" + str(self.posx) + "," + str(self.posy) + ") has no target", False)
            xMove, yMove = self.moveDir()

        #Move creature to new spot
        self.posx = round(self.posx + xMove,1)
        self.posy = round(self.posy + yMove,1)
        verbose(self.species + " at (" + str(self.posx) + "," + str(self.posy) + ")", False)

        #Check bounds
        if self.posx >= display_width:
            self.posx = display_width - 1
        elif self.posx < 0:
            self.posx = 1
        if self.posy >= display_height:
            self.posy = display_height - 1
        elif self.posy < 0:
            self.posy = 1


#Inherited or Sub class (Note Person in bracket) 
class Fox(Animal): 
    #Constructor 
    #fox default attributes
    def __init__(self):
        super(Fox, self).__init__()
        self.speed = 2
        self.img = os.getcwd() + '/Animals/fox.png'
        self.targetdistance = 99999         
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]
        self.meal = 500
        self.swimSpeed = .3

class Rabbit(Animal): 
    #Constructor 
    #rabbit default attributes
    def __init__(self):
        super(Rabbit, self).__init__()
        self.speed = 3
        self.img = os.getcwd() + '/Animals/rabbit.png' 
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]

#land updater
def checkLocation(creature, tiles):
    verbose(creature.species + " at (" + str(creature.posx) + "," + str(creature.posy) + ")", False)
    verbose(creature.species + " at tile (" + str(int(creature.posx / tile_size)+1) + "," + str(int(creature.posy / tile_size)+1) + ")", False)
       
    return tiles[int(creature.posx / tile_size), int(creature.posy / tile_size)].decode('utf-8')

#Check future location
def checkSpot(xLoc, yLoc, tiles):
    xLoc = min(xLoc, display_width - 1)
    yLoc = min(yLoc, display_height - 1)
    verbose("(xloc, yloc) = (" + str(xLoc) + "," + str(yLoc) + ")", False)
    verbose("(xloctile, yloctile) = (" + str(int(xLoc / tile_size)) + "," + str(int(yLoc / tile_size)) + ")", False)
    verbose("Tile type is " + tiles[int(xLoc / tile_size), int(yLoc / tile_size)].decode('utf-8'))
    return tiles[int(xLoc / tile_size), int(yLoc / tile_size)].decode('utf-8')

#Simple grab random integer or probability 1 / given integer
def randInt(range, prob = False):
    verbose("Range was " + str(range), False)
    range = math.ceil(range)
    verbose("Range is " + str(range), False)
    if range < 1:
        p = 0
        verbose("0 Probability Given", False)
    elif prob:
        p = 1.0 * random.randint(1,range) / range
        verbose("Random Probability = " + str(p), False) 
    elif range != 0:
        p = random.randint(1,range)
        verbose("Random Value = " + str(p), False)
    else:
        p = 1
        verbose("Random Value = " + str(p), False)
    return p

#convenient switch for debut text
def verbose(printMe,loudOption = False):
    if loudOption:
        print(printMe)

#Give Animals Initial Placement
def setAnimalSpawn(type, size, mult, width, height, tiles):

    N = int(size * mult)

    #Create array
    if type == "fox":
        creatures = np.array([Fox() for i in range(N)])
    elif type == "rabbit":
        creatures = np.array([Rabbit() for i in range(N)])
    
    #Decide where they will start
    for creature in creatures:  
        W = randInt(width - 2 * tile_size) + tile_size
        H = randInt(height - 2 * tile_size) + tile_size
        verbose(creature.species + " initialized at (" + str(W) + "," + str(H) + ")", False)
        verbose(creature.species + " initialized at tile (" + str(int(W / tile_size)+1) + "," + str(int(H / tile_size)+1) + ")", False)
        while (tiles[int(W / tile_size), int(H / tile_size)]).decode('utf-8') == "w" and creature.swimSpeed == 0:
            verbose(creature.species + " cannot swim, rerolling spawn location", False)
            W = randInt(width - 2 * tile_size) - tile_size
            H = randInt(height - 2 * tile_size) - tile_size
        verbose(creature.species + " spawned at (" + str(W) + "," + str(H) + ")", False)
        verbose(creature.species + " spawned on tile (" + str(int(W / tile_size)+1) + "," + str(int(H / tile_size)+1) + ")", False)
        
        creature.posx = W
        creature.posy = H
        creature.Location = tiles[int(W / tile_size), int(H / tile_size)].decode('utf-8')

    return creatures

#Loop until the user clicks the close button.
done=False

#Call generate map construction
map = gen_map(display_width / tile_size, display_height / tile_size)

#Call animal construction
foxes = setAnimalSpawn("fox", N, foxFreq, display_width, display_height, map)
rabbits = setAnimalSpawn("rabbit", N, rabbitFreq, display_width, display_height, map)

# Used to manage how fast the screen updates
clock=pg.time.Clock()

# -------- Main Program Loop -----------
while done == False:
    for event in pg.event.get(): # User did something
        if event.type == pg.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
            pg.quit
            sys.exit()            

    #iterates through the grid and places a tile
    i = 0
    gameDisplay.fill(black)
    while (i < display_width / tile_size):
        j = 0
        while (j < display_height / tile_size):
            #Select the appropriate tile
            place_tile(i, j, map[i,j].decode('utf-8'), tile_size)
            verbose("Placing " + str(i) + "," + str(j) + " " + map[i,j].decode('utf-8'))
            #coordinates of each tile printed
            label = myfont.render("(" + str(i+1) + "," + str(j+1) + ")", 1, (255, 255, 0))
            #gameDisplay.blit(label, (i * tile_size, j * tile_size + int(tile_size/2)))
            #next row
            j = j + 1
        #next column
        i = i + 1

    #Show animals
    died = 0
    for i, fox in enumerate(foxes):
        fox.location = checkLocation(fox, map)
        fox.move()  
        fox.thirsty(map)
        if fox.hunger <= 0 or fox.thirst <= 0 or fox.health <= 0:
            foxes = np.delete(foxes, i-died)
            died = died + 1
            #verbose("Deleting dead " + fox.species, True)
        fox.display()
        #verbose(fox.species + " at (" + str(fox.posx) + "," + str(fox.posy) + ") is on " + fox.location)

    died = 0
    for i, rabbit in enumerate(rabbits):
        rabbit.location = checkLocation(rabbit, map)
        rabbit.move()
        rabbit.thirsty(map)
        if rabbit.hunger <= 0 or rabbit.thirst <= 0 or rabbit.health <= 0:
            rabbits = np.delete(rabbits, i-died)
            died = died + 1
            #verbose("Deleting dead " + rabbit.species, True)
        rabbit.display()
        #verbose(rabbit.species + " at (" + str(rabbit.posx) + "," + str(rabbit.posy) + ") is on " + rabbit.location)

    #check collision
    for i, predator in enumerate(foxes):
        foxes[i].targetdistance = 99999
        foxes[i].target = ""
        eaten = 0
        for j, prey in enumerate(rabbits):
            if prey.Location == 'g':
                prey.hungry(fed = True)
            else:
                prey.hungry(fed = False)
            verbose("j = " + str(j) + ", eaten = " + str(eaten), False)
            distanceCheck = math.sqrt( (rabbits[j-eaten].posx - foxes[i].posx) ** 2 + (rabbits[j-eaten].posy - foxes[i].posy) ** 2)
            if distanceCheck < 8:
                verbose(prey.species + " was eaten at (" + str(rabbits[j-eaten].posx) + "," + str(rabbits[j-eaten].posy) + ")",True)
                rabbits = np.delete(rabbits, j-eaten)
                predator.hungry(fed = True)
                foxes[i].target = ""
                eaten = eaten + 1
                break
            elif distanceCheck < foxes[i].targetdistance:
                foxes[i].targetdistance = distanceCheck
                foxes[i].target = rabbits[j-eaten]
                verbose(prey.species + " is targetted at (" + str(rabbits[j-eaten].posx) + "," + str(rabbits[j-eaten].posy) + ")",False)

        predator.hungry(fed = False)

    # Limit to X frames per second
    clock.tick(FPS)
    
    #foxes = np.delete(foxes, 0) 

    # Go ahead and update the screen with what we've drawn.
    pg.display.update()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pg.quit()
sys.exit()

'''
keep = np.ones(ARRAY.shape, dtype=bool)
for pos, val in enumerate(ARRAY):
    if val < some_condition:
        keep[pos] = False
ARRAY = ARRAY[keep]
'''
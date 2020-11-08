import pygame as pg
import sys
import os
import math
import numpy as np
import random 
from pygame.math import Vector2
#from Scripts.Objects.Tiles import gen_map
#from Scripts.Imports import run_imports
#run_imports()

#Dimensions of window
display_width = 300
display_height = 300

#Sizing information
tile_size = 25
animal_size = 10

#Volume of creatures
N = 50
foxFreq = .05
rabbitFreq = .95
FPS = 15

#Starting Info
print("Starting Simulation:")
print(sys.version)
random.seed(1)
clock = pg.time.Clock()
crashed = False

#Tile selector
def gen_map(width,height):
    
    def makeTile(tiletype, x, y):
        tile = tiletype
        tile.x = x
        tile.y = y
        tile.updatePix()
        verbose("Adding " + tile.biome + " tile at (" + str(tile.x+1) + "," + str(tile.y+1) + ")", False)
        return tile

    #Empty map
    #Store Tile Objects
    tileObjects = pg.sprite.Group()
    verbose("There are " + str(len(tileObjects)),False)
    tileSet = []
    visual = ""
    verbose("map width = " + str(width) + " blocks, map height = " + str(height) + "blocks", False)
    
    #Decide which tile would be most appropriate, weight of neighboring tables matters
    i = 1
    while i <= height:
        j = 1
        tileRow = []
        while j <= width:
            rng = randInt(100, True)
            verbose("value is " + str(rng) + " i = " + str(i-1) + " j = " + str(j-1), False)
            if i == 1 or j == 1 or i == height or j == width: 
                if rng <= .8:
                    tile = makeTile(Water(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)
                else:
                    tile = makeTile(Grassland(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)
            else:
                #new roles for determining tile assignment
                rng_d = randInt(30,False) / 100.0
                rng_g = randInt(50,False) / 100.0
                rng_s = randInt(25,False) / 100.0
                rng_w = randInt(18,False) / 100.0

                #bonuses, tiles influences by adjacent tiles
                b_d = b_g = b_s = b_w = 0
                if tileRow[j-2].biome == "desert" or prevRow[j-1].biome == "desert":
                    b_d = .05
                if tileRow[j-2].biome == "grassland" or prevRow[j-1].biome == "grassland":
                    b_g = 0
                if tileRow[j-2].biome == "stone" or prevRow[j-1].biome == "stone":
                    b_s = .05
                if tileRow[j-2].biome == "water" or prevRow[j-1].biome == "water" or j == width - 1 or i == height - 1:
                    b_w = .18

                verbose("Tile = (" + str(i) + "," + str(j) + ")", False)
                verbose("Tile left = " + tileRow[j-2].biome + ", Tile above = " + prevRow[j-1].biome,False)
                verbose("d= " + str(rng_d) + " " + str(b_d) + " " + str(rng_d + b_d), False)
                verbose("g= " + str(rng_g) + " " + str(b_g) + " " + str(rng_g + b_g), False)
                verbose("s= " + str(rng_s) + " " + str(b_s) + " " + str(rng_s + b_s), False)
                verbose("w= " + str(rng_w) + " " + str(b_w) + " " + str(rng_w + b_w), False)

                #Determine highest rolling tile
                if max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_d + b_d:
                    tile = makeTile(Desert(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)
                elif max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_g + b_g:
                    tile = makeTile(Grassland(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)
                elif max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_s + b_s:
                    tile = makeTile(Stone(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)                   
                elif max(rng_d + b_d, rng_g + b_g, rng_s + b_s, rng_w + b_w) == rng_w + b_w:
                    tile = makeTile(Water(), j-1, i-1)
                    tileRow.append(tile)
                    tileObjects.add(tile)

            #Making String to print map to log
            visual = visual + tileRow[j-1].biome[0:1] + " "
            
            j = j + 1
                
        tileSet.append(tileRow)
        prevRow = tileRow
        i = i + 1
        verbose("There are " + str(len(tileRow)) + " in row",False)
        verbose("There are " + str(len(tileObjects)),False)
        verbose(visual, True)
        visual = ""
    return (tileSet, tileObjects)

#Define tile attributes as class
class Tile(pg.sprite.Sprite):

    def __init__(self
            ,x = 0
            ,y = 0
            ,pic = os.getcwd() + '/Tiles/grassland.png'
            ,swimming = False
            ,landSpeed = 1
            ,vegValue = 0
            ):

        #assign passed parameters to object
        super().__init__()
        self.x = x
        self.y = y
        self.pic = pic
        self.swimming = swimming
        self.landSpeed = landSpeed
        self.vegValue = vegValue

        #Other Calculated variables
        self.biome = self.pic[len(os.getcwd()) + len("/Tiles/"):self.pic.find(".png")]

    #update corresponding locations
    def updatePix(self):
        self.xpix = self.x * tile_size
        self.ypix = self.y * tile_size

    #draws the given tile
    def tileDisplay(self):
        picture = pg.image.load(self.pic)
        gameDisplay.blit(picture, (self.xpix,self.ypix))
        verbose("Placing " + str(self.xpix) + "," + str(self.ypix) + " " + self.biome, False)
        verbose("Tile size = " + str(tile_size) + " x = " + str(self.x) + " xpix = " + str(self.xpix), False)

    #draws the location label
    def tileLabel(self):
        #coordinates of each tile printed
        label = myfont.render("(" + str(self.x+1) + "," + str(self.y+1) + ")", 1, (255, 255, 0))
        gameDisplay.blit(label, (self.x * tile_size, self.y * tile_size + int(tile_size/2)))

    #update runs required display info
    def update(self):
        self.tileDisplay()
        #self.tileLabel()

#Desert Biome
class Desert(Tile):
    #Constructor
    def __init__(self):
        super(Desert,self).__init__()
        self.landSpeed = 1.5
        self.pic = os.getcwd() + '/Tiles/desert.png'

        #Other Calculated variables
        self.biome = self.pic[len(os.getcwd()) + len("/Tiles/"):self.pic.find(".png")]

#Grassland Biome
class Grassland(Tile):
    #Constructor
    def __init__(self):
        super(Grassland,self).__init__()
        self.landSpeed = 1.0
        self.pic = os.getcwd() + '/Tiles/grassland.png'
        self.vegValue = 20

        #Other Calculated variables
        self.biome = self.pic[len(os.getcwd()) + len("/Tiles/"):self.pic.find(".png")]

#Stone Biome
class Stone(Tile):
    #Constructor
    def __init__(self):
        super(Stone,self).__init__()
        self.landSpeed = 1.0
        self.pic = os.getcwd() + '/Tiles/stone.png'
        self.vegValue = 5

        #Other Calculated variables
        self.biome = self.pic[len(os.getcwd()) + len("/Tiles/"):self.pic.find(".png")]

#Water Biome
class Water(Tile):
    #Constructor
    def __init__(self):
        super(Water,self).__init__()
        self.swimming = True
        self.pic = os.getcwd() + '/Tiles/water.png'

        #Other Calculated variables
        self.biome = self.pic[len(os.getcwd()) + len("/Tiles/"):self.pic.find(".png")]

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
                ,hungerPain = 4
                ,meal = 20
                ,thirstPain = 1
                ,quenched = 50
                ,speedMod = 0
                ,prey = True
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
        self.prey = prey
        self.rect = pg.Rect(self.posx, self.posy, pg.image.load(self.img).get_rect().size[0], pg.image.load(self.img).get_rect().size[1])

        #Other Calculated variables
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]

    #Display the animals avatar
    def display(self):
        picture = pg.image.load(self.img)
        self.rect = pg.Rect(self.posx, self.posy, self.rect.size[0], self.rect.size[1])
        gameDisplay.blit(picture, (self.posx,self.posy))
        #verbose(self.img)

    #Hunger
    def hungry(self, fed = True):

        if self.prey == True and self.Location.vegValue > 0:
            verbose(self.species + " is at (" + str(self.posx) + "," + str(self.posy) + ") and is on tile " + self.Location.biome + " vegvalue = " + str(self.Location.vegValue), False)
            self.hunger = self.hunger + self.Location.vegValue
            if self.hunger > self.full:
                self.hunger = self.full
        elif self.prey == False and fed == True:
            self.hunger = self.full
        else:
            self.hunger = self.hunger - self.hungerPain

        verbose(self.species + " at (" + str(self.posx) + "," + str(self.posy) + ") has " + str(self.hunger) + " hunger", False)

    #Thirst
    def thirsty(self, area):

        drank = False
        if ( self.Location == 'water' or 
             checkSpot(self.posx + tile_size, self.posy, area).biome == 'water' or 
             checkSpot(self.posx, self.posy + tile_size, area).biome == 'water' or 
             checkSpot(self.posx - tile_size, self.posy, area).biome == 'water' or 
             checkSpot(self.posx, self.posy - tile_size, area).biome == 'water' ) :
            drank = True

        if drank:
            self.thirst = self.thirst + self.quenched   
            if self.thirst > self.notThirst:
                self.thirst = self.notThirst
        else:
            self.thirst = self.thirst - self.thirstPain

    #in the event of death
    def ifDeath(self):
        if self.hunger <= 0 or self.thirst <= 0 or self.health == 0:
            verbose(self.species + " died. (" + str(self.posx) + "," + str(self.posy) + ")"
                + ", health = " + str(self.health)
                + ", hunger = " + str(self.hunger)
                + ", thirst = " + str(self.thirst), True)
            self.kill()

    #updateHealth
    def update(self,area,oppCreatures):
        self.updateLocationOrTarget(area, oppCreatures)
        self.hungry(False)
        self.thirsty(area)
        self.ifDeath()
        self.display() 
        self.move(area)

    #Track movement bonuses
    def updateLocationOrTarget(self,area, oppCreatures):

        #
        #Check tile that  
        self.Location = checkSpot(self.posx, self.posy, area)

        #if prey, encounters cause them to be eaten
        if self.prey == True:
            for enemy in oppCreatures:
                if pg.sprite.collide_rect(self, enemy) == True:
                    self.health = 0
                    self.ifDeath()
                    enemy.hungry(True)
        #if predator select target
        elif self.prey == False:
            distance = 99999
            for enemy in oppCreatures:
                checkDistance = math.sqrt((self.posx - enemy.posx) ** 2 + (self.posy - enemy.posy) ** 2)
                if checkDistance <= distance:
                    distance = checkDistance
                    self.target = enemy

    #Move toward target
    def moveTo(self, area):
        #Find angle to object
        try:
            A = abs(math.degrees(math.atan((self.posy-self.target.posy)/(self.posx-self.target.posx))))
        except ZeroDivisionError:
            A = 90

        verbose("Angle is " + str(A))
        verbose(self.species +" at (" + str(self.posx) + "," + str(self.posy) + ") is targeting (" + str(self.target.posx) + "," + str(self.target.posy) + ")", False)
        
        #check tile movement penalties
        self.heading(abs(math.cos(A)), abs(math.sin(A)), area)
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

    def moveDir(self, tiles, xMove = 99999, yMove = 99999):

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
        self.heading(xMove, yMove, tiles)

        xMove = xMove * self.speedMod
        yMove = yMove * self.speedMod
        verbose("prehead 2 - " + self.species + " at (" + str(self.posx) + "," + str(self.posy) + ") is moving (" + str(xMove) + "," + str(yMove) + "), with speed = " + str(self.speed) + " and mod = " + str(self.speedMod), False)

        return xMove, yMove

    #change movement penalties
    def heading(self, xMove, yMove, tiles):
        #check what land speed is of the given tile
        standingOn = checkSpot(self.posx + xMove, self.posy + yMove, tiles)

        if standingOn.swimming == False:
            self.speedMod = standingOn.landSpeed
        else:
            self.speedMod = self.swimSpeed

    #Move the animal
    def move(self, area, xMove = 0, yMove = 0):

        try:
            xMove, yMove = self.moveTo(area)
            verbose("Call moveTo()", False)
        except AttributeError:
            verbose("Fox at (" + str(self.posx) + "," + str(self.posy) + ") has no target", False)
            xMove, yMove = self.moveDir(area)

        #Move creature to new spot
        verbose(self.species + " at (" + str(self.posx) + "," + str(self.posy) + "), velocity = (" + str(xMove) + "," + str(yMove) + ") to (" + str(self.posx + xMove) + "," + str(self.posy + yMove) + ")" , False)
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
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]
        self.meal = 500
        self.swimSpeed = .3
        self.prey = False

class Rabbit(Animal): 
    #Constructor 
    #rabbit default attributes
    def __init__(self):
        super(Rabbit, self).__init__()
        self.speed = 3
        self.img = os.getcwd() + '/Animals/rabbit.png' 
        self.species = self.img[len(os.getcwd()) + len("/Animals/"):self.img.find(".png")]
        self.hungerPain = 20

#land updater
def checkLocation(creature, tiles):
    verbose(creature.species + " at (" + str(creature.posx) + "," + str(creature.posy) + ")", True)
    verbose(creature.species + " at tile (" + str(int(creature.posx / tile_size)+1) + "," + str(int(creature.posy / tile_size)+1) + ") + biome = " + tiles[int(creature.posx / tile_size)][int(creature.posy / tile_size)].biome, True)

    return (checkSpot(creature.posx, creature.posy, tiles))

#Check future location
def checkSpot(xLocIn, yLocIn, tiles):
    verbose("width " + str(display_width) + " height " + str(display_height), False)
    xLoc = min(xLocIn, display_width - 1)
    yLoc = min(yLocIn, display_height - 1)
    verbose("(xloc, yloc) = (" + str(xLoc) + "," + str(yLoc) + ")", False)
    verbose("(xloctile, yloctile) = (" + str(int(xLoc / tile_size)+1) + "," + str(int(yLoc / tile_size)+1) + ") + tile size = " + str(tile_size), False)
    tileType =  tiles[int(yLoc / tile_size)][int(xLoc / tile_size)]
    verbose("Tile type is " + tileType.biome, False)
    return (tileType)

#Give Animals Initial Placement
def setAnimalSpawn(type, size, mult, tiles):

    N = int(size * mult)

    creatures = pg.sprite.Group()
    
    i = 0
    while (i < N):

        #Create creature
        if type == "fox":
            creature = Fox()
        elif type == "rabbit":
            creature = Rabbit()

        W = randInt(display_width - 2 * tile_size) + tile_size
        H = randInt(display_height - 2 * tile_size) + tile_size
        verbose(creature.species + " initialized at (" + str(W) + "," + str(H) + ")", False)
        verbose(creature.species + " initialized at tile (" + str(int(W / tile_size)+1) + "," + str(int(H / tile_size)+1) + ")", False)
        
        #Make sure animals that can swim dont spawn in water and vice versa, reroll if so
        while checkSpot(W, H, tiles).swimming == True and creature.swimSpeed == 0:
            verbose(creature.species + " cannot swim, rerolling spawn location", False)
            W = randInt(display_width   - 2 * tile_size) - tile_size
            H = randInt(display_height - 2 * tile_size) - tile_size
        
        verbose(creature.species + " spawned at (" + str(W) + "," + str(H) + ")", False)
        verbose(creature.species + " spawned on tile (" + str(int(W / tile_size)+1) + "," + str(int(H / tile_size)+1) + ")", False)
        
        creature.posx = W
        creature.posy = H
        creature.Location = tiles[int(W / tile_size)][int(H / tile_size)].biome
        creature.display()
        creatures.add(creature)

        i = i + 1

    return creatures

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

#Begins map gen, animal spawn and simulation loop
def main():
    
    #generate the map we will use
    map, tiles = gen_map(display_width / tile_size, display_height / tile_size)
    verbose(tiles, False)

    #Create animal groups
    animals = pg.sprite.Group()
    prey = pg.sprite.Group()
    predators = pg.sprite.Group()

    #Call species construction
    foxes = setAnimalSpawn("fox", N, foxFreq, map)
    predators.add(foxes)
    rabbits = setAnimalSpawn("rabbit", N, rabbitFreq, map)
    prey.add(rabbits)
    animals.add(predators,prey)
    
    # Used to manage how fast the screen updates
    clock=pg.time.Clock()

    #Loop until the user clicks the close button.
    done=False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        #iterates through the grid and places a tile
        tiles.update()

        #Move the prey
        prey.update(map, predators)

        #Move the predators
        predators.update(map, prey)

        #Display Tile & Sprite Count
        tileCount = myfont.render("Tiles: " + str(len(tiles)), 1, pg.Color('black'))
        gameDisplay.blit(tileCount, (5, 5))
        predatorCount = myfont.render("Predators: " + str(len(predators)), 1, pg.Color('black'))
        gameDisplay.blit(predatorCount, (5, 20))
        preyCount = myfont.render("Prey: " + str(len(prey)), 1, pg.Color('black'))
        gameDisplay.blit(preyCount, (5, 35))
        animalCount = myfont.render("Animals: " + str(len(animals)), 1, pg.Color('black'))
        gameDisplay.blit(animalCount, (5, 50))

        #Define boarder for the animals
        game_area = pg.Rect(0, 0, display_width, display_height)
        game_area_color = pg.Color('green1')
        pg.draw.rect(gameDisplay, game_area_color, game_area, 2)

        #gameDisplay.fill(black)
        pg.display.flip()
        clock.tick(FPS)


#Begin initializing parameters for sim
if __name__ == '__main__':
    
    #Start Sim
    pg.init()

    #Text labels
    myfont = pg.font.SysFont("Arial", 12)
    black = (0,0,0)

    #Window parameters
    gameDisplay = pg.display.set_mode((display_width,display_height))
    pg.display.set_caption('Ecosystem')
    
    #Main Program Loop
    main()

    #End
    pg.quit()
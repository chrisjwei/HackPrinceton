#py2exe to export it
#AGES OF PROGRESSION MANY SPRITES

import pygame, math, random, time, gc, copy
from pygame.locals import *
from pygame.color import THECOLORS

class Game(object): #holds overall game variables
    gameEnd = False
    playerWins = False
    gameState = "Main" #main menu
    gameCheats = False #cheats are turned off for now
    gameTextFeedback = [time.strftime(time.strftime("%H:%M:%S ",
                                                    time.gmtime())+\
                                      "Game has begun")
                        ,"",""]

class Minimap(object):
    
    def make2dList(self, rows, cols):
        a=[]
        for row in xrange(rows): a += [[0]*cols]
        return a
    
    def __init__(self,rows,cols,blocksize):
        self.blockSize = blocksize #each quandrant is 640x640 pixels
        self.blockRows = rows
        self.blockCols = cols
        self.fogGridInit = self.make2dList(self.blockRows,self.blockCols)
        self.fogGrid = copy.deepcopy(self.fogGridInit)
        self.viewableStructures = []
        self.viewableShips = []
        self.dirs = [[-1,-1],[-1, 0],[-1, 1],
                     [ 0,-1],       [ 0, 1],
                     [ 1,-1],[ 1, 0],[ 1, 1]]

    def update(self):
        self.fogGrid = copy.deepcopy(self.fogGridInit) #reset grid
        for structure in Structure.friendlyStructureList: #updates fog of war (clear)
            (row,col) = (int(abs(structure.x-1))/640,int(abs(structure.y-1))/640) #makes sure it doesnt go off the map
            if structure.powered == True: #must be powered
                self.fogGrid[row][col] = 1 #reveal the area from the fog
                for direction in self.dirs: #updates nearby fog of war blocks (foggy)
                    drow,dcol = direction[0],direction[1]
                    if row+drow >= 0 and row+drow <= self.blockRows \
                       and col+dcol >= 0 and col+dcol <= self.blockCols:
                        if self.fogGrid[row+drow][col+dcol] == 0:
                            self.fogGrid[row+drow][col+dcol] = 2 #2 is foggy, not clear, still visible though
        for ship in FriendlyShip.friendlyShipList:
            (row,col) = (int(abs(ship.x-1))/640,int(abs(ship.y-1))/640) #makes sure it doesnt go off the map
            if row >= 0 and row < self.blockRows \
                   and col >= 0 and col < self.blockCols:
                self.fogGrid[row][col] = 1
            for dir in self.dirs: #updates nearby fog of war blocks (foggy)
                drow,dcol = dir[0],dir[1]
                if row+drow >= 0 and row+drow < self.blockRows \
                   and col+dcol >= 0 and col+dcol < self.blockCols:
                    if self.fogGrid[row+drow][col+dcol] == 0:
                        self.fogGrid[row+drow][col+dcol] = 2 #2 is foggy, not clear, still visible though
                        
    def draw(self,surface):
        self.viewableStructures = []
        self.viewableShips = []
        for row in xrange(self.blockRows):
            for col in xrange(self.blockCols):
                if self.fogGrid[row][col] == 1:
                    pygame.draw.rect(surface,THECOLORS["blue"],Rect(19+(row*16.4),520+(col*16.4),16.4,16.4))
                elif self.fogGrid[row][col] == 2:
                    pygame.draw.rect(surface,THECOLORS["navy"],Rect(19+(row*16.4),520+(col*16.4),16.4,16.4))

                    
        for structure in Structure.structureList:
            x = (((1.0*structure.x)/6400)*164)+19
            y = (((1.0*structure.y)/6400)*164)+520
            size = max(structure.spriteWidth*(0.025625)/2,2) #ratio between map and size
            (row,col) = (int(abs(structure.x-1))/640,int(abs(structure.y-1))/640)
            if self.fogGrid[row][col] == 1 or self.fogGrid[row][col] == 2:
                if structure.isFriendly == True:
                    color = THECOLORS["yellow"]
                elif structure.isFriendly == False:
                    color = THECOLORS["red"]
                else:
                    color = THECOLORS["grey"]
                structure.hidden = False #show the structure
                pygame.draw.rect(surface,color,Rect(x,y,size,size))
                self.viewableStructures.append(structure) #simultaneously finds viewable structures
            else:
                structure.hidden = True #hide the structure
        for ship in Ship.shipList:
            x = (((1.0*ship.x)/6400)*164)+19
            y = (((1.0*ship.y)/6400)*164)+520
            size = max(ship.spriteWidth*(0.025625)/2,1) #ratio between map and size
            (row,col) = (int(abs(ship.x-1))/640,int(abs(ship.y-1))/640)
            if self.fogGrid[row][col] == 1 or self.fogGrid[row][col] == 2:
                if ship.friendly == True:
                    color = THECOLORS["yellow"]
                elif ship.friendly == False:
                    color = THECOLORS["red"]
                else:
                    color = THECOLORS["grey"]
                ship.hidden = False #show the ship
                pygame.draw.rect(surface,color,Rect(x,y,size,size))
                self.viewableShips.append(ship) #simultaneously finds viewable structures
            else:
                ship.hidden = True #hide the structure


class Structure(object):
    structureList = []
    enemyStructureList = []
    friendlyStructureList = []
    
    def __init__(self,parent,x,y,hp,armor,shields):

        self.type = "Structure"
        self.cost = 0 #cost will be used later
        self.x = x #initial position
        self.y = y
        self.isFriendly = True
        self.hp = hp #initial attributes
        self.maxhp = hp 
        self.armor = armor 
        self.maxArmor = armor
        self.shields = shields
        self.maxShields = shields
        self.shieldsTimer = 0 #used to track how long since last damage taken
        self.shieldResetTime = 500 #once it hits 500, start recharge
        self.shieldsRegen = 1 #rate of recharge
        self.hpRegen = 0.1 #rate of repair
        self.selected = False #selected = false by default
        self.UIcolor = THECOLORS["grey"] #ui colors grey, will be changed later
        self.UIcolor2 = THECOLORS["grey"]
        self.UIcolor3 = THECOLORS["grey"]
        self.name = "Structure"
        self.actions = [] #cant take any actions, but opens possibilities of actions for children
        self.actionTypes = [] #records what kind of action each action in self.actions is
        self.actionNumbers = 0 #the count, so we dont have to calculate it every time
        self.castRange = 0 #how far we can build things from this
        self.placingItem = False #this turns true when we want to build something from the selected building
        self.targetBuildPosition = None #where we want to build the building
        self.rallyPointXY = None #where we want our rally point to be
        self.maxUpgrade = 2 #our maxupgrade value will be 2, because sprites are time consuming T__T
        self.energyCost = 0.01
        self.references = set()
        self.removeReferences = False
        self.inactive = True #upon initialization, all structures must go through building process
        self.buildTime = 0
        self.buildTimeEnd = 1000 #10 sec build time by default
        self.hidden = False #holds whether or not to allow structure to be interacted with
        self.children = []
        self.powered = True
        if parent == None:
            self.parents = []
        else:
            self.parents = [parent] #this for powering purposes
             #this is so we can remove our parenthood upon death
            for parent in self.parents:
                parent.children.append(self) #backwards inheritance

    def regenShields(self):
        if self.shields < self.maxShields:
            if self.shieldsTimer == 0:
                self.shields += self.shieldsRegen
            else:
                self.shieldsTimer -= 1
        if self.shields > self.maxShields:
            self.shields = self.maxShields #resets if it overshoots

    def regenHull(self):
        if self.hp < self.maxhp:
            self.hp += self.hpRegen #constant hp regen
            Resources.energy -= self.energyCost*10

    def expendEnergy(self):
        Resources.energy -= self.energyCost

    def rebuild(self):
        self.buildTime += 1
        if self.hp < self.maxhp:
            self.hp += 10
        else:
            self.hp = self.maxhp
        if self.armor < self.maxArmor:
            self.armor += 10
        else:
            self.armor = self.maxArmor
        if self.buildTime >= self.buildTimeEnd:
            self.buildTime = 0 #resets the build time for the next upgrade
            self.inactive = False #sets it to an active building
    
    def loop(self):
        self.powered = False
        if self.parents != None and self.parents != []:
            for parent in self.parents:
                if parent.powered == True:
                    self.powered = True
                    break
        if self.powered == True:
            if self.inactive == True and Resources.energy > 0:
                self.rebuild()
            self.regenShields()
            self.regenHull()
            self.expendEnergy()
        elif self.name != "Base":
            self.parents = []
            self.children = []
        if self.hp <= 0:
            self.onDestroy()

    def onDestroy(self):
        if self.children != []:
            for children in self.children:
                children.parents.remove(self)
        if self.parents != [] and self.parents != None:
            for parent in self.parents:
                parent.children.remove(self)
            
        for ref in self.references:
            ref.attackTarget = None
        if self.isFriendly == True:
            Structure.friendlyStructureList.remove(self)
        if self.isFriendly == False: #this is not an else statement, because of neutral structures
            Structure.enemyStructureList.remove(self)
        Structure.structureList.remove(self)
        self.removeReferences = True

    def distance(self,(x0,y0),(x1,y1)):
        return ((x0 - x1)**2+(y0 - y1)**2)**0.5 

    def placeStructure(self,structure,parent,x,y):
        if self.targetBuildPosition != None:

            if (self.distance((self.x,self.y),self.targetBuildPosition)) < self.castRange:
                Structure.structureList.append(structure(parent,x,y))
                Game.gameTextFeedback.insert(0,("Structure built at (%d,%d)" % (x,y)))
                self.targetBuildPosition = None
            else:
                self.targetBuildPosition = None
                Game.gameTextFeedback.insert(0,"Target position outside of range")

        else:
            self.targetBuildPosition = (x,y)
            self.placeStructure(structure,parent,x,y)

    def rallyPoint(self,x,y):
        if self.targetBuildPosition != None:
            self.targetBuildPosition = None
            self.rallyPointXY = (x,y)
        else:
            self.targetBuildPosition = (x,y)
            self.rallyPoint(x,y)

    def action_sell(self):
        Resources.metal += self.cost/2
        self.onDestroy()

class Turret(Structure):

    cost = [100,50]
    
    def __init__(self,parent,x,y,hp=1000,armor=300,shields=300,friendly=True):
        super(Turret,self).__init__(parent,x,y,hp,armor,shields)
        self.sprites = Sprites.sprTurrets
        self.sprite = Sprites.sprTurrets[0]
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.isFriendly = friendly
        self.name = "Turret"
        self.friendly = True
        self.castRange = 300 #how far we can build things from this
        self.cost = 100
        self.buildTimeEnd = 1000 # 10 seconds
        self.upgrade = 0
        self.upgradeCost = [500,100,0]
        self.inactive = True
        self.type = 0 #bullets
        self.turnSpeed = 0.2
        self.att = [15,30,1] #bullets, missiles,laser
        self.bulletSpeed = 20
        self.missileSpeed = 10
        self.laserSpeed = 50
        self.direction = 0
        self.reload = 0
        self.reloadTicksType = [4,35,.7]
        self.reloadTicks = self.reloadTicksType[0]
        self.dps = self.findDps()
        self.UIColor = THECOLORS["yellow"]
        self.UIColor2 = THECOLORS["pink"]
        self.UIColor3 = THECOLORS["cyan"]
        self.actions = [self.action_upgrade,self.action_changeBullets,self.action_changeMissiles,
                        self.action_changeLasers,self.action_sell]
        self.actionTypes = ["upgrade","alter","alter","alter","sell"]
        self.actionSprites = [Sprites.sprButtonUpgrade,
                              Sprites.sprButtonTurretBullets,
                              Sprites.sprButtonTurretMissiles,
                              Sprites.sprButtonTurretLasers,
                              Sprites.sprButtonSell]
        self.actionNumbers = len(self.actions)
        Structure.friendlyStructureList.append(self)

        self.attributes = [["Name",self.name],
                           ["Type",["Bullets","Missiles","Lasers"][self.type]],
                           ["Range", self.castRange],["DPS", self.dps]]
        self.attributesNumber = len(self.attributes)
        self.upgrading = False
        self.attackTarget = None
        self.turnDirection = 0
        self.targetDir = 0

    def rotateToTargetDir(self): #rotates so the ship is in correct orientation
        if self.targetDir > self.direction:
            cc = self.targetDir - self.direction
            cl = 2*math.pi-self.targetDir + self.direction
        else:
            cc = 2*math.pi-self.direction + self.targetDir
            cl = self.direction - self.targetDir
        if cc < cl:
            self.turnDirection = 1 # 1 is counterclockwise
            self.theta = cc
        else:
            self.turnDirection = -1
            self.theta = cl
        self.direction += self.turnDirection*self.turnSpeed*((self.theta)/(math.pi))
        self.direction = self.direction % (2*math.pi)    

    def findDirFromPos(self,x,y):
        dx = x-self.x
        dy = self.y - y
        r = self.distance((self.x,self.y),(x,y))
        if r != 0 and abs(dx/r) <= 1:
            #arccos always returns positive angle
            if dy >= 0: #if in the positive spectrum
                return math.acos((dx/r)) #just return arccos
            else:
                return 2*math.pi - math.acos((dx/r)) #else return arcos from 2pi

    def findNearbyTargets(self):
        if self.attackTarget == None:
            output = []
            if self.friendly == True:
                shipList = EnemyShip.enemyShipList
                structureList = Structure.enemyStructureList
            else:
                shipList = FriendlyShip.friendlyShipList
                structureList = Structure.friendlyStructureList
            for ship in shipList:
                if self.distance((self.x,self.y),(ship.x,ship.y)) <= self.castRange:
                    output.append(ship)
            if output == []:
                for structure in structureList:
                    if self.distance((self.x,self.y),(structure.x,structure.y)) <= self.castRange:
                        output.append(structure)
            self.targetNearbyTargets(output) #target one of the elements in output
        elif self.distance((self.x,self.y),(self.attackTarget.x,self.attackTarget.y)) > self.castRange:
            self.attackTarget.references.remove(self) #removes reference
            self.attackTarget = None #no attack target

    def targetNearbyTargets(self,targets):
        if self.attackTarget == None and targets != []:
            self.attackTarget = random.choice(targets)
            self.attackTarget.references.add(self)


    def attack(self,target):
        if self.type == 0: #bullet form
            self.targetDir = self.findDirFromPos(target.x,target.y)
            if self.reload >= self.reloadTicks:
                self.reload = 0
                Bullet.bulletList.append(Bullet(self.x,self.y,True,self.att[0],self.bulletSpeed,self.direction,0,0))
                Bullet.bulletList.append(Bullet(self.x,self.y,True,self.att[0],self.bulletSpeed,self.direction,0,0))
        elif self.type == 1: #missile form
            self.targetDir = self.findDirFromPos(target.x,target.y)
            if self.reload >= self.reloadTicks:
                Bullet.bulletList.append(Missile(self.x,self.y,True,self.att[1],self.missileSpeed,self.direction,0,0,self.attackTarget))
                self.reload = 0
        else: #laser form
            self.targetDir = self.findDirFromPos(target.x,target.y)
            Bullet.bulletList.append(Laser(self.x,self.y,True,self.att[2],self.laserSpeed,self.direction,self.attackTarget.x,self.attackTarget.y))
            if self.reload >= self.reloadTicks:
                self.reload = 0
        self.rotateToTargetDir()
        
            
    def rebuild(self):
        self.buildTime += 1
        if self.upgrading == True:
            if self.hp < self.maxhp:
                self.hp += 10
            else:
                self.hp = self.maxhp
            if self.armor < self.maxArmor:
                self.armor += 10
            else:
                self.armor = self.maxArmor
        if self.buildTime >= self.buildTimeEnd:
            self.buildTime = 0 #resets the build time for the next upgrade
            self.inactive = False #sets it to an active building
            self.upgrading = False
    
    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        pygame.draw.circle(surface, THECOLORS["blue"], (x,y), self.castRange, 1)
        if self.inactive == True:
            pygame.draw.arc(surface,THECOLORS["grey"],
                            Rect(x-(self.spriteRadius/2)-20,y-(self.spriteRadius/2)-20,self.spriteRadius+40,self.spriteRadius+40),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.buildTime)/self.buildTimeEnd)),2) #draws build time
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields
    
    def action_changeBullets(self):
        if self.type != 0:
            self.inactive = True
            self.upgrading = False #we are not upgrading
            self.buildTime = self.buildTimeEnd/2 #restart building time
            self.type = 0
            self.sprite = self.sprites[self.type] #change sprite
            self.reloadTicks = self.reloadTicksType[self.type]
            self.attributes = [["Name",self.name],
                           ["Type",["Bullets","Missiles","Lasers"][self.type]],
                           ["Range", self.castRange],["DPS", self.findDps()]]

    def action_changeMissiles(self):
        if self.type != 1:
            self.inactive = True
            self.upgrading = False #we are not upgrading
            self.buildTime = self.buildTimeEnd/2 #restart building time
            self.type = 1
            self.sprite = self.sprites[self.type] #change sprite
            self.reloadTicks = self.reloadTicksType[self.type]
            self.attributes = [["Name",self.name],
                               ["Type",["Bullets","Missiles","Lasers"][self.type]],
                               ["Range", self.castRange],["DPS", self.findDps()]]
            
    def action_changeLasers(self):
        if self.type != 2:
            self.inactive = True
            self.upgrading = False #we are not upgrading
            self.buildTime = self.buildTimeEnd/2 #restart building time
            self.type = 2
            self.sprite = self.sprites[self.type] #change sprite
            self.reloadTicks = self.reloadTicksType[self.type]
            self.attributes = [["Name",self.name],
                               ["Type",["Bullets","Missiles","Lasers"][self.type]],
                               ["Range", self.castRange],["DPS", self.findDps()]]
        

    def action_upgrade(self):
        if Resources.metal >= self.upgradeCost[0] and Resources.energy >= self.upgradeCost[1] and self.upgrade < self.maxUpgrade:
            if self.upgrade <= self.maxUpgrade - 1:
                Resources.metal -= self.upgradeCost[0]
                Resources.energy -= self.upgradeCost[1]
                self.upgrade += 1
                self.doUpgrade(self.upgrade)

    def doUpgrade(self,upgrade):
        self.upgrading = True
        self.inactive = True
        self.upgradeCost[0] *= 30
        self.upgradeCost[1] *= 30
        if upgrade == 1:
            self.castRange = 500
            self.maxhp = 1500
            self.maxArmor = 500
            self.maxShields = 500
            self.att = [20,40,1.5]
        elif upgrade == 2:
            self.att = [25,50,2]
            self.castRange = 700
            self.maxhp = 3000
            self.maxArmor = 1000
            self.maxShields = 1000
        self.attributes = [["Name",self.name],
                           ["Type",["Bullets","Missiles","Lasers"][self.type]],
                           ["Range", self.castRange],["DPS", self.findDps()]]

    def findDps(self):
        return int((100.0/self.reloadTicks)*self.att[self.type])

    def loop(self):
        self.powered = False
        if self.parents != None and self.parents != []:
            for parent in self.parents:
                if parent.powered == True:
                    self.powered = True
                    break
        if self.powered == True:
            if self.inactive == True and Resources.energy > 0:
                self.rebuild()
            else:
                self.regenShields()
                self.regenHull()
                self.expendEnergy()
                self.findNearbyTargets()
                if self.attackTarget != None:
                    self.attack(self.attackTarget)
        else:
            self.parents = []
            self.children = []
        if self.reload <= self.reloadTicks:
            self.reload += 1
        if self.hp <= 0:
            self.onDestroy()
        

class Warpgate(Structure): #the enemy structure
    warpgateCount = 0
    def __init__(self,x,y,shipType,hp,armor,shields):
        super(Warpgate,self).__init__(None,x,y,hp,armor,shields)
        Warpgate.warpgateCount += 1
        self.hidden = True
        self.powered = True
        self.inactive = False
        self.isFriendly = False
        self.shipType = shipType #the type of spawning enemy
        if shipType == EnemyHammerhead or shipType == EnemyCarrier or shipType == EnemyHornet:
            self.level = 2
            self.sprite = Sprites.sprWarpgate2
        elif shipType == EnemyBruiser or shipType == EnemyKnife or shipType == EnemySaucer:
            self.level = 1
            self.sprite = Sprites.sprWarpgate1
        else:
            self.level = 0
            self.sprite = Sprites.sprWarpgate0
        self.UIColor = THECOLORS["red"]
        self.UIColor2 = THECOLORS["blue"]
        self.UIColor3 = THECOLORS["violet"]
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight/2]
        self.name = "Warpgate"
        self.actionNumbers = 0
        self.buildTime = 0
        self.buildTimeEnd = 0 #instant build time
        self.energyCost = 0
        Structure.enemyStructureList.append(self)
        self.attributes = [["Name",self.name],["Space Age", "Tier %d" % self.level],["Warp Enemy", self.shipType.name]]
        self.attributesNumber = len(self.attributes)

    def generateEnemy(self):
        if self.hidden == False and (self.shields < self.maxShields or\
                                     self.armor < self.maxArmor or\
                                     self.hp < self.maxhp):
            if random.random() > 0.99:
                rallyX = self.x+random.gauss(0,32)
                rallyY = self.y+random.gauss(0,32)
                Ship.shipList.append(self.shipType(self.x,self.y,rallyX,rallyY))


    def loop(self):
        if self.hp <= 0:
            self.onDestroy()
        else:
            self.regenShields()
            self.regenHull()
            self.expendEnergy()
            self.generateEnemy()

    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields
    def onDestroy(self):
        super(Warpgate,self).onDestroy()
        Warpgate.warpgateCount -= 1
        Game.gameTextFeedback.insert(0,"Level %d Warpgate Destroyed, %d remaining" \
                                     % (self.level , Warpgate.warpgateCount))
        if Warpgate.warpgateCount == 0:
            Game.gameEnd = True
            Game.playerWins = True



class Base(Structure):
    
    def __init__(self,x,y,hp,armor,shields,friendly):
        super(Base,self).__init__(self,x,y,hp,armor,shields)
        self.inactive = False #only the base starts off completely built
        self.energyLevel = 0#top level
        self.armor = armor
        self.hp = hp
        self.shields = shields
        self.cost = 0
        self.sprite = Sprites.sprBase0
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight/2]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.isFriendly = friendly
        self.name = "Base"
        self.castRange = 500 #how far we can build things from this
        self.upgrade = 0
        self.upgradeCost = [4000,4000,0]
        self.upgradeTime = 6000 #time it takes to u
        self.buildTimeEnd = 6000 # 1 min
        self.energyRate = 0.07
        self.energyPerSecond = int(self.energyRate * 100)
        self.attributes = [["Name",self.name],["Space Age", "Tier %d" % self.upgrade],["Energy per Second", self.energyPerSecond]]
        self.attributesNumber = len(self.attributes)
        self.shieldsRegen = 4
        self.hpRegen = 1
        self.energyCost = 0
        
        if self.isFriendly == True:
            self.UIColor = THECOLORS["yellow"]
            self.UIColor2 = THECOLORS["pink"]
            self.UIColor3 = THECOLORS["cyan"]
            self.actions = [self.action_upgrade,self.action_createBeacon]
            self.actionTypes = ["upgrade","place"]
            self.actionNumbers = len(self.actions)
            self.actionSprites = [Sprites.sprButtonUpgrade,Sprites.sprButtonBeacon]
            Structure.friendlyStructureList.append(self)
        else:
            #self.actions = []
            #self.actionTypes = []
            self.UIColor = THECOLORS["red"]
            self.UIColor2 = THECOLORS["blue"]
            self.UIColor3 = THECOLORS["violet"]
            self.actionNumbers = 0
            Structure.enemyStructureList.append(self)

    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        pygame.draw.circle(surface, THECOLORS["blue"], (x,y), self.castRange, 1)
        if self.inactive == True:
            pygame.draw.arc(surface,THECOLORS["grey"],
                            Rect(x-(self.spriteRadius/2)-20,y-(self.spriteRadius/2)-20,self.spriteRadius+40,self.spriteRadius+40),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.buildTime)/self.buildTimeEnd)),2) #draws build time
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields
        
    def action_createBeacon(self,x,y):
        if Resources.metal >= Beacon.cost[0] and Resources.energy >= Beacon.cost[1]:
            Resources.metal -= Beacon.cost[0]
            Resources.energy -= Beacon.cost[1]
            self.placeStructure(Beacon,self,x,y)
        
    def action_upgrade(self):
        if Resources.metal >= self.upgradeCost[0] and Resources.energy >= self.upgradeCost[1] and self.upgrade < self.maxUpgrade:
            if self.upgrade <= self.maxUpgrade - 1:
                Resources.metal -= self.upgradeCost[0]
                Resources.energy -= self.upgradeCost[1]
                self.upgrade += 1
                self.doUpgrade(self.upgrade)

    def doUpgrade(self,upgrade):
        self.upgradeCost[0] *= 50
        self.upgradeCost[1] *= 50
        self.buildTime = 0
        if upgrade == 1:
            self.sprite = Sprites.sprBase1
            self.castRange += 200
            self.maxhp = 15000
            self.maxArmor = 7000
            self.maxShields = 2000
            self.energyRate = 0.2
            self.energyPerSecond = self.energyRate*100
            self.shieldsRegen = 5
            self.hpRegen = 1.5
            Resources.unitCap += 5
        elif upgrade == 2:
            self.sprite = Sprites.sprBase2
            self.castRange += 200
            self.maxhp = 2000
            self.maxArmor = 600
            self.maxShields = 600
            self.energyRate = 0.3
            self.energyPerSecond = self.energyRate*100
            self.shieldsRegen = 6
            self.hpRegen = 2
            Resources.unitCap += 5
        self.inactive = True
        self.attributes = [["Name",self.name],["Space Age", "Tier %d" % self.upgrade],["Energy per Second", self.energyPerSecond]]


    def loop(self):
        super(Base, self).loop()
        if self.inactive == True:
            self.rebuild()
        self.powered = True
        Resources.energy += self.energyRate

    def onDestroy(self):
        super(Base,self).onDestroy()
        Game.gameTextFeedback.insert(0,"Base destroyed, Game over")
        Game.gameEnd = True #game is done
        Game.playerWins = False #player loses

class Beacon(Structure):

    cost = [50,50,0]
    
    def __init__(self,parent,x,y,hp=1000,armor=100,shields=100,friendly=True):
        super(Beacon,self).__init__(parent,x,y,hp,armor,shields)
        self.sprite = Sprites.sprBeacon0
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.isFriendly = friendly
        self.name = "Beacon"
        self.castRange = 400 #how far we can build things from this
        self.cost = 100
        self.buildTimeEnd = 700 # 7 seconds
        self.upgrade = 0
        self.upgradeCost = [100,100,0]
        self.inactive = True
        self.energyLevel = parent.energyLevel + 1
        
        if self.isFriendly == True:
            self.UIColor = THECOLORS["yellow"]
            self.UIColor2 = THECOLORS["pink"]
            self.UIColor3 = THECOLORS["cyan"]
            self.actions = [self.action_upgrade,self.action_adopt,self.action_createBeacon,
                            self.action_createTurret, self.action_createBarracks,
                            self.action_createFactory,self.action_sell]
            self.actionTypes = ["upgrade","adopt","place","place","place","place","sell"]
            self.actionSprites = [Sprites.sprButtonUpgrade,
                                  Sprites.sprButtonTarget,
                                  Sprites.sprButtonBeacon,
                                  Sprites.sprButtonTurret,
                                  Sprites.sprButtonBarracks,
                                  Sprites.sprButtonFactory,
                                  Sprites.sprButtonSell]
            self.actionNumbers = len(self.actions)
            Structure.friendlyStructureList.append(self)
        else:
            self.UIColor = THECOLORS["red"]
            self.UIColor2 = THECOLORS["blue"]
            self.UIColor3 = THECOLORS["violet"]
            Structure.enemyStructureList.append(self)

        self.attributes = [["Name",self.name],["Range", self.castRange],["Generation", self.energyLevel]]
        self.attributesNumber = len(self.attributes)
    
    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        pygame.draw.circle(surface, THECOLORS["blue"], (x,y), self.castRange, 1)
        if self.inactive == True:
            pygame.draw.arc(surface,THECOLORS["grey"],
                            Rect(x-(self.spriteRadius/2)-20,y-(self.spriteRadius/2)-20,self.spriteRadius+40,self.spriteRadius+40),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.buildTime)/self.buildTimeEnd)),2) #draws build time
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields
    def action_adopt(self,x,y):
        pass
    
    def action_createBeacon(self,x,y):
        if Resources.metal >= Beacon.cost[0] and Resources.energy >= Beacon.cost[1]:
            Resources.metal -= Beacon.cost[0]
            Resources.energy -= Beacon.cost[1]
            self.placeStructure(Beacon,self,x,y)

    def action_createTurret(self,x,y):
        if Resources.metal >= Turret.cost[0] and Resources.energy >= Turret.cost[1]:
            Resources.metal -= Turret.cost[0]
            Resources.energy -= Turret.cost[1]
            self.placeStructure(Turret,self,x,y)
    
    def action_createBarracks(self,x,y):
        if Resources.metal >= Barracks.cost[0] and Resources.energy >= Barracks.cost[1]:
            Resources.metal -= Barracks.cost[0]
            Resources.energy -= Barracks.cost[1]
            self.placeStructure(Barracks,self,x,y)
            
    def action_createFactory(self,x,y):
        if Resources.metal >= Factory.cost[0] and Resources.energy >= Factory.cost[1]:
            Resources.metal -= Factory.cost[0]
            Resources.energy -= Factory.cost[1]
            self.placeStructure(Factory,self,x,y)

    def action_upgrade(self):
        if Resources.metal >= self.upgradeCost[0] and Resources.energy >= self.upgradeCost[1] and self.upgrade < self.maxUpgrade:
            if self.upgrade <= self.maxUpgrade - 1:
                Resources.metal -= self.upgradeCost[0]
                Resources.energy -= self.upgradeCost[1]
                self.upgrade += 1
                self.doUpgrade(self.upgrade)
                Game.gameTextFeedback.insert(0,"Beacon upgraded to level %d" \
                                     % self.upgrade)
            else:
                Game.gameTextFeedback.insert(0,"Max upgrade reached")
        else:
            Game.gameTextFeedback.insert(0,"More resources required M:%d E:%d" \
                                     %(self.upgradeCost[0],self.upgradeCost[1]))

    def doUpgrade(self,upgrade):
        self.inactive = True
        self.upgradeCost[0] *= 30
        self.upgradeCost[1] *= 30
        if upgrade == 1:
            self.sprite = Sprites.sprBeacon1
            self.castRange = 700
            self.maxhp = 1500
            self.maxArmor = 500
            self.maxShields = 500
        elif upgrade == 2:
            self.sprite = Sprites.sprBeacon2
            self.castRange = 1200
            self.maxhp = 3000
            self.maxArmor = 1000
            self.maxShields = 1000
            

    def loop(self):
        super(Beacon, self).loop()
        self.attributes = [["Name",self.name],["Range", self.castRange],["Generation", self.energyLevel]]

class Barracks(Structure):
    
    cost = [200,50,0]
    
    def __init__(self,parent,x,y,hp=1000,armor=100,shields=100,friendly=True):
        super(Barracks,self).__init__(parent,x,y,hp,armor,shields)
        self.inactive = True
        self.sprite = Sprites.sprBarracks[0]
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.isFriendly = friendly
        self.name = "Barracks"
        self.castRange = 200 #how far we can build things from this
        #self.cost = [500,500,0]
        self.upgrade = 0
        self.buildTimeEnd = 2000 # 20 seconds
        self.upgradeCost = [500,80,0]
        self.barrackSize = 0 #small
        self.barrackSizeLabels = ["Small","Medium","Large","Huge"]
        #self.units = [Ship]
        
        if self.isFriendly == True:
            self.UIColor = THECOLORS["yellow"]
            self.UIColor2 = THECOLORS["pink"]
            self.UIColor3 = THECOLORS["cyan"]
            self.actions = [self.action_upgrade,self.action_rallyPoint,
                            self.action_createUnitBullets,
                            self.action_createUnitMissiles,
                            self.action_createUnitLasers,
                            self.action_sell]
            self.actionTypes = ["upgrade","rally","unit","unit","unit","sell"]
            self.actionSprites = [Sprites.sprButtonUpgrade,
                                  Sprites.sprButtonRally,
                                  Sprites.sprButtonBuildShipBullets,
                                  Sprites.sprButtonBuildShipMissiles,
                                  Sprites.sprButtonBuildShipLasers,
                                  Sprites.sprButtonSell]
            self.actionNumbers = len(self.actions)
            Structure.friendlyStructureList.append(self)
            
        else:
            self.UIColor = THECOLORS["red"]
            self.UIColor2 = THECOLORS["blue"]
            self.UIColor3 = THECOLORS["violet"]
            Structure.enemyStructureList.append(self)

        self.attributes = [["Name",self.name],
                           ["Size", self.barrackSizeLabels[self.barrackSize]]]
        self.attributesNumber = len(self.attributes)

    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        pygame.draw.circle(surface, THECOLORS["blue"], (x,y), self.castRange, 1)
        if self.inactive == True:
            pygame.draw.arc(surface,THECOLORS["grey"],
                            Rect(x-(self.spriteRadius/2)-20,y-(self.spriteRadius/2)-20,self.spriteRadius+40,self.spriteRadius+40),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.buildTime)/self.buildTimeEnd)),2) #draws build time
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields

    def action_upgrade(self):
        if Resources.metal >= self.upgradeCost[0] and Resources.energy >= self.upgradeCost[1]:
            if self.upgrade < self.maxUpgrade:
                Resources.metal -= self.upgradeCost[0]
                Resources.energy -= self.upgradeCost[1]
                self.barrackSize += 1
                self.upgrade += 1
                self.doUpgrade(self.upgrade)
            else:
                Game.gameTextFeedback.insert(0,"Max upgrade reached")
        else:
            Game.gameTextFeedback.insert(0,"More resources required M:%d E:%d" \
                                     %(self.upgradeCost[0],self.upgradeCost[1]))

    def doUpgrade(self,upgrade):
        self.inactive = True #cannot preform actions until completely done 
        self.sprite = Sprites.sprBarracks[upgrade]
        self.upgradeCost[0] *= (upgrade+1)**1
        self.upgradeCost[1] *= (upgrade+1)**1
        if upgrade == 1:
            self.castRange = 300
            self.maxhp = 1500
            self.maxArmor = 500
            self.maxShields = 500
        elif upgrade == 2:
            self.castRange = 500
            self.maxhp = 3000
            self.maxArmor = 1000
            self.maxShields = 1000
        self.attributes = [["Name",self.name],
                           ["Size", self.barrackSizeLabels[self.barrackSize]]]

    def action_rallyPoint(self,x,y):
        self.rallyPoint(x,y)       

    def action_createUnitBullets(self): #just ship
        shipClass = [FriendlyBasic,FriendlyKnife,FriendlyHornet][self.upgrade]
        if FriendlyShip.friendlyShipNumber < Resources.unitCap and Resources.metal >= shipClass.cost:
            Resources.metal -= shipClass.cost
            if self.rallyPointXY != None:
                Ship.shipList.append(shipClass(self.x,self.y,self.rallyPointXY[0],self.rallyPointXY[1]))
            else:
                Ship.shipList.append(shipClass(self.x,self.y,self.x,self.y))
    
    def action_createUnitMissiles(self): #just ship
        shipClass = [FriendlyBomber,FriendlySaucer,FriendlyCarrier][self.upgrade]
        if FriendlyShip.friendlyShipNumber < Resources.unitCap and Resources.metal >= shipClass.cost:
            Resources.metal -= shipClass.cost
            if self.rallyPointXY != None:
                Ship.shipList.append(shipClass(self.x,self.y,self.rallyPointXY[0],self.rallyPointXY[1]))
            else:
                Ship.shipList.append(shipClass(self.x,self.y,self.x,self.y))

    def action_createUnitLasers(self): #just ship
        shipClass = [FriendlyLaser,FriendlyBruiser,FriendlyHammerhead][self.upgrade]
        if FriendlyShip.friendlyShipNumber < Resources.unitCap and Resources.metal >= shipClass.cost:
            Resources.metal -= shipClass.cost
            if self.rallyPointXY != None:
                Ship.shipList.append(shipClass(self.x,self.y,self.rallyPointXY[0],self.rallyPointXY[1]))
            else:
                Ship.shipList.append(shipClass(self.x,self.y,self.x,self.y))

    def loop(self):
        super(Barracks, self).loop()
        

class Factory(Structure):
    
    cost = [100,25,0]
    
    def __init__(self,parent,x,y,hp=1000,armor=100,shields=100,friendly=True):
        super(Factory,self).__init__(parent,x,y,hp,armor,shields)
        self.inactive = True
        self.sprite = Sprites.sprFactory[0]
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,
                     y-self.spriteWidth/2,y+self.spriteHeight]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.isFriendly = friendly
        self.name = "Factory"
        self.castRange = 800
        self.upgrade = 0
        self.upgradeCost = [100,50,0]
        self.factorySize = 0 #small
        self.factorySizeLabels = ["Small","Medium","Large","Huge"]
        self.target = None
        self.miningSpeed = 0.1
        #self.units = [Ship]
        
        if self.isFriendly == True:
            self.UIColor = THECOLORS["yellow"]
            self.UIColor2 = THECOLORS["pink"]
            self.UIColor3 = THECOLORS["cyan"]
            self.actions = [self.action_upgrade,self.action_targetAsteroid,self.action_sell]
            self.actionTypes = ["upgrade","target","sell"]
            self.actionNumbers = len(self.actions)
            self.actionSprites = [Sprites.sprButtonUpgrade,
                                  Sprites.sprButtonTarget,
                                  Sprites.sprButtonSell]
            Structure.friendlyStructureList.append(self)
            
        else:
            self.UIColor = THECOLORS["red"]
            self.UIColor2 = THECOLORS["blue"]
            self.UIColor3 = THECOLORS["violet"]
            Structure.enemyStructureList.append(self)

        self.attributes = [["Name",self.name],
                           ["Size", self.factorySizeLabels[self.factorySize]],
                           ["Mining Speed",self.miningSpeed]]
        self.attributesNumber = len(self.attributes)

    def loop(self):
        super(Factory,self).loop()
        if self.target != None and self.inactive == False and self.target.hidden == False:
            if self.target.resources != 0:
                self.target.resources -= self.miningSpeed
                Resources.metal += self.miningSpeed
            else:
                self.target = None #ran out of material
        else:
            self.target = None  #became hidden or inactive
        self.attributes = [["Name",self.name],["Size", self.factorySizeLabels[self.factorySize]],["Mining Speed",self.miningSpeed]]

    def action_upgrade(self):
        if Resources.metal >= self.upgradeCost[0] and Resources.energy >= self.upgradeCost[1]:
            if self.upgrade < self.maxUpgrade:
                Resources.metal -= self.upgradeCost[0]
                Resources.energy -= self.upgradeCost[1]
                self.factorySize += 1
                self.sprite = Sprites.sprFactory[self.factorySize]
                self.upgrade += 1
                self.doUpgrade(self.upgrade)
            else:
                Game.gameTextFeedback.insert(0,"Max upgrade reached")
        else:
            Game.gameTextFeedback.insert(0,"More resources required M:%d E:%d" \
                                     %(self.upgradeCost[0],self.upgradeCost[1]))

    def doUpgrade(self,upgrade):
        self.inactive = True #begins build process
        self.upgradeCost[0] *= (upgrade+1)**2
        self.upgradeCost[1] *= (upgrade+1)**2
        if upgrade == 1:
            self.miningSpeed = 0.15
            self.maxhp = 1500
            self.maxArmor = 500
            self.maxShields = 500
        elif upgrade == 2:
            self.miningSpeed = 0.20
            self.maxhp = 2000
            self.maxArmor = 600
            self.maxShields = 600
        self.attributes = [["Name",self.name],
                           ["Size", self.factorySizeLabels[self.factorySize]],
                           ["Mining Speed",self.miningSpeed]]

    def action_targetAsteroid(self,asteroid):
        self.target = asteroid
        
    def drawSelected(self,surface,x,y,dx,dy):
        (x,y) = (x+dx,y+dy)
        pygame.draw.circle(surface, THECOLORS["blue"], (x,y), self.castRange, 1)
        if self.inactive == True:
            pygame.draw.arc(surface,THECOLORS["grey"],
                            Rect(x-(self.spriteRadius/2)-20,y-(self.spriteRadius/2)-20,self.spriteRadius+40,self.spriteRadius+40),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.buildTime)/self.buildTimeEnd)),2) #draws build time
        if self.hp > 0:
            pygame.draw.arc(surface,self.UIColor,
                            Rect(x-(self.spriteRadius/2)-8,y-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.hp)/self.maxhp)),2) #draws health
        if self.armor > 0:
            pygame.draw.arc(surface,self.UIColor2,
                            Rect(x-(self.spriteRadius/2)-12,y-(self.spriteRadius/2)-12,self.spriteRadius+24,self.spriteRadius+24),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.armor)/self.maxArmor)),2) #draws armor
        if self.shields > 0:
            pygame.draw.arc(surface,self.UIColor3,
                            Rect(x-(self.spriteRadius/2)-16,y-(self.spriteRadius/2)-16,self.spriteRadius+32,self.spriteRadius+32),
                            math.pi/2,((math.pi/2)+2*math.pi*(float(self.shields)/self.maxShields)),2) #draws shields
        if self.target != None:
            pygame.draw.line(surface,THECOLORS["cyan"],(x,y),(self.target.x+dx,self.target.y+dy),2)

class Asteroid(Structure):
    asteroidList = []
    
    def __init__(self,x,y,resources):
        super(Asteroid,self).__init__(None,x,y,0,0,0)
        self.animationRotation = random.uniform(0,360)
        self.name = "Asteroid"
        self.isFriendly = None #its neutral
        Asteroid.asteroidList.append(self)
        self.resources = resources #asteroids uses resources to tell when to on destory
        self.maxResources = resources
        self.attributes = [["Name",self.name],["Resources", self.resources]]
        self.attributesNumber = len(self.attributes)
        self.actionNumbers = 0
        if self.maxResources < 500:
            self.size = 0
        elif self.maxResources < 1000:
            self.size = 1
        elif self.maxResources < 10000:
            self.size = 2
        elif self.maxResources < 500000:
            self.size = 3
        else:
            self.size = 4
        self.sprite = pygame.transform.rotate(Sprites.sprAsteroid[self.size][random.randint(0,2)],self.animationRotation)
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()
        self.rect = [x-self.spriteWidth/2,x+self.spriteWidth/2,y-self.spriteWidth/2,y+self.spriteHeight]
        self.spriteRadius = (self.spriteHeight**2 + self.spriteWidth**2)**0.5
        self.UIColor = THECOLORS["grey"]

    def drawSelected(self,surface,x,y,dx,dy):
        pygame.draw.arc(surface,self.UIColor,
                        Rect(x+dx-(self.spriteRadius/2)-8,y+dy-(self.spriteRadius/2)-8,self.spriteRadius+16,self.spriteRadius+16),
                        math.pi/2,((math.pi/2)+2*math.pi*(float(self.resources)/self.maxResources)),2) #draws health

    def loop(self):
        self.attributes = [["Name",self.name],["Resources", self.resources]] #updates attributes
        if self.resources <= 0:
            self.onDestroy()

    def onDestroy(self):
        super(Asteroid,self).onDestroy()
        Asteroid.asteroidList.remove(self)

class Resources(object):
        metal = 300
        energy = 300
        unitCap = 10
                
class Camera(object):

    def __init__(self,width,height,mapHeight,mapWidth,dx=0,dy=0):
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.mapHeight = mapHeight
        self.mapWidth = mapWidth
        self.xvel = 0
        self.yvel = 0

    def isWithinView(self,x,y):
        return x >= self.minx and x <= self.maxx and y >= self.miny and y <= self.maxy

    def loop(self):
        prevdx = self.dx
        prevdy = self.dy
        self.dx += self.xvel
        self.dy += self.yvel
        if self.dx > 0 or self.dx < -self.mapWidth+self.width: self.dx = prevdx
        if self.dy > 0 or self.dy < -self.mapHeight+self.height+200: self.dy = prevdy
        
        
        
class Vector(object):

    def __init__(self,x,y): #given <xi,yj>
        self.x = x
        self.y = y #be careful <<
        self.length = ((x**2)+(y**2))**0.5

    def __eq__(self,other): #if the two components equal
        return self.x == other.x and self.y == other.y

    def angle(self): #finds angle from 0 in radians
        if self.length != 0 and abs(self.x/self.length) <= 1:
            #arccos always returns positive angle
            if self.y >= 0: #if in the posritive spectrum
                return math.acos((self.x/self.length)) #just return arccos
            else:
                return 2*math.pi - math.acos(self.x/self.length)
        else:
            return 0

    def dot(self,other):
        return (self.x*other.x) + (self.y*other.y)

    def sub(self,other):
        return Vector(self.x-other.x,self.y-other.y)

    def angleBetween(self,other):
        return abs(self.angle() - other.angle())

    def unit(self):
        if self.length != 0:
            return Vector(self.x/self.length,self.y/self.length)
        else:
            return Vector(0,0)

    
    
class Sprites(object):
    sprShip = pygame.image.load("Sprites/Ships/spr_SpaceShip.png").convert_alpha()
    sprShipFront = pygame.image.load("Sprites/Ships/spr_SpaceShip_front.png").convert_alpha()
    sprShipRight = pygame.image.load("Sprites/Ships/spr_SpaceShip_right.png").convert_alpha()
    sprShipLeft = pygame.image.load("Sprites/Ships/spr_SpaceShip_left.png").convert_alpha()
    sprShipBack = pygame.image.load("Sprites/Ships/spr_SpaceShip_back.png").convert_alpha()
    sprEnemyShip = pygame.image.load("Sprites/Ships/spr_SpaceShipEnemy.png").convert_alpha()
    
    sprShipBruiser = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiser.png").convert_alpha()
    sprShipBruiserEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiserEnemy.png").convert_alpha()
    sprShipBruiserLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiser_left.png").convert_alpha()
    sprShipBruiserRight = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiser_right.png").convert_alpha()
    sprShipBruiserFront = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiser_front.png").convert_alpha()
    sprShipBruiserBack = pygame.image.load("Sprites/Ships/spr_SpaceShipBruiser_back.png").convert_alpha()

    sprShipSaucer = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucer.png").convert_alpha()
    sprShipSaucerEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucerEnemy.png").convert_alpha()
    sprShipSaucerLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucer_left.png").convert_alpha()
    sprShipSaucerRight = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucer_right.png").convert_alpha()
    sprShipSaucerFront = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucer_front.png").convert_alpha()
    sprShipSaucerBack = pygame.image.load("Sprites/Ships/spr_SpaceShipSaucer_back.png").convert_alpha()

    sprShipKnife = pygame.image.load("Sprites/Ships/spr_SpaceShipKnife.png").convert_alpha()
    sprShipKnifeEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipKnifeEnemy.png").convert_alpha()
    sprShipKnifeLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipKnife_left.png").convert_alpha()
    sprShipKnifeRight = pygame.image.load("Sprites/Ships/spr_SpaceShipKnife_right.png").convert_alpha()
    sprShipKnifeFront = pygame.image.load("Sprites/Ships/spr_SpaceShipKnife_front.png").convert_alpha()
    sprShipKnifeBack = pygame.image.load("Sprites/Ships/spr_SpaceShipKnife_back.png").convert_alpha()
    
    sprShipBomber = pygame.image.load("Sprites/Ships/spr_SpaceShipBomber.png").convert_alpha()
    sprShipBomberEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipBomberEnemy.png").convert_alpha()
    sprShipBomberLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipBomber_left.png").convert_alpha()
    sprShipBomberRight = pygame.image.load("Sprites/Ships/spr_SpaceShipBomber_right.png").convert_alpha()
    sprShipBomberFront = pygame.image.load("Sprites/Ships/spr_SpaceShipBomber_front.png").convert_alpha()
    sprShipBomberBack = pygame.image.load("Sprites/Ships/spr_SpaceShipBomber_back.png").convert_alpha()

    sprShipLaser = pygame.image.load("Sprites/Ships/spr_SpaceShipLaser.png").convert_alpha()
    sprShipLaserEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipLaserEnemy.png").convert_alpha()
    sprShipLaserLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipLaser_left.png").convert_alpha()
    sprShipLaserRight = pygame.image.load("Sprites/Ships/spr_SpaceShipLaser_right.png").convert_alpha()
    sprShipLaserFront = pygame.image.load("Sprites/Ships/spr_SpaceShipLaser_front.png").convert_alpha()
    sprShipLaserBack = pygame.image.load("Sprites/Ships/spr_SpaceShipLaser_back.png").convert_alpha()

    sprShipCarrier = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrier.png").convert_alpha()
    sprShipCarrierEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrierEnemy.png").convert_alpha()
    sprShipCarrierLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrier_left.png").convert_alpha()
    sprShipCarrierRight = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrier_right.png").convert_alpha()
    sprShipCarrierFront = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrier_front.png").convert_alpha()
    sprShipCarrierBack = pygame.image.load("Sprites/Ships/spr_SpaceShipCarrier_back.png").convert_alpha()

    sprShipHornet = pygame.image.load("Sprites/Ships/spr_SpaceShipHornet.png").convert_alpha()
    sprShipHornetEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipHornetEnemy.png").convert_alpha()
    sprShipHornetLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipHornet_omni.png").convert_alpha()
    sprShipHornetRight = pygame.image.load("Sprites/Ships/spr_SpaceShipHornet_omni.png").convert_alpha()
    sprShipHornetFront = pygame.image.load("Sprites/Ships/spr_SpaceShipHornet_omni.png").convert_alpha()
    sprShipHornetBack = pygame.image.load("Sprites/Ships/spr_SpaceShipHornet_omni.png").convert_alpha()

    sprShipHammerhead = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerhead.png").convert_alpha()
    sprShipHammerheadEnemy = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerheadEnemy.png").convert_alpha()
    sprShipHammerheadLeft = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerhead_left.png").convert_alpha()
    sprShipHammerheadRight = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerhead_right.png").convert_alpha()
    sprShipHammerheadFront = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerhead_front.png").convert_alpha()
    sprShipHammerheadBack = pygame.image.load("Sprites/Ships/spr_SpaceShipHammerhead_back.png").convert_alpha()

    sprMissile = pygame.image.load("Sprites/Bullets/spr_Missile.png").convert_alpha()
    bgSpace = pygame.image.load("Sprites/Background/bg_Space.jpg")
    
    tutPage1 = pygame.image.load("Sprites/Tutorial/tut_page1.jpg")
    tutPage2 = pygame.image.load("Sprites/Tutorial/tut_page2.jpg")
    tutPage3 = pygame.image.load("Sprites/Tutorial/tut_page3.jpg")
    tutPage4 = pygame.image.load("Sprites/Tutorial/tut_page4.jpg")
    tutPage5 = pygame.image.load("Sprites/Tutorial/tut_page5.jpg")
    tutPage6 = pygame.image.load("Sprites/Tutorial/tut_page6.jpg")
    tutPages = [tutPage1,tutPage2,tutPage3,tutPage4,tutPage5,tutPage6]
    
    sprMouse = pygame.image.load("Sprites/spr_Cursor.png").convert_alpha()
    sprMenu = pygame.image.load("Sprites/Misc/spr_ui_menubar.png").convert_alpha()
    sprBase0 = pygame.image.load("Sprites/Buildings/spr_Base_0.png").convert_alpha()
    sprBase1 = pygame.image.load("Sprites/Buildings/spr_Base_1.png").convert_alpha()
    sprBase2 = pygame.image.load("Sprites/Buildings/spr_Base_2.png").convert_alpha()
    
    sprBeacon0 = pygame.image.load("Sprites/Buildings/spr_Beacon_0.png").convert_alpha()
    sprBeacon1 = pygame.image.load("Sprites/Buildings/spr_Beacon_1.png").convert_alpha()
    sprBeacon2 = pygame.image.load("Sprites/Buildings/spr_Beacon_2.png").convert_alpha()
    
    sprBarracks = [pygame.image.load("Sprites/Buildings/spr_Barracks_0.png").convert_alpha(),
                   pygame.image.load("Sprites/Buildings/spr_Barracks_1.png").convert_alpha(),
                   pygame.image.load("Sprites/Buildings/spr_Barracks_2.png").convert_alpha()]
    sprFactory = [pygame.image.load("Sprites/Buildings/spr_Factory_0.png").convert_alpha(),
                  pygame.image.load("Sprites/Buildings/spr_Factory_1.png").convert_alpha(),
                  pygame.image.load("Sprites/Buildings/spr_Factory_2.png").convert_alpha()]
    sprTurrets = [pygame.image.load("Sprites/Buildings/spr_Turret_Bullets_0.png").convert_alpha(),
                  pygame.image.load("Sprites/Buildings/spr_Turret_Missiles_0.png").convert_alpha(),
                  pygame.image.load("Sprites/Buildings/spr_Turret_Lasers_0.png").convert_alpha()] 
    sprMenuTop = pygame.image.load("Sprites/Misc/spr_ui_resourcebar.png").convert_alpha()
    sprWarpgate2 = pygame.image.load("Sprites/Buildings/spr_Warpgate_2.png").convert_alpha()
    sprWarpgate1 = pygame.image.load("Sprites/Buildings/spr_Warpgate_1.png").convert_alpha()
    sprWarpgate0 = pygame.image.load("Sprites/Buildings/spr_Warpgate_0.png").convert_alpha()

    sprAsteroidTiny1 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsTiny/tiny_asteroid_1.png").convert_alpha()
    sprAsteroidTiny2 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsTiny/tiny_asteroid_2.png").convert_alpha()
    sprAsteroidTiny3 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsTiny/tiny_asteroid_3.png").convert_alpha()
    sprAsteroidSmall1 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsSmall/small_asteroid_1.png").convert_alpha()
    sprAsteroidSmall2 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsSmall/small_asteroid_2.png").convert_alpha()
    sprAsteroidSmall3 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsSmall/small_asteroid_3.png").convert_alpha()
    sprAsteroidMedium1 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsMedium/medium_asteroid_1.png").convert_alpha()
    sprAsteroidMedium2 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsMedium/medium_asteroid_2.png").convert_alpha()
    sprAsteroidMedium3 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsMedium/medium_asteroid_3.png").convert_alpha()
    sprAsteroidBig1 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsBig/big_asteroid_1.png").convert_alpha()
    sprAsteroidBig2 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsBig/big_asteroid_2.png").convert_alpha()
    sprAsteroidBig3 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsBig/big_asteroid_3.png").convert_alpha()
    sprAsteroidHuge1 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsHuge/huge_asteroid_1.png").convert_alpha()
    sprAsteroidHuge2 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsHuge/huge_asteroid_2.png").convert_alpha()
    sprAsteroidHuge3 = pygame.image.load("Sprites/Buildings/Asteroids/AsteroidsHuge/huge_asteroid_3.png").convert_alpha()
    
    sprAsteroid = [[sprAsteroidTiny1,sprAsteroidTiny2,sprAsteroidTiny3],
                   [sprAsteroidSmall1,sprAsteroidSmall2,sprAsteroidSmall3],
                   [sprAsteroidMedium1,sprAsteroidMedium2,sprAsteroidMedium3],
                   [sprAsteroidBig1,sprAsteroidBig2,sprAsteroidBig3],
                   [sprAsteroidHuge1,sprAsteroidHuge2,sprAsteroidHuge3]]
    sprWorkerShip = pygame.image.load("Sprites/Ships/spr_WorkerShip.png").convert_alpha()
    sprButtonBarracks = pygame.image.load("Sprites/UI/spr_button_barracks.png").convert_alpha()
    sprButtonBeacon = pygame.image.load("Sprites/UI/spr_button_beacon.png").convert_alpha()
    sprButtonBuildShipBullets = pygame.image.load("Sprites/UI/spr_button_buildShipBullets.png").convert_alpha()
    sprButtonBuildShipMissiles = pygame.image.load("Sprites/UI/spr_button_buildShipMissiles.png").convert_alpha()
    sprButtonBuildShipLasers = pygame.image.load("Sprites/UI/spr_button_buildShipLasers.png").convert_alpha()
    sprButtonFactory = pygame.image.load("Sprites/UI/spr_button_factory.png").convert_alpha()                          
    sprButtonRally = pygame.image.load("Sprites/UI/spr_button_rally.png").convert_alpha()
    sprButtonTarget = pygame.image.load("Sprites/UI/spr_button_target.png").convert_alpha()
    sprButtonUpgrade = pygame.image.load("Sprites/UI/spr_button_upgrade.png").convert_alpha()
    sprButtonSell = pygame.image.load("Sprites/UI/spr_button_sell.png").convert_alpha()
    sprButtonTurret = pygame.image.load("Sprites/UI/spr_button_turret.png").convert_alpha()
    sprButtonTurretBullets = pygame.image.load("Sprites/UI/spr_button_turret_bullets.png").convert_alpha()
    sprButtonTurretLasers = pygame.image.load("Sprites/UI/spr_button_turret_lasers.png").convert_alpha()
    sprButtonTurretMissiles = pygame.image.load("Sprites/UI/spr_button_turret_missiles.png").convert_alpha()

    bgMainscreen = pygame.image.load("Sprites/Background/bg_Mainscreen.jpg")
    bgMainscreenParallax1 = pygame.image.load("Sprites/Background/mainscreen_parallax1.png").convert_alpha()
    bgMainscreenParallax2 = pygame.image.load("Sprites/Background/mainscreen_parallax2.png").convert_alpha()
    bgMainscreenButton = pygame.image.load("Sprites/Background/mainscreen_button.png").convert_alpha()

    bgWinScreen = pygame.image.load("Sprites/WinLose/bgWin.jpg")
    bgLoseScreen = pygame.image.load("Sprites/WinLose/bgLose.jpg")
    

    
class Background(object):
    def __init__(self):
        self.sprite = Sprites.bgSpace
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()

class Mouse(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.sprite = Sprites.sprMouse
        self.spriteHeight = self.sprite.get_height()
        self.spriteWidth = self.sprite.get_width()

class Line(object):

    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def getIntersection(self,rect):
        #liang-barsky algo
        (xmin,xmax,ymin,ymax) = (rect[0],rect[1],rect[2],rect[3])
        (u1list,u2list) = ([],[])
        if self.x1 == self.x2 and self.y1 == self.y2:
            return self.x1 <= xmax and self.x1 >= xmin and self.y1 <= ymax and self.y1 >= ymin
        dx = self.x2-self.x1
        dy = self.y2-self.y1
        p = [-dx,dx,-dy,dy]
        q = [self.x1-xmin,xmax-self.x1,self.y1-ymin,ymax-self.y1]
        for i in xrange(4):
            if p[i] == 0:
                if q[i] < 0:
                    return False
            elif p[i] < 0:
                u1list.append(float(q[i])/float(p[i]))
            else:
                u2list.append(float(q[i])/float(p[i]))
        u1 = max(0,max(u1list))
        u2 = min(1,min(u2list))
        if u1 > u2:
            return False
        else:
            return True

class Bullet(object):

    bulletList = []

    @classmethod
    def getBulletList(cls):
        return Bullet.bulletList

    def __init__(self,x,y,isfriendly,att,speed,direction,ix,iy):

        self.sprite = None # this denotes a line drawing
        self.friendly = isfriendly
        self.att = att
        self.speed = speed#speed
        self.direction = (direction + random.gauss(0,.02)) % (2*math.pi)
        self.lifespan = 20
        self.xvel = ix
        self.yvel = iy
        self.x = x
        self.y = y
        self.lx = x #stores last position of x
        self.ly = y #stores last position of y
        self.shieldsMultiplier = 0.6 #decreased damage to shields
        self.armorMultiplier = 1.5 #increased damage to armor
        self.hpMultiplier = 1 #normal hull damage
        
        if isfriendly == True:
            self.color = THECOLORS["yellow"]
        else:
            self.color = THECOLORS["red"]

    def loop(self):
        self.line = Line(self.lx,self.ly,self.x,self.y)
        self.move()
        self.checkForDestroy()

    def checkForDestroy(self):
        self.lifespan -= 1
        if self.friendly == True:
            shipList = copy.copy(EnemyShip.enemyShipList)
            structureList = copy.copy(Structure.enemyStructureList)
        else:
            shipList = copy.copy(FriendlyShip.friendlyShipList)
            structureList = copy.copy(Structure.friendlyStructureList)
        for ship in shipList:
            if self.line.getIntersection(ship.rect): ##############################################################
                if ship.shields > 0: #if shields up
                    ship.shields -= self.att*self.shieldsMultiplier
                elif ship.armor > 0: #if armor up
                    ship.armor -= self.att*self.armorMultiplier
                else: #else attack hull
                    ship.hp -= self.att*self.hpMultiplier
                ship.shieldsTimer = ship.shieldResetTime #resets regen rate
                self.onDestroy()
                break
        for structure in structureList:
            if self.line.getIntersection(structure.rect): ##############################################################
                if structure.shields > 0: #if shields up
                    structure.shields -= self.att*self.shieldsMultiplier
                elif structure.armor > 0: #if armor up
                    structure.armor -= self.att*self.armorMultiplier
                else: #else attack hull
                    structure.hp -= self.att*self.hpMultiplier
                structure.shieldsTimer = structure.shieldResetTime #resets regen rate
                self.onDestroy()
                break 
        if self.lifespan == 0:
            self.onDestroy()

    def move(self):
        self.lx = self.x
        self.ly = self.y
        self.x += (math.cos(self.direction))*self.speed + self.xvel
        self.y -= (math.sin(self.direction))*self.speed + self.yvel


    def onDestroy(self):
        try:
            Bullet.bulletList.remove(self)
        except:
            pass

class Missile(Bullet):

    def __init__(self,x,y,isfriendly,att,speed,direction,ix,iy,target,initialDir=0):
        super(Missile,self).__init__(x,y,isfriendly,att,speed,direction,ix,iy)
        if initialDir == 0:
            self.initialDir = random.choice([-1,1])
        else:
            self.initialDir = initialDir
        self.sprite = Sprites.sprMissile # this denotes a line drawing
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.lifespan = 100
        self.xvel = ix + 0.5*speed*math.cos(self.direction+self.initialDir*(math.pi/4))
        self.yvel = iy + 0.5*speed*math.sin(self.direction+self.initialDir*(math.pi/4))
        self.acceleration = 0.3
        self.shieldsMultiplier = 1 #normal shield damage
        self.armorMultiplier = .6 #diminished damage to armor
        self.hpMultiplier = 2.5 #critical hull damage
        self.turnSpeed = 0.6
        self.speed = 1
        self.maxSpeed = 6
        self.desiredDir = 0
        self.targetDir = 0
        self.turnDirection = 1
        self.theta = 0
        self.attackTarget = target
        target.references.add(self)

    def findDirFromPos(self,x,y):
        dx = x-self.x
        dy = self.y - y
        r = self.distance(x,y)
        if r != 0 and abs(dx/r) <= 1:
            #arccos always returns positive angle
            if dy >= 0: #if in the positive spectrum
                return math.acos((dx/r)) #just return arccos
            else:
                return 2*math.pi - math.acos((dx/r)) #else return arcos from 2pi

    def distance(self,x,y):
        return (((x-self.x)**2)+((y-self.y)**2))**0.5

    def loop(self):
        self.line = Line(self.lx,self.ly,self.x,self.y)
        self.move()
        self.checkForDestroy()            

    def move(self):
        self.speed += 0.2
        if self.attackTarget != None:
            self.direction = self.findDirFromPos(self.attackTarget.x,self.attackTarget.y)
        self.lx = self.x
        self.ly = self.y
        self.x += math.cos(self.direction)*self.speed+self.xvel
        self.y -= math.sin(self.direction)*self.speed+self.yvel


    def onDestroy(self):
        try:
            Bullet.bulletList.remove(self)
        except:
            pass

class Laser(Bullet):
    def __init__(self,x,y,isfriendly,att,speed,direction,tx,ty):
        super(Laser,self).__init__(x,y,isfriendly,att,speed,direction,0,0)
        self.lx = self.x
        self.ly = self.y
        self.targetX,self.targetY = tx + random.gauss(0,5),ty+ random.gauss(0,5)
        self.sprite = None
        self.lifespan = 2
        self.shieldsMultiplier = 2.5 #critical damage to shields
        self.armorMultiplier =1 #normal damage to armor
        self.hpMultiplier = 0.6 #diminished hull damage
        if isfriendly == True:
            self.color = THECOLORS["cyan"]
        else:
            self.color = THECOLORS["violet"]

    def move(self):

        self.x = self.targetX
        self.y = self.targetY


class Ship(object):

    shipList = []

    @classmethod
    def getShipList(cls):
        return Ship.shipList

    def __init__(self,x,y):

        self.hidden = True
        self.cost = 0
        self.name = "Ship"
        self.type = "Ship"
        #self.sprite = Sprites.sprShip
        self.spriteBack = Sprites.sprShipBack
        self.spriteFront = Sprites.sprShipFront
        self.spriteLeft = Sprites.sprShipLeft
        self.spriteRight = Sprites.sprShipRight
        self.spriteWidth = 0#self.sprite.get_width()
        self.spriteHeight = 0#self.sprite.get_height()
        self.spriteRadius = 0#self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.x = x
        self.y = y
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 50
        self.maxShields = 50
        self.armor = 50
        self.maxArmor = 50
        self.maxhp = 100
        self.hp = 100
        self.att = 10
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = x
        self.targetY = y
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.2 #acceleration
        self.maxFrThrust = 0.1 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.backThrust = False
        self.rightThrust = False
        self.leftThrust = False
        self.frontThrust = False
        self.selected = False
        self.action = "resting"
        self.attackTarget = None
        self.attackRange = 100
        self.reload = 0
        self.bulletSpeed = 20
        self.reloadTicks = 20
        self.references = set()
        self.targetRange = 500
        self.possibleTargets = []
        self.friendly = True
        self.strafeDirection = "left"
        self.shieldsTimer = 0
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1
        self.hpRegen = 0.01
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)
        self.inactive = True
        self.buildTime = 0
        self.buildTimeEnd = 500

    def rebuild(self):
        self.buildTime += 1
        if self.buildTime >= self.buildTimeEnd:
            self.buildTime = 0
            self.inactive = False
        
    def regenShields(self):
        if self.shields < self.maxShields:
            if self.shieldsTimer == 0:
                self.shields += self.shieldsRegen
            else:
                self.shieldsTimer -= 1
        if self.shields > self.maxShields:
            self.shields = self.maxShields #resets if it overshoots

    def regenHull(self):
        if self.hp < self.maxhp:
            self.hp += self.hpRegen #constant hp regen
    
    def distance(self,x,y):
        return (((x-self.x)**2)+((y-self.y)**2))**0.5


    def magnitude(self,x,y):
        return ((x**2)+(y**2))**0.5

    def stoppingDistance(self):
        if self.maxFrThrust != 0:
            v = self.magnitude(self.xvel, self.yvel)
            a = self.maxFrThrust*0.5
            return ((v**2)/(2*a))
        else:
            return 0

    def findNearbyTargets(self):
        output = []
        if self.friendly == True:
            shipList = EnemyShip.enemyShipList
            structureList = Structure.enemyStructureList
        else:
            shipList = FriendlyShip.friendlyShipList
            structureList = Structure.friendlyStructureList
        for ship in shipList:
            if self.distance(ship.x,ship.y) <= self.targetRange:
                output.append(ship)
        if output == []:
            for structure in structureList:
                if self.distance(structure.x,structure.y) <= self.targetRange:
                    output.append(structure)
        self.possibleTargets = output        

    def targetNearbyTargets(self):
        if self.attackTarget == None and self.possibleTargets != []:
            self.attack(self.possibleTargets[random.randint(0,len(self.possibleTargets)-1)])
            self.possibleTargets = []

    def loop(self):
        self.rect = self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        if self.inactive == True:
            self.rebuild()
        else:
            self.findNearbyTargets()
            self.targetNearbyTargets()
            self.regenShields()
            self.regenHull()
            if self.armor < 0:
                self.armor = 0
            if (self.xvel != 0 and self.yvel != 0) or (self.x != self.targetX and self.y != self.targetY):
                self.moveToPosition(self.targetX,self.targetY)
        if self.hp <= 0:
            self.onDestroy()

    def findFormationPosition(self,x,y,a,i):
        fleetSize = len(a)
        theta = 2*i*math.pi/fleetSize#finds position on the circle
        circumference = 30 * fleetSize
        radius = circumference/(2*math.pi)
        self.targetX = x + radius*math.cos(theta)
        self.targetY = y - radius*math.sin(theta)
    
    def attack(self,target):
        self.action = "attacking"
        self.attackTarget = target
        target.references.add(self) #adds our ship to the list of references used for garbage collection
        self.targetX = target.x
        self.targetY = target.y
        self.moveToPosition(self.targetX,self.targetY)

    def fireBullet(self):
        Bullet.bulletList.append(Bullet(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))

    def evasiveAction(self,tx,ty,r):
        #r = desired radius
        if random.random < 0.1:
            self.strafeDirection = random.choice(["left","right"])
        if self.distance(tx,ty) < r:
            self.rotateToTargetDir() #point at target
            if self.reload == 0:
                self.fireBullet()
                self.reload = self.reloadTicks
            if self.distance(tx,ty) > (r/3):
                self.frontThrust = False #back off a little
                self.backThrust = False
                if self.strafeDirection == "left":
                    self.leftThrust = True
                    self.rightThrust = False
                else:
                    self.rightThrust = True
                    self.leftThrust = False
            else:
                self.frontThrust = True #back off a little
                self.backThrust = False
                if self.strafeDirection == "left":
                    self.leftThrust = True
                    self.rightThrust = False
                else:
                    self.rightThrust = True
                    self.leftThrust = False
        else:
            self.turnToDirection(tx,ty) #move to target
            self.frontThrust = False
            self.backThrust = True
            self.leftThrust = False
            self.rightThrust = False

    def nonEvasiveAction(self,tx,ty,target,r):
        self.leftThrust = False
        self.rightThrust = False
        if self.distance(target.x,target.y) > target.spriteRadius:
            self.turnToDirection(target.x,target.y) #move to target
            self.frontThrust = False
            self.backThrust = True
            self.leftThrust = False
            self.rightThrust = False
        else:
            self.rotateToTargetDir()
            if self.reload == 0:
                self.fireBullet()
                self.reload = self.reloadTicks
            if self.xvel != 0 and self.yvel != 0:
                self.turnToDirection(tx,ty)
                self.frontThrust = True
                self.backThrust = False
                self.leftThrust = False
                self.rightThrust = False
    
    def moveToPosition(self,tx,ty):
        if self.reload > 0:
            self.reload -= 1
        self.targetDir = self.findDirFromPos(tx,ty)
        if self.action == "moving" or self.action == "resting":
            self.turnToDirection(tx,ty)
            self.findThrust(tx,ty)
        elif self.action == "attacking":
            if self.attackTarget == None:
                self.action = "moving"
            elif self.attackTarget.type == "Structure":
                self.targetX = self.attackTarget.x
                self.targetY = self.attackTarget.y
                self.nonEvasiveAction(tx,ty,self.attackTarget,self.attackRange)
            else:
                self.targetX = self.attackTarget.x
                self.targetY = self.attackTarget.y
                self.evasiveAction(tx,ty,self.attackRange)
        else:
            pass
        
        ################################################
        frontDir = self.direction
        leftDir = (self.direction+math.pi/2)%(2*math.pi)
        rightDir = (self.direction-math.pi/2)%(2*math.pi)
        backDir = (self.direction+math.pi)%(2*math.pi)
        ################################################
        prevxvel = self.xvel
        prevyvel = self.yvel
        if self.backThrust == True:
            self.xvel += self.maxBkThrust*math.cos(frontDir)
            self.yvel += self.maxBkThrust*math.sin(frontDir)
        if self.frontThrust == True:
            self.xvel += self.maxFrThrust*math.cos(backDir)
            self.yvel += self.maxFrThrust*math.sin(backDir)
        if self.leftThrust == True:
            self.xvel += self.maxSdThrust*math.cos(rightDir)
            self.yvel += self.maxSdThrust*math.sin(rightDir)
        if self.rightThrust == True:
            self.xvel += self.maxSdThrust*math.cos(leftDir)
            self.yvel += self.maxSdThrust*math.sin(leftDir)

        if self.magnitude(self.xvel,self.yvel) > self.maxSpeed:
            self.xvel = prevxvel
            self.yvel = prevyvel

        self.x += self.xvel
        self.y -= self.yvel
        
    def findDirFromPos(self,x,y):
        dx = x-self.x
        dy = self.y - y
        r = self.distance(x,y)
        if r != 0 and abs(dx/r) <= 1:
            #arccos always returns positive angle
            if dy >= 0: #if in the positive spectrum
                return math.acos((dx/r)) #just return arccos
            else:
                return 2*math.pi - math.acos((dx/r)) #else return arcos from 2pi       

    def findThrust(self,tx,ty):
        if self.distance(tx,ty) < self.stoppingDistance() or self.distance(tx,ty) < 30:
            backDir = (self.direction+math.pi)%(2*math.pi)
            self.leftThrust = False
            self.rightThrust = False
            if self.magnitude(self.xvel + self.maxFrThrust*math.cos(backDir),self.yvel + self.maxFrThrust*math.sin(backDir)) < self.magnitude(self.xvel,self.yvel):
                self.frontThrust = True
                self.backThrust = False
            else:
                self.frontThrust = False
                self.backThrust = False
            if self.magnitude(self.xvel,self.yvel) < 2:
                self.backThrust = False
                self.frontThrust = False
                self.xvel /=1.1
                self.yvel /=1.1
                self.action = "resting"
        else:
            self.frontThrust = False
            self.backThrust = True

    def rotateToDir(self):
        if self.desiredDir > self.direction:
            cc = self.desiredDir - self.direction
            cl = 2*math.pi-self.desiredDir + self.direction
        else:
            cc = 2*math.pi-self.direction + self.desiredDir
            cl = self.direction - self.desiredDir
        if cc < cl:
            self.turnDirection = 1 # 1 is counterclockwise
            self.theta = cc
        else:
            self.turnDirection = -1
            self.theta = cl
        self.direction += self.turnDirection*self.turnSpeed*((self.theta)/(math.pi))
        self.direction = self.direction % (2*math.pi)

    def rotateToTargetDir(self): #rotates so the ship is in correct orientation
        if self.targetDir > self.direction:
            cc = self.targetDir - self.direction
            cl = 2*math.pi-self.targetDir + self.direction
        else:
            cc = 2*math.pi-self.direction + self.targetDir
            cl = self.direction - self.targetDir
        if cc < cl:
            self.turnDirection = 1 # 1 is counterclockwise
            self.theta = cc
        else:
            self.turnDirection = -1
            self.theta = cl
        self.direction += self.turnDirection*self.turnSpeed*((self.theta)/(math.pi))
        self.direction = self.direction % (2*math.pi)    

    def turnToDirection(self,tx,ty):
        vt = Vector(tx-self.x,self.y-ty) #direction of target
        vi = Vector(self.xvel,self.yvel) #direction of inertia
        self.velDir = vi.angle()
        vd = (vt.unit()).sub(vi.unit()) #desired direction vector
        if vd.length > 0 and abs(vd.x/vd.length)<=1:
            if vd.y >= 0:
                self.desiredDir = math.acos(vd.x/vd.length)
            else:
                self.desiredDir = 2*math.pi - math.acos(vd.x/vd.length)
        else:
            self.desiredDir = 0
        if vd.length > 0.1:
            self.rotateToDir()
        else:
            self.rotateToTargetDir() #smoother turning

    def onDestroy(self):
        for ref in self.references:
            ref.attackTarget = None
        Ship.shipList.remove(self)


class FriendlyShip(Ship):

    friendlyShipList = set()
    selectedFriendlyShips = set()
    friendlyShipNumber = 0
    
    def __init__(self,x,y):
        super(FriendlyShip,self).__init__(x,y) #all the atributes of ship
        self.cost = 10
        FriendlyShip.friendlyShipList.add(self)
        FriendlyShip.friendlyShipNumber += 1
        self.friendly = True #except, its now considered unfriendly
        self.UIColor = THECOLORS["yellow"] #health
        self.UIColor2 = THECOLORS["pink"] #armor
        self.UIColor3 = THECOLORS["cyan"] #shields
        self.sprite = Sprites.sprShip
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [x,x+self.spriteWidth,y,y+self.spriteHeight]
        
        
    def onDestroy(self):
        super(FriendlyShip,self).onDestroy()
        #Ship.shipList.remove(self)
        FriendlyShip.friendlyShipList.remove(self)
        FriendlyShip.friendlyShipNumber -= 1
        if self.selected == True:
            FriendlyShip.selectedFriendlyShips.remove(self)

    def moveToPosition(self,tx,ty):
        if self.reload > 0:
            self.reload -= 1
        self.targetDir = self.findDirFromPos(tx,ty)
        if self.action == "moving" or self.action == "resting":
            self.turnToDirection(tx,ty)
            self.findThrust(tx,ty)
        elif self.action == "attacking":
            if self.attackTarget == None:
                self.action = "moving"
            elif self.attackTarget.type == "Structure":
                self.targetX = self.attackTarget.x
                self.targetY = self.attackTarget.y
                self.nonEvasiveAction(tx,ty,self.attackTarget,self.attackRange)
            else:
                self.targetX = self.attackTarget.x
                self.targetY = self.attackTarget.y
                self.evasiveAction(tx,ty,self.attackRange)
        else:
            pass
        
        ################################################
        frontDir = self.direction
        leftDir = (self.direction+math.pi/2)%(2*math.pi)
        rightDir = (self.direction-math.pi/2)%(2*math.pi)
        backDir = (self.direction+math.pi)%(2*math.pi)
        ################################################
        prevxvel = self.xvel
        prevyvel = self.yvel
        if self.backThrust == True:
            self.xvel += self.maxBkThrust*math.cos(frontDir)
            self.yvel += self.maxBkThrust*math.sin(frontDir)
        if self.frontThrust == True:
            self.xvel += self.maxFrThrust*math.cos(backDir)
            self.yvel += self.maxFrThrust*math.sin(backDir)
        if self.leftThrust == True:
            self.xvel += self.maxSdThrust*math.cos(rightDir)
            self.yvel += self.maxSdThrust*math.sin(rightDir)
        if self.rightThrust == True:
            self.xvel += self.maxSdThrust*math.cos(leftDir)
            self.yvel += self.maxSdThrust*math.sin(leftDir)

        if self.magnitude(self.xvel,self.yvel) > self.maxSpeed:
            self.xvel = prevxvel
            self.yvel = prevyvel

        self.x += self.xvel
        self.y -= self.yvel
        
class EnemyShip(Ship):

    enemyShipList = set()
    selectedEnemyShips = set()
    enemyShipNumber = 0
    
    def __init__(self,x,y):
        super(EnemyShip,self).__init__(x,y) #all the atributes of ship
        self.cost = 10
        self.buildTimeEnd = 0
        self.buildTime = 0
        EnemyShip.enemyShipList.add(self)
        EnemyShip.enemyShipNumber += 1
        self.friendly = False #except, its now considered unfriendly
        self.sprite = Sprites.sprEnemyShip
        self.UIColor = THECOLORS["red"] #health
        self.UIColor2 = THECOLORS["blue"] #armor
        self.UIColor3 = THECOLORS["violet"] #shields
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [x,x+self.spriteWidth,y,y+self.spriteHeight]        

    def onDestroy(self):
        super(EnemyShip,self).onDestroy()
        #Ship.shipList.remove(self)
        EnemyShip.enemyShipList.remove(self)
        if self.selected == True:
            EnemyShip.selectedEnemyShips.remove(self)
        EnemyShip.enemyShipNumber -= 1

    def targetNearbyTargets(self):
        if self.attackTarget == None:
            if self.possibleTargets != []:
                self.attack(random.choice(self.possibleTargets))
                self.possibleTargets = []
            elif Structure.friendlyStructureList != []:
                self.attack(random.choice(Structure.friendlyStructureList))
                
        
    def moveToPosition(self,tx,ty):
        if self.reload > 0:
            self.reload -= 1
        self.targetDir = self.findDirFromPos(tx,ty)
        if self.action == "moving" or self.action == "resting":
            self.leftThrust = False
            self.rightThrust = False
            self.turnToDirection(tx,ty)
            self.findThrust(tx,ty)
        elif self.action == "attacking":
            self.targetNearbyTargets()
            if self.attackTarget == None:
                self.action = "moving"
            elif self.attackTarget.type == "Structure":
                self.nonEvasiveAction(tx,ty,self.attackTarget,self.attackRange)
            else:
                self.targetX = self.attackTarget.x
                self.targetY = self.attackTarget.y
                self.evasiveAction(tx,ty,self.attackRange)
            
        else:
            pass
        
        ################################################
        frontDir = self.direction
        leftDir = (self.direction+math.pi/2)%(2*math.pi)
        rightDir = (self.direction-math.pi/2)%(2*math.pi)
        backDir = (self.direction+math.pi)%(2*math.pi)
        ################################################
        prevxvel = self.xvel
        prevyvel = self.yvel
        if self.backThrust == True:
            self.xvel += self.maxBkThrust*math.cos(frontDir)
            self.yvel += self.maxBkThrust*math.sin(frontDir)
        if self.frontThrust == True:
            self.xvel += self.maxFrThrust*math.cos(backDir)
            self.yvel += self.maxFrThrust*math.sin(backDir)
        if self.leftThrust == True:
            self.xvel += self.maxSdThrust*math.cos(rightDir)
            self.yvel += self.maxSdThrust*math.sin(rightDir)
        if self.rightThrust == True:
            self.xvel += self.maxSdThrust*math.cos(leftDir)
            self.yvel += self.maxSdThrust*math.sin(leftDir)

        if self.magnitude(self.xvel,self.yvel) > self.maxSpeed:
            self.xvel = prevxvel
            self.yvel = prevyvel
        
        self.x += self.xvel
        self.y -= self.yvel

################################################################################
########                                                                ########
########                       SHIP VARIANTS                            ########
########                                                                ########
################################################################################

class FriendlyHammerhead(FriendlyShip):
    cost = 2000
    def __init__(self,x,y,targetX,targetY):
        super(FriendlyHammerhead,self).__init__(x,y)
        self.name = "Hammerhead"
        self.cost = 2000
        self.sprite = Sprites.sprShipHammerhead
        self.spriteBack = Sprites.sprShipHammerheadBack
        self.spriteFront = Sprites.sprShipHammerheadFront
        self.spriteLeft = Sprites.sprShipHammerheadLeft
        self.spriteRight = Sprites.sprShipHammerheadRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 1500
        self.maxShields = 1500
        self.armor = 2000
        self.maxArmor = 2000
        self.maxhp = 1000
        self.hp = 1000
        self.att = 1
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.5 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 5
        self.speed = 0
        self.attackRange = 200
        self.bulletSpeed = 200
        self.reloadTicks = 1
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x+5,self.y-5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x+5,self.y+5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x-5,self.y+5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x-5,self.y-5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))


class EnemyHammerhead(EnemyShip):
    cost = 2000
    name = "Hammerhead"
    def __init__(self,x,y,targetX,targetY):
        super(EnemyHammerhead,self).__init__(x,y)
        self.name = "Hammerhead"
        self.cost = 2000
        self.sprite = Sprites.sprShipHammerheadEnemy
        self.spriteBack = Sprites.sprShipHammerheadBack
        self.spriteFront = Sprites.sprShipHammerheadFront
        self.spriteLeft = Sprites.sprShipHammerheadLeft
        self.spriteRight = Sprites.sprShipHammerheadRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 1500
        self.maxShields = 1500
        self.armor = 2000
        self.maxArmor = 2000
        self.maxhp = 1000
        self.hp = 1000
        self.att = 1
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.5 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 5
        self.speed = 0
        self.attackRange = 200
        self.bulletSpeed = 200
        self.reloadTicks = 1
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x+5,self.y-5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x+5,self.y+5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x-5,self.y+5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x-5,self.y-5,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))

class FriendlyCarrier(FriendlyShip):
    cost = 1500
    def __init__(self,x,y,targetX,targetY):
        super(FriendlyCarrier,self).__init__(x,y)
        self.name = "Carrier"
        self.cost = 1500
        self.sprite = Sprites.sprShipCarrier
        self.spriteBack = Sprites.sprShipCarrierBack
        self.spriteFront = Sprites.sprShipCarrierFront
        self.spriteLeft = Sprites.sprShipCarrierLeft
        self.spriteRight = Sprites.sprShipCarrierRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 1500
        self.maxShields = 1500
        self.armor = 2000
        self.maxArmor = 2000
        self.maxhp = 1000
        self.hp = 1000
        self.att = 40
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.25 #acceleration
        self.maxFrThrust = 0.2 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 4
        self.reloadTicks = 40
        self.targetRange = 700
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel+1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel-1,self.attackTarget,-1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel+1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel-1,self.attackTarget,-1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel-1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel+1,self.attackTarget,-1))

class EnemyCarrier(EnemyShip):
    cost = 1500
    name = "Carrier"
    def __init__(self,x,y,targetX,targetY):
        super(EnemyCarrier,self).__init__(x,y)
        self.name = "Carrier"
        self.cost = 1500
        self.sprite = Sprites.sprShipCarrierEnemy
        self.spriteBack = Sprites.sprShipCarrierBack
        self.spriteFront = Sprites.sprShipCarrierFront
        self.spriteLeft = Sprites.sprShipCarrierLeft
        self.spriteRight = Sprites.sprShipCarrierRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 1500
        self.maxShields = 1500
        self.armor = 2000
        self.maxArmor = 2000
        self.maxhp = 1000
        self.hp = 1000
        self.att = 40
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.25 #acceleration
        self.maxFrThrust = 0.2 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 4
        self.reloadTicks = 40
        self.targetRange = 700
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel+1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel-1,self.attackTarget,-1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel+1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel-1,self.attackTarget,-1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel+1,self.yvel-1,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel-1,self.yvel+1,self.attackTarget,-1))

class FriendlyBruiser(FriendlyShip):
    cost = 150
    def __init__(self,x,y,targetX,targetY):
        super(FriendlyBruiser,self).__init__(x,y)
        self.name = "Bruiser"
        self.cost = 150
        self.sprite = Sprites.sprShipBruiser
        self.spriteBack = Sprites.sprShipBruiserBack
        self.spriteFront = Sprites.sprShipBruiserFront
        self.spriteLeft = Sprites.sprShipBruiserLeft
        self.spriteRight = Sprites.sprShipBruiserRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 300
        self.maxShields = 300
        self.armor = 200
        self.maxArmor = 200
        self.maxhp = 500
        self.hp = 500
        self.att = 0.5
        self.turnSpeed = 0.34
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.15 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 90
        self.reloadTicks = 2
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.1,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.05,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction-0.05,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction-0.1,self.targetX,self.targetY))

class EnemyBruiser(EnemyShip):
    cost = 150
    name = "Bruiser"
    
    def __init__(self,x,y,targetX,targetY):
        super(EnemyBruiser,self).__init__(x,y)
        self.name = "Bruiser"
        self.cost = 150
        self.sprite = Sprites.sprShipBruiserEnemy
        self.spriteBack = Sprites.sprShipBruiserBack
        self.spriteFront = Sprites.sprShipBruiserFront
        self.spriteLeft = Sprites.sprShipBruiserLeft
        self.spriteRight = Sprites.sprShipBruiserRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 300
        self.maxShields = 300
        self.armor = 200
        self.maxArmor = 200
        self.maxhp = 500
        self.hp = 500
        self.att = 15
        self.turnSpeed = 0.34
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.15 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 20
        self.missileSpeed = 4
        self.reloadTicks = 20
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.1,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.05,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction-0.05,self.targetX,self.targetY))
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction-0.1,self.targetX,self.targetY))

class FriendlyKnife(FriendlyShip):
    cost = 100
    def __init__(self,x,y,targetX,targetY):
        super(FriendlyKnife,self).__init__(x,y)
        self.name = "Knife"
        self.cost = 100
        self.sprite = Sprites.sprShipKnife
        self.spriteBack = Sprites.sprShipKnifeBack
        self.spriteFront = Sprites.sprShipKnifeFront
        self.spriteLeft = Sprites.sprShipKnifeLeft
        self.spriteRight = Sprites.sprShipKnifeRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 500
        self.maxShields = 500
        self.armor = 400
        self.maxArmor = 400
        self.maxhp = 200
        self.hp = 200
        self.att = 4
        self.turnSpeed = 0.5
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.3 #acceleration
        self.maxFrThrust = 0.3 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 20
        self.reloadTicks = 2
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Bullet(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.1,self.xvel,self.yvel))

class EnemyKnife(EnemyShip):
    cost = 100
    name = "Knife"
    def __init__(self,x,y,targetX,targetY):
        super(EnemyKnife,self).__init__(x,y)
        self.name = "Knife"
        self.cost = 100
        self.sprite = Sprites.sprShipKnifeEnemy
        self.spriteBack = Sprites.sprShipKnifeBack
        self.spriteFront = Sprites.sprShipKnifeFront
        self.spriteLeft = Sprites.sprShipKnifeLeft
        self.spriteRight = Sprites.sprShipKnifeRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 500
        self.maxShields = 500
        self.armor = 400
        self.maxArmor = 400
        self.maxhp = 200
        self.hp = 200
        self.att = 4
        self.turnSpeed = 0.5
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.3 #acceleration
        self.maxFrThrust = 0.3 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 4
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 20
        self.reloadTicks = 2
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Bullet(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction+0.1,self.xvel,self.yvel))

class FriendlySaucer(FriendlyShip):
    cost = 150
    def __init__(self,x,y,targetX=None,targetY=None):
        super(FriendlySaucer,self).__init__(x,y)
        self.name = "Saucer"
        self.cost = 150
        self.sprite = Sprites.sprShipSaucer
        self.spriteBack = Sprites.sprShipSaucerBack
        self.spriteFront = Sprites.sprShipSaucerFront
        self.spriteLeft = Sprites.sprShipSaucerLeft
        self.spriteRight = Sprites.sprShipSaucerRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 30
        self.maxShields = 30
        self.armor = 70
        self.maxArmor = 70
        self.maxhp = 100
        self.hp = 100
        self.att = 30
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 400
        self.bulletSpeed = 5
        self.reloadTicks = 50
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget,-1))

class EnemySaucer(EnemyShip):
    cost = 150
    name = "Saucer"
    def __init__(self,x,y,targetX=None,targetY=None):
        super(EnemySaucer,self).__init__(x,y)
        self.name = "Saucer"
        self.cost = 150
        self.sprite = Sprites.sprShipSaucerEnemy
        self.spriteBack = Sprites.sprShipSaucerBack
        self.spriteFront = Sprites.sprShipSaucerFront
        self.spriteLeft = Sprites.sprShipSaucerLeft
        self.spriteRight = Sprites.sprShipSaucerRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 30
        self.maxShields = 30
        self.armor = 70
        self.maxArmor = 70
        self.maxhp = 100
        self.hp = 100
        self.att = 30
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 400
        self.bulletSpeed = 5
        self.reloadTicks = 50
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget,1))
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget,-1))

class FriendlyHornet(FriendlyShip):
    cost = 1500
    def __init__(self,x,y,targetX=None,targetY=None):
        super(FriendlyHornet,self).__init__(x,y)
        self.name = "Hornet"
        self.cost = 1500
        self.sprite = Sprites.sprShipHornet
        self.spriteBack = Sprites.sprShipHornetBack
        self.spriteFront = Sprites.sprShipHornetFront
        self.spriteLeft = Sprites.sprShipHornetLeft
        self.spriteRight = Sprites.sprShipHornetRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 500
        self.maxShields = 500
        self.armor = 200
        self.maxArmor = 200
        self.maxhp = 300
        self.hp = 300
        self.att = 12
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 50
        self.reloadTicks = 6
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Bullet(self.x,self.y+1,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+5,self.y+5,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+1,self.y-1,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+2,self.y-5,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))


class EnemyHornet(EnemyShip):
    cost = 1500
    name = "Hornet"
    def __init__(self,x,y,targetX=None,targetY=None):
        super(EnemyHornet,self).__init__(x,y)
        self.name = "Hornet"
        self.cost = 1500
        self.sprite = Sprites.sprShipHornetEnemy
        self.spriteBack = Sprites.sprShipHornetBack
        self.spriteFront = Sprites.sprShipHornetFront
        self.spriteLeft = Sprites.sprShipHornetLeft
        self.spriteRight = Sprites.sprShipHornetRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 500
        self.maxShields = 500
        self.armor = 200
        self.maxArmor = 200
        self.maxhp = 300
        self.hp = 300
        self.att = 5
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 50
        self.reloadTicks = 5
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 2
        self.hpRegen = 0.02
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        cd1 = 30*math.cos(self.direction+0.1)
        cd2 = 30*math.cos(self.direction+0.2)
        cd3 = 30*math.cos(self.direction+0.25)
        cd4 = 30*math.cos(self.direction-0.1)
        cd5 = 30*math.cos(self.direction-0.2)
        cd6 = 30*math.cos(self.direction-0.25)
        sd1 = 30*math.cos(self.direction+0.1)
        sd2 = 30*math.sin(self.direction+0.2)
        sd3 = 30*math.sin(self.direction+0.25)
        sd4 = 30*math.sin(self.direction-0.1)
        sd5 = 30*math.sin(self.direction-0.2)
        sd6 = 30*math.sin(self.direction-0.25)
        Bullet.bulletList.append(Bullet(self.x+cd1,self.y-sd1,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+cd2,self.y-sd2,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+cd3,self.y-sd3,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+cd4,self.y-sd4,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+cd5,self.y-sd5,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))
        Bullet.bulletList.append(Bullet(self.x+cd6,self.y-sd6,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel))

class FriendlyBasic(FriendlyShip):
    cost = 10
    def __init__(self,x,y,targetX=None,targetY=None):
        super(FriendlyBasic,self).__init__(x,y)
        self.name = "Basic"
        self.cost = 10
        self.sprite = Sprites.sprShip
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 20
        self.maxShields = 20
        self.armor = 50
        self.maxArmor = 50
        self.maxhp = 100
        self.hp = 100
        self.att = 7
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.15 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 20
        self.reloadTicks = 20
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

class EnemyBasic(EnemyShip):
    cost = 10
    name = "Basic"
    def __init__(self,x,y,targetX,targetY):
        super(EnemyBasic,self).__init__(x,y)
        self.name = "Basic"
        self.cost = 10
        self.sprite = Sprites.sprEnemyShip
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 20
        self.maxShields = 20
        self.armor = 50
        self.maxArmor = 50
        self.maxhp = 100
        self.hp = 100
        self.att = 7
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.15 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 3
        self.speed = 0
        self.attackRange = 100
        self.bulletSpeed = 20
        self.reloadTicks = 20
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

class FriendlyBomber(FriendlyShip):
    cost = 15
    def __init__(self,x,y,targetX=None,targetY=None):
        super(FriendlyBomber,self).__init__(x,y)
        self.name = "Bomber"
        self.cost = 15
        self.sprite = Sprites.sprShipBomber
        self.spriteBack = Sprites.sprShipBomberBack
        self.spriteFront = Sprites.sprShipBomberFront
        self.spriteLeft = Sprites.sprShipBomberLeft
        self.spriteRight = Sprites.sprShipBomberRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 30
        self.maxShields = 30
        self.armor = 70
        self.maxArmor = 70
        self.maxhp = 100
        self.hp = 100
        self.att = 21
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.3 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 2
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 4
        self.reloadTicks = 50
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget))

class EnemyBomber(EnemyShip):
    cost = 15
    name = "Bomber"
    def __init__(self,x,y,targetX=None,targetY=None):
        super(EnemyBomber,self).__init__(x,y)
        self.name = "Bomber"
        self.cost = 15
        self.sprite = Sprites.sprShipBomberEnemy
        self.spriteBack = Sprites.sprShipBomberBack
        self.spriteFront = Sprites.sprShipBomberFront
        self.spriteLeft = Sprites.sprShipBomberLeft
        self.spriteRight = Sprites.sprShipBomberRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 30
        self.maxShields = 30
        self.armor = 70
        self.maxArmor = 70
        self.maxhp = 100
        self.hp = 100
        self.att = 21
        self.turnSpeed = 0.3
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.3 #acceleration
        self.maxFrThrust = 0.15 #deceleration
        self.maxSdThrust = 0.1 #stablizing acceleration
        self.maxSpeed = 2
        self.speed = 0
        self.attackRange = 300
        self.bulletSpeed = 4
        self.reloadTicks = 50
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Missile(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.xvel,self.yvel,self.attackTarget))

class FriendlyLaser(FriendlyShip):
    cost = 15
    def __init__(self,x,y,targetX=None,targetY=None):
        super(FriendlyLaser,self).__init__(x,y)
        self.name = "Lasers"
        self.cost = 15
        self.sprite = Sprites.sprShipLaser
        self.spriteBack = Sprites.sprShipLaserBack
        self.spriteFront = Sprites.sprShipLaserFront
        self.spriteLeft = Sprites.sprShipLaserLeft
        self.spriteRight = Sprites.sprShipLaserRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 50
        self.maxShields = 50
        self.armor = 50
        self.maxArmor = 50
        self.maxhp = 100
        self.hp = 100
        self.att = 0.5
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.4 #deceleration
        self.maxSdThrust = 0.2 #stablizing acceleration
        self.maxSpeed = 6
        self.speed = 0
        self.attackRange = 80
        self.bulletSpeed = 90
        self.reloadTicks = 1
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))


class EnemyLaser(EnemyShip):
    cost = 15
    name = "Laser"
    def __init__(self,x,y,targetX=None,targetY=None):
        super(EnemyLaser,self).__init__(x,y)
        self.name = "Lasers"
        self.cost = 15
        self.sprite = Sprites.sprShipLaserEnemy
        self.spriteBack = Sprites.sprShipLaserBack
        self.spriteFront = Sprites.sprShipLaserFront
        self.spriteLeft = Sprites.sprShipLaserLeft
        self.spriteRight = Sprites.sprShipLaserRight
        self.spriteWidth = self.sprite.get_width()
        self.spriteHeight = self.sprite.get_height()
        self.spriteRadius = self.magnitude(self.spriteWidth/2,self.spriteHeight/2)+10 #iffy room
        self.rect = [self.x,self.x+self.spriteWidth,self.y,self.y+self.spriteHeight]
        self.shields = 50
        self.maxShields = 50
        self.armor = 50
        self.maxArmor = 50
        self.maxhp = 100
        self.hp = 100
        self.att = 0.5
        self.turnSpeed = 0.4
        self.turnDirection = 0
        self.theta = 0
        self.targetX = targetX
        self.targetY = targetY
        self.targetDirection = 0
        self.direction = 0 #direction spaceship is facing
        self.desiredDir = 0 #desired dir to counteract inertia
        self.velDir = 0 #direction of the momentum
        self.xvel = 0
        self.yvel = 0
        self.xaccel = 0
        self.yaccel = 0
        self.maxBkThrust = 0.4 #acceleration
        self.maxFrThrust = 0.4 #deceleration
        self.maxSdThrust = 0.2 #stablizing acceleration
        self.maxSpeed = 6
        self.speed = 0
        self.attackRange = 80
        self.bulletSpeed = 90
        self.reloadTicks = 1
        self.targetRange = 500
        self.shieldResetTime = 500 #100ticks before shields regen
        self.shieldsRegen = 1.2
        self.hpRegen = 0.015
        self.attributes = [["Name",self.name],["Attack", self.att]]
        self.attributesNumber = len(self.attributes)

    def fireBullet(self):
        Bullet.bulletList.append(Laser(self.x,self.y,self.friendly,self.att,self.bulletSpeed,self.direction,self.targetX,self.targetY))









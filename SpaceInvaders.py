import pygame, math, random, copy, time, gc
from pygame.locals import *
from pygame.color import THECOLORS

#FRAMESPERSEC = 60
DT = 0.010

def memoized(f):
    import functools
    cachedResults = dict()
    @functools.wraps(f)
    def wrapper(*args):
        if args not in cachedResults:
            cachedResults[args] = f(*args)
        return cachedResults[args]
    return wrapper

################################################################################
class SpaceInvaders(object):
    
    def __init__(self):
        self._mainscreen = True
        self._running = True
        self._tutorial = False
        self._winLoseScreen = False
        self.tutorialPage = 0
        self._display_surf = None
        self.width, self.height = 1000, 500
        self.uiHeight = 200
        self.size = (self.width,(self.height+self.uiHeight))
        self.mapMultiplier = 2 #determines the size of the map (the background
                               #size is 3200x3200

    def on_init(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.Surface = pygame.display.set_mode\
                       (self.size,pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        import Classes
        self.Classes = Classes
        self.loadObjects()
        self.loadTutorialPages()
        self.mapHeight = self.background.spriteHeight*self.mapMultiplier
        self.mapWidth = self.background.spriteWidth*self.mapMultiplier
        self.shiftDown = False
        self.lastTimeCalled = time.time()
        self.multiSelect = False
        self.selectedStructure = None
        self.actionNumber = -1
        self.placingItem = False
        self.selectingRallyPoint = False
        self.targetingAsteroid = False
        self.targetingAdoption = False
        self.smallFont = pygame.font.Font(None, 14) #loads fonts
        self.medFont = pygame.font.Font(None, 18)

    def loadTutorialPages(self):
        self.tutorialPage = 0
        self.tutorialPages = self.Classes.Sprites.tutPages

    def loadAsteroids(self):
        gridList = []
        totalResources = 0
        for col in xrange(64):
            gridList.append([0]*64)
        for row in xrange(0,64): #grid size = 100 pixels
            for col in xrange(0,64):
                if (row < 9 and col < 9):
                    if (row >= 2 and row <=5) and (col >= 3 and col <=5):
                        continue #no asteroids made near the base
                    elif random.random() > 0.8:
                        loc = (100*row+random.randint(0,100),\
                               100*col+random.randint(0,100))
                        asteroid = self.Classes.Asteroid(
                            loc[0],loc[1],700+random.randint(-300,300))
                        self.Classes.Structure.structureList.append(asteroid)
                elif random.random() > 0.97:
                    #if gridList[row]
                    gridList[row][col] = 1
                    loc = (100*row+random.randint(0,100),\
                           100*col+random.randint(0,100))
                    distFromCenter = (abs(row-32)+abs(col-32))/64.0
                    size = (random.uniform(4,5)*(1/(1+distFromCenter)))
                    asteroid = self.Classes.Asteroid(
                        loc[0],loc[1],int(round((10)**size)))
                    totalResources += asteroid.resources
                    self.Classes.Structure.structureList.append(asteroid)
                    #the minimum size = 100 to 500 (10x10)
                    # 500 to 1000 (50x50)
                    # 1000 to 10000 (100x100)
                    # 10000 to 500000 (200x200)
                    #max size = 10000 to 100000 size = 400x400
        self.Classes.Game.gameTextFeedback.insert(0,\
                                                  "Resources Generated: %d"\
                                                  % totalResources)
        self.loadWarpgates(gridList)

    def loadWarpgates(self,gridList): #THIS IS CALLED AFTER ASTEROIDS
        c = self.Classes
        for row in xrange(14,62): #from 14 to 62, we can generate enemies
            for col in xrange(14,62):
                if gridList[row][col] == 0: #makes sure not overlapping asteroids
                    distFromCenter = (abs(row-32)+abs(col-32))/64.0
                    if random.random() > 0.985 + distFromCenter/100.0:
                        #more frequent generation in the middle
                        (x,y) = (100*row+random.randint(0,100),\
                               100*col+random.randint(0,100))
                        level = int(((1-distFromCenter-0.01)**1.7)*3)
                        shipType = [[c.EnemyBasic,c.EnemyBomber,c.EnemyLaser],
                                    [c.EnemyBruiser,c.EnemyKnife,c.EnemySaucer],
                                    [c.EnemyHammerhead,
                                     c.EnemyCarrier,
                                     c.EnemyHornet]]\
                                    [level][random.randint(0,2)]
                        #based on level choose a shiptype
                        hp = [100,1000,5000][level] + \
                             int(abs(random.gauss(0,10**(level+1))/5))
                        armor = [50,500,3000][level] + \
                                int(abs(random.gauss(0,10**(level+1))/5))
                        shields = [50,500,3000][level] + \
                                  int(abs(random.gauss(0,10**(level+1))/5))
                        warpgate = c.Warpgate(x,y,shipType,hp,armor,shields)
                        self.Classes.Structure.structureList.append(warpgate)
        self.Classes.Game.gameTextFeedback.insert(0,
                                                  "Warpgates Generated: %d"\
                                                  % self.Classes.Warpgate.\
                                                  warpgateCount)
        
    def loadObjects(self):
        self.minimap = self.Classes.Minimap(10,10,640)#load minimap
        self.loadAsteroids()
        self.Classes.Structure.structureList.append(\
            self.Classes.Base(400,400,10000,5000,1000,True))
        self.mouse = self.Classes.Mouse(self.width/2,self.height/2)
        self.background = self.Classes.Background()
        self.camera = self.Classes.Camera(\
            self.width,self.height,\
            self.background.spriteHeight*self.mapMultiplier,\
            self.background.spriteWidth*self.mapMultiplier)
        self.minimap.update()

    def isWithinBounds(self,(x,y),(xb1,yb1),(xb2,yb2)):
        if xb1 == xb2 or yb1 == yb2:
            return False #zero area rectangle cant select anything
        if xb1 > xb2: #finds upper and lower x bound
            upperXBound = xb1
            lowerXBound = xb2
        else:
            upperXBound = xb2
            lowerXBound = xb1
        if yb1 > yb2: #finds upper and lower y bound
            upperYBound = yb1
            lowerYBound = yb2
        else:
            upperYBound = yb2
            lowerYBound = yb1
        if x < upperXBound and x > lowerXBound:
            if y < upperYBound and y > lowerYBound:
                return True #if within bounds return true
        return False #otherwise return false

    def withinUIRange(self,(x,y)): #checks if the (x,y) is on top of a uielement
        if self.isWithinBounds((x,y),(0,self.height),\
                               (201,self.height+self.uiHeight)):
            return 0 #left, minimap
        if self.isWithinBounds((x,y),(223,self.height+83),\
                               (639,self.height+self.uiHeight)):
            return 1 #middle bar
        if self.isWithinBounds((x,y),(661,self.height+23),\
                               (self.width,self.height+self.uiHeight)):
            return 2 #right action bar
        else:
            return -1 #no action

    def uiInterfaceWithMousePosition(self,event,index):
        (x,y) = event.pos
        if index == 0: #if its a click in the minimap
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if x>= 19:
                        if x <= 157: #within the boundaries minus width of box
                            #this transfers the click position to an actual dx
                            self.camera.dx = -1*int(round(((x-19)/164.0)*6400))
                        else:
                            self.camera.dx = -5400 #this is the cap dx
                            
                    if y >= self.height+20 and y <= self.height+184:
                        #this transfers click position to an actual dy
                        if y <= self.height+165:
                            self.camera.dy = -1*int(round((\
                            (y-self.height-20)/164.0)*6400))
                        else:
                            self.camera.dy = -5700 #cap dy
                    #dimensions: 19,self.height+20,183,self.height+184
        elif index == 1: #in the middle
            pass #no actions avaliable, may introduce some in future
        else: #in the right bar
            self.actionNumber = -1 #reset the action
            if y > self.height+110: #check pressed in lower half
                if self.isWithinBounds((x,y),(673,self.height+115),\
                                       (746,self.height+188)):
                    self.actionNumber = 4
                elif self.isWithinBounds((x,y),(754,self.height+115),\
                                         (826,self.height+188)):
                    self.actionNumber = 5
                elif self.isWithinBounds((x,y),(836,self.height+115),\
                                         (909,self.height+188)):
                    self.actionNumber = 6
                elif self.isWithinBounds((x,y),(917,self.height+115),\
                                         (990,self.height+188)):
                    self.actionNumber = 7
            else: #it is then in the upper half, check which button was pressed
                if self.isWithinBounds((x,y),(673,self.height+35),\
                                       (746,self.height+108)):
                    self.actionNumber = 0
                elif self.isWithinBounds((x,y),(754,self.height+35),\
                                         (826,self.height+108)):
                    self.actionNumber = 1
                elif self.isWithinBounds((x,y),(836,self.height+35),\
                                         (909,self.height+108)):
                    self.actionNumber = 2
                elif self.isWithinBounds((x,y),(917,self.height+35),\
                                         (990,self.height+108)):
                    self.actionNumber = 3
            if self.selectedStructure != None and self.actionNumber != -1 and \
               self.selectedStructure.isFriendly == True and\
               self.selectedStructure.inactive == False: #if valid structure and
                                                         #valid action
                if self.selectedStructure.actionNumbers > self.actionNumber:
                    #given the action number is a valid button
                    if self.selectedStructure.actionTypes[self.actionNumber]\
                       == "place": #begin placing sequence
                        self.placingItem = True
                    elif self.selectedStructure.actionTypes[self.actionNumber]\
                         == "rally": #begin rally sequence
                        self.selectingRallyPoint = True
                    elif self.selectedStructure.actionTypes[self.actionNumber]\
                         == "target": #being target sequence
                        self.targetingAsteroid = True
                    elif self.selectedStructure.actionTypes[self.actionNumber]\
                         == "adopt":
                        self.targetingAdoption = True
                    else: #if its not a special case, then just do it
                        self.selectedStructure.actions[self.actionNumber]()
                        self.actionNumber = -1 #reset action number
                        self.placingItem = False #reset all the booleans
                        self.targetingAsteroid = False
                        self.selectingRallyPoint = False
                        self.targetingAdoption = False
                else:
                    self.actionNumber = -1 #reset action number if not valid
            else:
                self.actionNumber = -1 #reset the action number when done
                    
        
    
    def on_event(self, event):
        if event.type == pygame.QUIT: #if quit, then quit
            self._running = False
        elif event.type == MOUSEBUTTONDOWN: #on mouse down
            eventXY = (event.pos[0] - self.camera.dx, #xy based on camera
                       event.pos[1] - self.camera.dy)
            if self.withinUIRange(event.pos) != -1: #if it is within the uirange
                self.uiInterfaceWithMousePosition(event,
                                                  self.withinUIRange(event.pos))
            elif self.targetingAsteroid == True: #THIS IS ALL UI RELATED STUFF
                for ast in self.Classes.Asteroid.asteroidList:
                    if ast.hidden == False:
                        if self.isWithinBounds(eventXY, #if clicks on ast
                                               (ast.x-ast.spriteWidth/2,
                                                ast.y-ast.spriteHeight/2),
                                               (ast.x+ast.spriteWidth,
                                                ast.y+ast.spriteHeight)):
                            if ((ast.x - self.selectedStructure.x)**2+\
                                (ast.y - self.selectedStructure.y)**2)**0.5\
                                <= self.selectedStructure.castRange:
                                a = ast
                                i = self.actionNumber
                                self.selectedStructure.actions[i](a)
                                self.targetingAsteroid = False #targets & resets
                            break #dont keep searching
                self.targetingAsteroid = False
                self.actionNumber = -1
            elif self.placingItem == True:
                i = self.actionNumber
                pos1,pos2 = event.pos[0]-\
                            self.camera.dx,event.pos[1]-self.camera.dy
                self.selectedStructure.actions[i](pos1,pos2)
                self.actionNumber = -1
                self.placingItem = False
            elif self.selectingRallyPoint == True:
                self.selectedStructure.rallyPointXY = eventXY
                self.actionNumber = -1
                self.selectingRallyPoint = False
            elif self.targetingAdoption == True and \
                 self.selectedStructure.powered == True:
                for structure in self.Classes.Structure.friendlyStructureList:
                    if structure.name == "Base":
                        continue #can't adopt bases
                    if structure.name == "Beacon":
                        if structure.energyLevel >= \
                           self.selectedStructure.energyLevel: #cant adopt up
                            if self.isWithinBounds\
                               (eventXY,
                                (structure.x-structure.spriteWidth/2,
                                 structure.y-structure.spriteHeight/2),
                                (structure.x+structure.spriteWidth,
                                 structure.y+structure.spriteHeight)):
                                self.selectedStructure.children.append(structure)
                                structure.parents.append(self.selectedStructure)
                                break
                    elif self.isWithinBounds\
                               (eventXY,
                                (structure.x-structure.spriteWidth/2,
                                 structure.y-structure.spriteHeight/2),
                                (structure.x+structure.spriteWidth,
                                 structure.y+structure.spriteHeight)):
                                self.selectedStructure.children.append(structure)
                                structure.parents.append(self.selectedStructure)
                                break                        
                self.targetingAdoption = False
                self.actionNumber = -1

            else: #THIS IS ALL ACTION BASED STUFF
                if self.actionNumber == -1:
                    eventXY=(event.pos[0]-self.camera.dx,
                             event.pos[1]-self.camera.dy)
                    if event.button == 3:#right click gives the ships an order
                        for structure in self.Classes.Structure.enemyStructureList:
                            if structure.hidden == True:
                                continue #disallows selecting hidden structures
                            if self.isWithinBounds(\
                                eventXY,(structure.x+structure.spriteWidth/2,
                                         structure.y+structure.spriteHeight/2),
                                (structure.x-structure.spriteWidth/2,
                                 structure.y-structure.spriteHeight/2)):
                                if structure.selected == False:
                                    self.selectedStructure = structure 
                                    structure.selected = True
                                else:
                                    self.selectedStructure = None
                                    structure.selected = False
                            else:
                                structure.selected = False
                        for structure in\
                            self.Classes.Structure.friendlyStructureList:
                            structure.selected = False #deselects friendly strct
                        self.initialEventXY = eventXY
                        self.multiSelect = True

                    elif event.button == 1:
                        self.initialEventXY = eventXY #stores the location
                        self.selectedStructure = None
                        for ast in self.Classes.Asteroid.asteroidList:
                            if ast.hidden == True:
                                continue #disallows selecting hidden asteroids
                            if self.isWithinBounds(eventXY,
                                                   (ast.x+ast.spriteWidth/2,
                                                    ast.y+ast.spriteHeight/2),
                                                   (ast.x-ast.spriteWidth/2,
                                                    ast.y-ast.spriteHeight/2)):
                                    if ast.selected == False and \
                                       ast.removeReferences == False:
                                        if self.selectedStructure != None:
                                            self.selectedStructure.selected = False
                                        self.selectedStructure = ast
                                    else:
                                        self.selectedStructure = None
                                        ast.selected = False
                            else:
                                ast.selected = False
                        if self.selectedStructure != None:
                            self.selectedStructure.selected = True #only selects one at a time
                        else:
                            for structure in self.Classes.Structure.friendlyStructureList:
                                if structure.hidden == True:
                                    continue #disallows selecting hidden structures
                                if self.isWithinBounds(eventXY,(structure.x+structure.spriteWidth/2,structure.y+structure.spriteHeight/2),(structure.x-structure.spriteWidth/2,structure.y-structure.spriteHeight/2)):
                                    if structure.selected == False and structure.removeReferences == False:
                                        self.selectedStructure = structure #tells ui what to display
                                    else:
                                        self.selectedStructure = None
                                        structure.selected = False
                                else:
                                    structure.selected = False
                            if self.selectedStructure != None:
                                self.selectedStructure.selected = True #only selects one at a time
                        for structure in self.Classes.Structure.enemyStructureList:
                            structure.selected = False
                        self.multiSelect = True
                else:
                    pass #######                

        elif event.type == MOUSEBUTTONUP:
            
            eventXY = (event.pos[0] - self.camera.dx, event.pos[1] - self.camera.dy)
            if event.button == 1:
                if self.withinUIRange(event.pos) == -1:
                    self.finalEventXY = eventXY
                    for ship in self.Classes.FriendlyShip.friendlyShipList:
                        if self.shiftDown == False:
                            ship.selected = False #deselects everything
                        if ship.distance(self.mouse.ax,self.mouse.ay) < ship.spriteRadius:
                            ship.selected = not(ship.selected) #inverts the selection
                        if self.multiSelect == True:
                            if self.isWithinBounds((ship.x,ship.y),self.finalEventXY,self.initialEventXY):
                                ship.selected = True #does not deselect stuff
                    self.multiSelect = False

                    for ship in self.Classes.EnemyShip.selectedEnemyShips: #deselects all enemies
                        ship.selected = False
        
                    self.findSelectedShips() #reloads the selected ships    

            elif event.button == 3:
                self.finalEventXY = eventXY
                for ship in self.Classes.EnemyShip.enemyShipList:
                    if self.shiftDown == False:
                        ship.selected = False #deselects everything
                    if ship.distance(self.mouse.ax,self.mouse.ay) < ship.spriteRadius:
                        ship.selected = not(ship.selected) #inverts the selection
                    if self.multiSelect == True:
                        if self.isWithinBounds((ship.x,ship.y),self.finalEventXY,self.initialEventXY):
                            ship.selected = True #does not deselect stuff
                self.multiSelect = False
                self.findSelectedShips() #reloads the selected ships    
                i = 0 #sets index to 0
                for ship in self.Classes.FriendlyShip.selectedFriendlyShips:
                    i += 1
                    if self.selectedStructure != None and self.selectedStructure.removeReferences == False:
                        if self.selectedStructure.selected == True and self.selectedStructure.isFriendly == False:
                            ship.action = "attacking"
                            ship.attack(self.selectedStructure)
                    elif self.Classes.EnemyShip.selectedEnemyShips != []:
                        ship.action = "attacking"
                        ship.attack(self.Classes.EnemyShip.selectedEnemyShips[random.randint(0,len(self.Classes.EnemyShip.selectedEnemyShips)-1)])
                    else: #move elsewise
                        ship.action = "moving"
                        ship.findFormationPosition(self.mouse.ax,self.mouse.ay,self.Classes.FriendlyShip.selectedFriendlyShips,i)
           
        elif event.type == KEYDOWN:
            if event.key == K_c:
                self.Classes.Game.gameCheats = not(self.Classes.Game.gameCheats)
                self.Classes.Game.gameTextFeedback.insert(0, "Cheats: %s" % self.Classes.Game.gameCheats)
            if event.key == K_q:
                self._running = False
            if event.key == 304: #SHIFT DOWN
                self.shiftDown = True
            if event.key == 32: #SPACE
                if self.Classes.Game.gameCheats == True:
                    self.Classes.Resources.metal += 10000
                    self.Classes.Resources.energy += 10000
            if event.key == 306: #CONTROL
                if self.Classes.Game.gameCheats == True:
                    for ship in self.Classes.FriendlyShip.friendlyShipList:
                        if ship.inactive == True: 
                            ship.buildTime =100000 #automatically builds ships
                    for structure in self.Classes.Structure.friendlyStructureList:
                        if structure.inactive == True:
                            structure.buildTime = 100000
            if event.key == 275: #right
                self.camera.xvel = -15
            elif event.key == 276: #left
                self.camera.xvel = 15
            if event.key == 273: #up
                self.camera.yvel = 15
            elif event.key == 274: #down
                self.camera.yvel = -15
                if self.camera.dy < -self.mapHeight: self.camera.dy = prevdy
                
        elif event.type == KEYUP:
            if event.key == 304: #SHIFT UP
                self.shiftDown = False
            if event.key == 274: #down
                self.camera.yvel = 0
            if event.key == 273: #up
                self.camera.yvel = 0
            if event.key == 276:
                self.camera.xvel = 0
            if event.key == 275:
                self.camera.xvel = 0
                
        elif event.type == QUIT:
            self._running = False
            self.on_cleanup()

    def on_event_mainscreen(self,event):
        if event.type == pygame.QUIT: #if quit, then quit
            self._running = False
            self._mainscreen = False 
        elif event.type == MOUSEBUTTONDOWN:
            if self.isWithinBounds(event.pos,(323,293),(662,375)): #first button
                self._mainscreen = False #play button
            elif self.isWithinBounds(event.pos,(323,402),(662,484)):
                self._mainscreen = False
                self._tutorial = True #tutorial buttons
            elif self.isWithinBounds(event.pos,(323,511),(662,594)):
                self._mainscreen = False
                self._running = False #quit button

    def on_event_tutorial(self,event):
        if event.type == pygame.QUIT: #if quit, then quit
            self._running = False
            self._mainscreen = False 
        elif event.type == MOUSEBUTTONDOWN:
            if self.tutorialPage == 5: #if last page
                self._tutorial = False #go to the main game
            else:
                 self.tutorialPage += 1

    def on_event_winLose(self,event):
        if event.type == pygame.QUIT: #if quit, then quit
            self._winLoseScreen = False
        elif event.type == MOUSEBUTTONDOWN:
            self._winLoseScreen = False

    def moveMouseCursor(self):
        dx,dy = self.camera.dx,self.camera.dy
        pygameMouseX,pygameMouseY = pygame.mouse.get_pos() #stores mouse coord
        self.mouse.ax = pygameMouseX-dx #actual x
        self.mouse.ay = pygameMouseY-dy #actual y
        self.mouse.x = pygameMouseX-dx - self.mouse.spriteWidth/2 #modified mouse coord
        self.mouse.y = pygameMouseY-dy - self.mouse.spriteHeight/2 #use this ONLY for rendering

    def moveBullets(self):
        for bullet in self.Classes.Bullet.bulletList:
            bullet.loop()

    def updateStructures(self):
        for structure in self.Classes.Structure.structureList:
            structure.loop()
            if self.selectedStructure == structure:
                if structure.removeReferences == True:
                    self.selectedStructure = None
    
    def moveShips(self):
        for ship in self.Classes.Ship.shipList:
            ship.loop()

    def findSelectedShips(self):
        selectedE = [] #enemy list
        selectedF = [] #friendly list
        for ship in self.Classes.Ship.shipList:
            if ship.selected == True:
                if ship.friendly == True:
                    selectedF.append(ship)
                else:
                    selectedE.append(ship)
        self.Classes.FriendlyShip.selectedFriendlyShips = copy.copy(selectedF)
        self.Classes.EnemyShip.selectedEnemyShips = copy.copy(selectedE)

    def updateSelectedStructure(self):
        if self.selectedStructure.hidden == True:
            self.selectedStructure = None #deselects hidden structures
        
    def on_loop(self):
        self.moveMouseCursor() #keeps mouse crusor centered on mouse
        self.camera.loop()
        self.updateSelectedStructure
         #moves all ships

    def getTimeSinceLastCall(self):
        return time.time()-self.lastTimeCalled


    def on_loop_time(self): #moves based on time
        
        if self.getTimeSinceLastCall() > DT:
            self.lastTimeCalled = time.time() #resets DT counter
            self.moveShips()
            self.moveBullets()
            self.updateStructures()
            self.minimap.update()

    def on_loop_mainscreen(self):
        self.moveMouseCursor()

    def on_loop_tutorial(self):
        self.moveMouseCursor()

    def on_loop_winLose(self):
        self.moveMouseCursor()

#----------------------------------------------------DRAW FUNCTIONS--------------------------------------------------------------
    def rot_center(self,image,angle): #FROM http://www.pygame.org/wiki/RotateCenter
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def drawStructures(self):
        dx,dy = self.camera.dx,self.camera.dy
        #for structure in self.Classes.Structure.structureList:
        for structure in self.minimap.viewableStructures:
            x,y = structure.x+dx,structure.y+dy
            if structure.powered == True and structure.children != []:
                for children in structure.children:
                    pygame.draw.line(self.Surface,THECOLORS["cyan"],(x,y),(children.x+dx,children.y+dy),2)
            if structure.name == "Turret":
                sprite = self.rot_center(structure.sprite, math.degrees(structure.direction))
            else:
                sprite = structure.sprite
            self.Surface.blit(sprite,(x-structure.spriteWidth/2,y-structure.spriteHeight/2))
            if structure.selected == True:
                structure.drawSelected(self.Surface,structure.x,structure.y,dx,dy)
                
    
    def drawBullets(self):
        dx = self.camera.dx
        dy = self.camera.dy
        for bullet in self.Classes.Bullet.bulletList:
            if bullet.sprite == None:
                pygame.draw.line(self.Surface,bullet.color,(bullet.lx+dx,bullet.ly+dy),(bullet.x+dx,bullet.y+dy))
            else:
                self.Surface.blit(self.rot_center(bullet.sprite,math.degrees(bullet.direction)),(bullet.x-bullet.spriteWidth/2+dx,bullet.y-bullet.spriteWidth/2+dy))
    def drawShips(self):
        dx,dy = self.camera.dx,self.camera.dy
        for ship in self.minimap.viewableShips:
            rotatedShip = self.rot_center(ship.sprite, math.degrees(ship.direction))
            rotatedShipFront = self.rot_center(ship.spriteFront, math.degrees(ship.direction))
            rotatedShipLeft = self.rot_center(ship.spriteLeft, math.degrees(ship.direction))
            rotatedShipRight = self.rot_center(ship.spriteRight, math.degrees(ship.direction))
            rotatedShipBack = self.rot_center(ship.spriteBack, math.degrees(ship.direction))
            x = ship.x - ship.spriteWidth/2 + dx
            y = ship.y - ship.spriteHeight/2 + dy
            self.Surface.blit(rotatedShip, (x,y))
            if ship.frontThrust == True:
                self.Surface.blit(rotatedShipFront, (x,y))
            if ship.backThrust == True:
                self.Surface.blit(rotatedShipBack, (x,y))
            if ship.rightThrust == True:
                self.Surface.blit(rotatedShipRight, (x,y))
            if ship.leftThrust == True:
                self.Surface.blit(rotatedShipLeft, (x,y))
            if ship.selected == True:
                if ship.inactive == True:
                    pygame.draw.arc(self.Surface,THECOLORS["white"],Rect(x-(ship.spriteWidth/2)-6,y-(ship.spriteHeight/2)-6,2*ship.spriteWidth+12,2*ship.spriteHeight+12),
                                    math.pi/2,((math.pi/2)+2*math.pi*(float(ship.buildTime)/ship.buildTimeEnd)),2) #draws buildTime
                if ship.hp > 0:
                    pygame.draw.arc(self.Surface,ship.UIColor,Rect(x-(ship.spriteWidth/2),y-(ship.spriteHeight/2),2*ship.spriteWidth,2*ship.spriteHeight),
                                    math.pi/2,((math.pi/2)+2*math.pi*(float(ship.hp)/ship.maxhp)),2) #draws health
                if ship.armor > 0:
                    pygame.draw.arc(self.Surface,ship.UIColor2,Rect(x-(ship.spriteWidth/2)-2,y-(ship.spriteHeight/2)-2,2*ship.spriteWidth+4,2*ship.spriteHeight+4),
                                    math.pi/2,((math.pi/2)+2*math.pi*(float(ship.armor)/ship.maxArmor)),2) #draws armor
                if ship.shields > 0:
                    pygame.draw.arc(self.Surface,ship.UIColor3,Rect(x-(ship.spriteWidth/2)-4,y-(ship.spriteHeight/2)-4,2*ship.spriteWidth+8,2*ship.spriteHeight+8),
                                    math.pi/2,((math.pi/2)+2*math.pi*(float(ship.shields)/ship.maxShields)),2) #draws shields

    def drawMiniMap(self,x0,y0,x1,y1):
        sizeRatio = float(y1-y0)/self.mapHeight
        pygame.draw.rect(self.Surface,THECOLORS["black"],Rect(x0,y0,(x1-x0),(y1-y0)))
        tenths = (x1-x0)/10.0
        for i in xrange(11):
            pygame.draw.line(self.Surface,THECOLORS["blue"],(x0+i*tenths,y0),(x0+i*tenths,y1))
            pygame.draw.line(self.Surface,THECOLORS["blue"],(x0,y0+i*tenths),(x1,y0+i*tenths))
        self.minimap.draw(self.Surface)
        dx = abs(self.camera.dx)
        dy = abs(self.camera.dy)
        x2 = x0+(dx*sizeRatio)
        y2 = y0+(dy*sizeRatio)
        pygame.draw.rect(self.Surface,THECOLORS["white"],Rect(x2,y2,(self.width*sizeRatio),((self.height+self.uiHeight)*sizeRatio)),1)

    def drawMiddleBar(self,x0,y0,x1,y1):
        if self.selectedStructure != None:
            self.Surface.blit(pygame.transform.scale(self.selectedStructure.sprite,(64,64)),(x0+27,y0+27))
            for i in xrange(self.selectedStructure.attributesNumber):
                text = self.medFont.render("%s: %s" % (self.selectedStructure.attributes[i][0],self.selectedStructure.attributes[i][1]), 1, THECOLORS["white"])
                self.Surface.blit(text, (345, 600 + (20*i)))

    def drawTopBar(self):
        self.Surface.blit(self.Classes.Sprites.sprMenuTop,(self.width-160,10))
        text1 = self.smallFont.render("%d" % self.Classes.Resources.metal, 1, THECOLORS["white"])
        text2 = self.smallFont.render("%d" % self.Classes.Resources.energy, 1, THECOLORS["white"])
        text3 = self.smallFont.render("%d/%d" % (self.Classes.FriendlyShip.friendlyShipNumber,self.Classes.Resources.unitCap), 1, THECOLORS["white"])
        self.Surface.blit(text1, (868, 30))
        self.Surface.blit(text2, (913, 30))
        self.Surface.blit(text3, (958, 30))

    def drawActions(self,structure):
        if structure != None and structure.inactive == False:
            if structure.actions != []:
                i = 0
                a = [(673,535),(754,535),(836,535),(917,535),
                     (673,615),(754,615),(836,615),(917,615)]
                for action in structure.actionSprites:
                    self.Surface.blit(action,a[i])
                    i += 1
    
    def drawMenuBar(self):
        self.Surface.blit(self.Classes.Sprites.sprMenu,(0,self.height))
        self.drawMiniMap(19,self.height+20,183,self.height+184)
        self.drawMiddleBar(223,self.height+81,661,self.height+200)
        self.drawActions(self.selectedStructure)

    def drawGameTextFeedback(self,x,y):
        self.Classes.Game.gameTextFeedback = self.Classes.Game.gameTextFeedback[0:3] #truncates previous messages
        for i in xrange(3): #renders only the 3 most recent messages 
            text = self.medFont.render(self.Classes.Game.gameTextFeedback[i], 1, Color(255-90*i,255-90*i,255-90*i))
            self.Surface.blit(text, (x, y - (20*i)))
    
    def drawUI(self):
        dx,dy = self.camera.dx,self.camera.dy
        if self.multiSelect == True: #draws the multiselect rectangle
            initXY = [self.initialEventXY[0]+dx,self.initialEventXY[1]+dy]
            ptlist = [initXY,(initXY[0],self.mouse.ay+dy),(self.mouse.ax+dx,self.mouse.ay+dy),(self.mouse.ax+dx,initXY[1])]
            pygame.draw.polygon(self.Surface,THECOLORS["yellow"],ptlist,1) #polygons allow for more freedom in drawing
        self.drawMenuBar()
        self.drawTopBar()
        self.drawGameTextFeedback(20, 474)
        self.Surface.blit(self.mouse.sprite, (self.mouse.x+dx,self.mouse.y+dy)) #draws cursor
#--------------------------------------------------------------------------------------------------------------------------------
    
    def on_render(self):
        self.Surface.blit(self.background.sprite, ((self.camera.dx)/(self.mapMultiplier*1.5),self.camera.dy/(self.mapMultiplier*1.5))) #draws background
        self.drawStructures() #draws all building
        self.drawBullets()
        self.drawShips() #draws all ships
        self.drawUI() #draws user interface
        pygame.display.flip()
        #self.fpsClock.tick(FRAMESPERSEC)

    def on_render_mainscreen(self):
        self.Surface.blit(self.Classes.Sprites.bgMainscreen,(0,0))
        self.Surface.blit(self.Classes.Sprites.bgMainscreenParallax1,(-80+(self.mouse.x*0.04),-60+(self.mouse.y*0.03)))
        self.Surface.blit(self.Classes.Sprites.bgMainscreenParallax2,(-80+(self.mouse.x*0.08),-60+(self.mouse.y*(0.06))))
        if self.mouse.y < 390: #top half
            self.Surface.blit(self.Classes.Sprites.bgMainscreenButton,(273,310))
        elif self.mouse.y < 498:
            self.Surface.blit(self.Classes.Sprites.bgMainscreenButton,(273,415))
        else:
            self.Surface.blit(self.Classes.Sprites.bgMainscreenButton,(273,520))
        self.Surface.blit(self.mouse.sprite, (self.mouse.x,self.mouse.y))
        pygame.display.flip()

    def on_render_tutorial(self):
        self.Surface.blit(self.tutorialPages[self.tutorialPage],(0,0))
        self.Surface.blit(self.mouse.sprite, (self.mouse.x,self.mouse.y))
        pygame.display.flip()

    def on_render_winLose(self):
        self.Surface.blit(self.mouse.sprite, (self.mouse.x,self.mouse.y))
        if self.Classes.Game.playerWins == False:
            self.Surface.blit(self.Classes.Sprites.bgLoseScreen,(0,0))
        else:
            self.Surface.blit(self.Classes.Sprites.bgWinScreen,(0,0))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        
        if self.on_init() == False:
            self._running = False
        while(self._mainscreen):
            for event in pygame.event.get():
                self.on_event_mainscreen(event)
            self.on_loop_mainscreen()
            self.on_render_mainscreen()
        while(self._tutorial):
            for event in pygame.event.get():
                self.on_event_tutorial(event)
            self.on_loop_tutorial()
            self.on_render_tutorial()
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_loop_time()
            self.on_render()
            if self.Classes.Game.gameEnd == True:
                self._running = False
                self._winLoseScreen = True # move to next screen
        while( self._winLoseScreen):
            for event in pygame.event.get():
                self.on_event_winLose(event)
            self.on_loop_winLose()
            self.on_render_winLose()
        self.on_cleanup()
 
if __name__ == "__main__" :
    game = SpaceInvaders()
    game.on_execute()

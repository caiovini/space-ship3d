from panda3d.core import (loadPrcFileData, 
                          AmbientLight,
                          NodePath, 
                          KeyboardButton, 
                          CollisionSphere, 
                          CollisionNode, 
                          CollisionTraverser, 
                          CollisionHandlerEvent, 
                          TextNode)


from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from star import Star

import random
import os
import math

ship_texture_path = os.path.join("assets", "corvette01_specular.png")
ship_path = os.path.join("assets", "corvette01.obj")

meteor_texture_path = os.path.join("assets", "rock_c_01_normal.dds")
meteor_path = os.path.join("assets", "rock_c_01.obj")

left_button = KeyboardButton.ascii_key('a')
right_button = KeyboardButton.ascii_key('d')

down_button = KeyboardButton.ascii_key('w')
up_button = KeyboardButton.ascii_key('s')

BLACK = (0, 0, 0)

class Game(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        base.cTrav = CollisionTraverser()

        # Initialize the handler.
        self.collHandEvent = CollisionHandlerEvent()
        self.collHandEvent.addInPattern('into-%in')

        self.accept('escape', base.finalizeExit)

        self.collCount = 0
        self.score = 0
        self.game_over = False

        star = Star()
        self.stars = []

        # Create coordinates for the stars
        x = [random.randint(-20, 20) for i in range(500)]
        y = [random.randint(-20, 20) for i in range(500)]
        z = [random.randint(-20, 20) for i in range(500)]

        for a, b, c in zip(x, y, z):
            self.stars.append(
                self.render.attachNewNode(star.create((a, c, b))))
            self.stars[-1].setHpr(0, 90, 0)

        self.render.set_shader_auto()

        meteor_texture = self.loader.loadTexture(meteor_texture_path)
        self.meteor = self.loader.loadModelCopy(meteor_path)
        self.meteor.setTexture(meteor_texture, 1)
        self.meteor.set_scale(1.55, 1.55, 1.55)
        self.meteor.setPos(random.randint(-10, 10), 160, random.randint(-10, 10))

        shipTxture = self.loader.loadTexture(ship_texture_path)
        self.ship = self.loader.loadModelCopy(ship_path)
        self.ship.setTexture(shipTxture, 1)
        self.ship.set_scale(1.55, 1.55, 1.55)
        self.ship.setPos(0, 30, 0)
        self.ship.setHpr(180, 90, 0)

        ship_sphere = self.initCollisionSphere(self.ship, False)
        ambient_ship = AmbientLight('ambient-ship')
        ambient_ship.setColorTemperature(5500)
        ambient_ship_NP = self.ship.attachNewNode(ambient_ship)
        self.ship.setLight(ambient_ship_NP)


        ambient_meteor = AmbientLight('ambient-meteor')
        ambient_meteor.setColorTemperature(1500)
        ambient_meteor = self.meteor.attachNewNode(ambient_meteor)
        self.meteor.setLight(ambient_meteor)

        meteor_sphere = self.initCollisionSphere(self.meteor, False)
        base.cTrav.addCollider(ship_sphere[0], self.collHandEvent)
        base.cTrav.addCollider(meteor_sphere[0], self.collHandEvent)


        self.accept(f"into-{ship_sphere[1]}", self.handle_collision)

        base.disableMouse()
        base.setBackgroundColor(BLACK) # Black like space
        base.camera.lookAt(self.ship)

        self.ship.reparent_to(self.render)
        self.meteor.reparent_to(self.render)

        taskMgr.add(self.handle_stars, 'task_star')
        taskMgr.add(self.move_task, "task_move") 
        taskMgr.add(self.normalize, "task_normalize")


        self.textGameOver = TextNode('node-game-over')
        self.textGameOver.setTextColor(255, 255, 0, 1)
        
        self.textNodePath = aspect2d.attachNewNode(self.textGameOver)
        self.textNodePath.setScale(0.10)
        self.textNodePath.setPos(-0.3, 0, 0)


        self.textScore = TextNode('node-score')
        self.textScore.setText(f"Score: {self.score}")
        self.textScore.setTextColor(255, 255, 0, 1)
        
        self.textScorePath = aspect2d.attachNewNode(self.textScore)
        self.textScorePath.setScale(0.10)
        self.textScorePath.setPos(-1.3, 0, 0.9)

    def handle_collision(self, collEntry):
        self.textGameOver.setText("GAME OVER !!!")
        self.game_over = True

    def move_task(self, _):

        """
            Move the ship according to the keys pressed by the user
            this changes perspective and position
            Ship does not go forward because the star coming in the direction of the ship give the sensation of movements

        """

        is_down = base.mouseWatcherNode.is_button_down

        if is_down(left_button):
            self.ship.setX(self.ship.getX() - .1)

            [l.setX(l.getX() - .1) for l in self.stars]
            if not self.ship.getH() > 210:
                self.ship.setH(self.ship.getH() + 1)

        if is_down(right_button):
            self.ship.setX(self.ship.getX() + .1)

            [l.setX(l.getX() + .1) for l in self.stars]
            if not self.ship.getH() < 150:
                self.ship.setH(self.ship.getH() - 1)

        if is_down(down_button):
            self.ship.setZ(self.ship.getZ() - .1)

            [l.setZ(l.getZ() - .1) for l in self.stars]
            if not self.ship.getP() > 120:
                self.ship.setP(self.ship.getP() + 1)

        if is_down(up_button):
            self.ship.setZ(self.ship.getZ() + .1)

            [l.setZ(l.getZ() + .1) for l in self.stars]
            if not self.ship.getP() < 60:
                self.ship.setP(self.ship.getP() - 1)

        """
            Move the meteor towards the ship
            position x and z are random according to ship coordinates

        """

        self.meteor.setY(self.meteor.getY() - 1)
        if self.meteor.getY() < -10: # Generate new meteor after this point
            self.meteor.setPos(random.randint(math.ceil(self.ship.getX() - 1), math.ceil(self.ship.getX() + 10)),
                               150, random.randint(math.ceil(self.ship.getZ() - 1), math.ceil(self.ship.getZ() + 10)))
            self.score += 1
            self.textScore.setText(f"Score: {self.score}")

        if not self.game_over:
            return Task.cont 

    def normalize(self, task):

        """
            Ship perspective changes as soon as player turns to the right or to the left
            make it go back to its original perspective coordinates

            original perspective: self.ship.getHpr --> (180, 90, 0)
        """

        is_down = base.mouseWatcherNode.is_button_down
        diff_camera_x = self.ship.getX() - base.camera.getX()
        diff_camera_z = self.ship.getZ() - base.camera.getZ()

        if not is_down(left_button):
            if self.ship.getH() > 180:
                self.ship.setH(self.ship.getH() - 1)

           
        if not is_down(right_button):
            if self.ship.getH() < 180:
                self.ship.setH(self.ship.getH() + 1)

            
        if not is_down(up_button):
            if self.ship.getP() < 90:
                self.ship.setP(self.ship.getP() + 1)

        
        if not is_down(down_button):
            if self.ship.getP() > 90:
                self.ship.setP(self.ship.getP() - 1)

        # Left and right 
        if diff_camera_x > 10:
            base.camera.setX(base.camera.getX() + .1)
        if diff_camera_x < -10:
            base.camera.setX(base.camera.getX() - .1)


        # Up and down
        if diff_camera_z > 7:
            base.camera.setZ(base.camera.getZ() + .1)
        if diff_camera_z < -7:
            base.camera.setZ(base.camera.getZ() - .1)

        if not self.game_over:
            return Task.cont

    def handle_stars(self, task):
        for star in self.stars:
            y_position = star.getY()
            if(y_position > -5):
                star.setY(y_position - 0.5)

            else:
                star.setY(random.randint(0, 50))

        return Task.cont

    def initCollisionSphere(self, obj, show=False):
        
        # Get the size of the object for the collision sphere.
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius() * 0.8

        # Create a collision sphere and name it something understandable.
        collSphereStr = f'CollisionHull{self.collCount}_{obj.name}'
        self.collCount += 1
        cNode = CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(center, radius))

        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()

        # Return a tuple with the collision node and its corrsponding string so
        # that the bitmask can be set.
        return (cNodepath, collSphereStr)


if __name__ == "__main__":
    game = Game()
    game.run()

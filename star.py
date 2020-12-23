from panda3d.core import NodePath, LineSegs

class Star():
    def __init__(self):
        
        self.np = NodePath('pen')

    def create( self, pos):

        segs = LineSegs()
        segs.setThickness(1.0)
        segs.moveTo( pos[0], pos[1], pos[2] - 1)
        segs.setColor(255, 255, 255, 1)
        segs.drawTo(pos)
        return segs.create()



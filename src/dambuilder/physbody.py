import ode

ode_world = ode.World()
ode_space = ode.Space()
contactgroup = ode.JointGroup()
    
def Ball(density, radius, x, y):
    body = ode.Body(ode_world)
    m = ode.Mass()
    m.setSphere(density, radius)
    body.setMass(m)
    body.setPosition((x, y, 0))
    # XXX do I need to keep joints alive?
    j = ode.Plane2DJoint(ode_world)
    j.attach(body, None)
    geom = ode.GeomSphere(ode_space, radius=radius)
    geom.setBody(body)
    return geom

def Immovable(x, y, w, h):
    # immovable object, so no body needed
    geom = ode.GeomBox(ode_space, (w, h, 0))
    geom.setPosition((x, y, 0))
    return geom

class CollisionBase(object):
    """Base class for all objects that need to detect collisions.
    """
    def __init__(self, geom):
        self.geom = geom
        geom.obj = self
        self._collisions = []

    def clear_collisions(self):
        self._collisions = []
        
    def add_collision(self, obj):
        self._collisions.append(obj)
        

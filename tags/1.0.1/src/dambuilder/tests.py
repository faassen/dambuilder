import unittest, doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def approx(a, b, d=0.001):
    """Float value a is approximately b.
    """
    return (a - d) < b < (a + d)

class MockGeomSphere(object):
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def getPosition(self):
        return self.x, self.y, self.z

    def getRadius(self):
        return self.radius

class MockGeomBox(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def setLengths(self, t):
        w, h, z = t
        self.w = w
        self.h = h
        
    def getPosition(self):
        return self.x, self.y, 0

    def getLengths(self):
        return self.w, self.h, 0

    def getAABB(self):
        # XXX only implemented as far as the tests need it..
        w = self.w / 2.
        return self.x - w, self.x + w, None, None, None, None 
    
globs = {'approx': approx,
         'MockGeomSphere': MockGeomSphere,
         'MockGeomBox': MockGeomBox}

def setUp(testcase):
    from dambuilder import physbody
    # we don't want the real ode
    physbody.ode_world = None
    physbody.ode_space = None
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('waterlevel.txt',
                             globs=globs,
                             optionflags=optionflags,
                             setUp=setUp),
        doctest.DocFileSuite('living.txt',
                             globs=globs,
                             optionflags=optionflags,
                             setUp=setUp),
        doctest.DocFileSuite('world.txt',
                             globs=globs,
                             optionflags=optionflags,
                             setUp=setUp),
        doctest.DocFileSuite('view.txt',
                             globs=globs,
                             optionflags=optionflags,
                             setUp=setUp),
        ])
    return suite

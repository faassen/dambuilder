
class Waterlevel(object):
    """A water level has several inputs."""

    def __init__(self, id, level):
        self.id = id
        self.level = float(level)

class Watersource(object):
    """A source has no level itself.
    """

    def __init__(self, id):
        self.id = id
        self.level = None

class WaterlevelError(Exception):
    pass

class World(object):
    def __init__(self):
        self._levels = {}
        self._connections = {}
        self._flows_into = {}

    def add_level(self, id, h):
        level = Waterlevel(id, h)
        self._levels[id] = level
        return level

    def add_source(self, id):
        source = Watersource(id)
        self._levels[id] = source
        return source
    
    def connect(self, connection_id, source, target, rate, minimum_level=0.):
        assert source.id != target.id
        if rate < 0:
            source, target = target, source
            rate = -rate
        if target.level is None:
            raise WaterlevelError("Cannot flow water into source.")
        self._connections[connection_id] = Connection(connection_id,
                                                      source.id,
                                                      target.id,
                                                      rate,
                                                      minimum_level)
        
    def disconnect(self, connection_id):
        del self._connections[connection_id]

    def get_level(self, level_id):
        return self._levels[level_id]
    
    def get_connection(self, connection_id):
        return self._connections[connection_id]
    
    def have_connection(self, connection_id):
        return connection_id in self._connections
    
    def step(self, stepsize):
        for connection in self._connections.values():
            connection.step(stepsize, self)

class Connection(object):
    def __init__(self, id, source_id, target_id, rate, minimum_level):
        self.id = id
        self.source_id = source_id
        self.target_id = target_id
        self.rate = rate
        self.minimum_level = minimum_level
        
    def step(self, stepsize, world):
        source = world.get_level(self.source_id)
        target = world.get_level(self.target_id)
        # if source is actually lower than target, reverse flow
        if source.level is not None and source.level < target.level:
            source, target = target, source
        amount = self.rate * stepsize
        # equalize level if that is possible this step
        if source.level is not None:
            difference = source.level - target.level
            if difference < amount:
                amount = difference / 2.
        target.level += amount
        if source.level is not None:
            source.level -= amount
            overspill = self.minimum_level - source.level
            if overspill > 0.:
                source.level += overspill
                target.level -= overspill

                

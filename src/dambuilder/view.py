
class View(object):
    def __init__(self, pixel_width, pixel_height, pixels_per_meter,
                 origin_x, origin_y):
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.pixels_per_meter = pixels_per_meter
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.width = float(pixel_width) / pixels_per_meter
        self.height = float(pixel_height) / pixels_per_meter
        self.halfway_x = self.width / 2.
        self.halfway_y = self.height / 2.
        
    def set_origin(self, origin_x, origin_y):
        self.origin_x = origin_x
        self.origin_y = origin_y

    def set_view(self, x, y):
        if x > self.halfway_x:
            self.origin_x = x - self.halfway_x
        else:
            self.origin_x = 0.
        if y > self.halfway_y:
            self.origin_y = y - self.halfway_y
        else:
            self.origin_y = 0.
            
    def get_origin(self):
        return self.origin_x, self.origin_y
    
    def coord(self, x, y):
        return (int(self.pixels_per_meter * (x - self.origin_x)),
                int(self.pixel_height -
                    (self.pixels_per_meter * (y - self.origin_y))))

    def conv(self, r):
        return int(self.pixels_per_meter * r)

    def visible(self, c, w, h):
        x, y = c
        if x + w < 0:
            return False
        if y + w < 0:
            return False
        if x >= self.pixel_width:
            return False
        if y >= self.pixel_height:
            return False
        return True
    
player_view = View(800, 550, 64., 0., 0.)
coord = player_view.coord
conv = player_view.conv
set_view = player_view.set_view
visible = player_view.visible

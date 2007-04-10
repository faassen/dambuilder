from dambuilder.view import player_view, coord, visible
from dambuilder.load import load
from dambuilder.constants import WOOD, STONE, BRICK, METAL

SECTION_HEIGHT = 20. / player_view.pixels_per_meter

def render_material(screen, x, y, material):
    if material is WOOD:
        image = load('materials', 'wood_01.png')
    elif material is STONE:
        image = load('materials', 'stones.png')
    elif material is BRICK:
        image = load('materials', 'bricks.png')
    elif material is METAL:
        image = load('materials', 'metal.png')
    screen.blit(image, coord(x, y))
    

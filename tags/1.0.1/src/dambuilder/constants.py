# color of the sky/background
SKY_COLOR = (229, 253, 250)
# color of the water
WATER_COLOR = (128, 166, 201)
# color of water in the waterfall
WATERFALL_COLOR = (120, 160, 190)

# display color
DISPLAY_COLOR = (40, 40, 40)
# text color in display
TEXT_COLOR = (255, 255, 255)
# selected text background color for display
SELECTED_COLOR = (255, 100,  100)

# maximum X coordinate of player
MAX_X = 25

# force with which the beaver walks
WALK_FORCE = 3.
# force with which the beaver jumps
JUMP_FORCE = 40.
# force the beaver uses to climb up and down
CLIMB_Y_FORCE = 4.
# force the beaver uses to swim up and down
SWIM_Y_FORCE = 4.

# area in which the beaver can fix leaks
FIX_SIZE = 1.0
# leak per second the beaver can fix
FIX_AMOUNT = 0.05

# if a dam floods on top, the rate with which it floods
FLOOD_RATE = 0.1

# water level lower than a nth of the size of a living is neglible. It
# will not even cause wading
NEGLIBLE_WATER_LEVEL_FACTOR = 8.

# slack in meters for when an object 'near' a dam
NEAR_DAM_SLACK = 0.05

# gravity of simulation
GRAVITY = -9.81

# force in which waterfall droplets are ejected
WATERFALL_DROPLET_FORCE = 0.01

# cycle action timeout in ms
CYCLE_TIMEOUT = 250
# build action timeout in ms
BUILD_TIMEOUT = 750
# timeout for buying stuff in ms
BUY_TIMEOUT = 100

# initial rate of created leak
INITIAL_LEAK_RATE = 0.01

# chance of new leaks appearing spontaneously, per second
# (scaled to dam size)
NEW_LEAK_CHANCE = 0.05

# the maximum amount of items in the game at the same time
MAX_ITEMS = 15
# maximum amount of critters
MAX_LIVINGS = 12

# kinds of materials
WOOD = 'wood'
STONE = 'stone'
BRICK = 'brick'
METAL = 'metal'

MATERIALS = [WOOD, STONE, BRICK, METAL]

# cost in trash of a certain material
MATERIAL_COST = {
    WOOD: 1,
    STONE: 2,
    BRICK: 4,
    METAL: 5,
    }

# when a leak already exists, chance leak will increase in size, no water yet
MATERIAL_EROSION_DRY = {
    WOOD: 0.001,
    STONE: 0.0005,
    BRICK: 0.0002,
    METAL: 0.0,
    }

# when a leak already exists and water is flowing through it, leak chance
MATERIAL_EROSION_WET = {
    WOOD: 0.004,
    STONE: 0.002,
    BRICK: 0.001,
    METAL: 0.002, # metal in water
    }

# how fast an animal can erode this
MATERIAL_ANIMAL_EROSION = {
    WOOD: 1.,
    STONE: 0.75,
    BRICK: 0.5,
    METAL: 0.2,
    }

# max velocity at which nibbling is possible
NIBBLE_VELOCITY = 0.01

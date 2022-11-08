from random import randrange


def rand_color():
    return randrange(255), randrange(255), randrange(255)


# define the RGB value
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
light_blue = (0, 255, 255)
dark_blue = (0, 0, 128)
brown = (165, 42, 42)
dark_brown = (139, 69, 19)
door_color = (169, 99, 39)
gray = (128, 128, 128)
white_dark = (200, 200, 200)
# background = (163, 145, 135)
background = (200, 183, 173)
magenta = (255, 0, 255)
yellow = (255, 255, 0)
dark_yellow = (255, 215, 0)
cyan = (0, 255, 255)
active_sprite = cyan
orange = (255, 165, 0)

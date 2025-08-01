## Create the simple logic for rolling 2 dice and display the dice roll

#!pip install pygame

import pygame
import random

pygame.init()

# ## Set pygame screen
# screen_width = 800
# screen_height = 800
# screen = pygame.display.set_mode((screen_width, screen_height))
# pygame.display.set_caption("Dice Roller")

## Font 
font = pygame.font.SysFont('Courier New', 30)
value_font = pygame.font.SysFont('Arial', 36)

DICE_ART = {

    1: (
        "┌─────────┐",
        "│         │",
        "│    ●    │",
        "│         │",
        "└─────────┘",
    ),

    2: (
        "┌─────────┐",
        "│  ●      │",
        "│         │",
        "│      ●  │",
        "└─────────┘",
    ),

    3: (
        "┌─────────┐",
        "│  ●      │",
        "│    ●    │",
        "│      ●  │",
        "└─────────┘",
    ),

    4: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│         │",
        "│  ●   ●  │",
        "└─────────┘",
    ),

    5: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│    ●    │",
        "│  ●   ●  │",
        "└─────────┘",

    ),

    6: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "└─────────┘",
    ),

}

DIE_HEIGHT = len(DICE_ART[1])
DIE_WIDTH = len(DICE_ART[1][0])
DIE_FACE_SEPARATOR = " "

## Roll 2 dice 
def dice_roll():
    return (random.randint(1,6), random.randint(1,6))

## If the two dices are equal, add to the total 
def dice_logic(rolled, previous_rolls):
    if rolled[0] == rolled[1]:
        previous_rolls.append(rolled)
        return True

    else:
        previous_rolls.clear()
        return False

## Display the actual value of the dice roll from the DICE_ART 
def draw_dice(screen, dice_values, x, y):
    for i, value in enumerate(dice_values):
        die_art = DICE_ART[value]
        for row_index, row in enumerate(die_art):
            text_surface = font.render(row, True, (0, 0, 0))
            screen.blit(text_surface, (x + i * 200, y + row_index * 30))  # Offset for 2nd die

def draw_total(screen, dice_values, x, y, value_font):
    total = sum(dice_values)
    total_surface = value_font.render(f"Total: {total}", True, (0, 0, 0))
    screen.blit(total_surface, (x - total_surface.get_width()//2, y))

## Button Properties 
but_x = 300
but_y = 600
but_width = 200
but_height = 80
but_color = (255, 0, 0)

but_rect = pygame.Rect(but_x, but_y, but_width, but_height)

circ_center = (400, 650)
circ_rad = 50
circ_color = (255, 0, 0)

def is_inside_circle(pos, center, radius):
    return (pos[0] - center[0])**2 + (pos[1] - center[1])**2 <= radius**2

def make_dice_button(screen, circ_color, circ_center, circ_rad):
    pygame.draw.circle(screen, circ_color, circ_center, circ_rad)
    button_text = value_font.render("ROLL", True, (255, 255, 255))
    text_rect = button_text.get_rect(center=circ_center)
    screen.blit(button_text, text_rect)

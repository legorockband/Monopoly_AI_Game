## Create the simple logic for rolling 2 dice and display the dice roll

#!pip install pygame

import pygame
import random

pygame.init()

## Set pygame screen
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dice Roller")

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

def dice_roll():
    ## Roll 2 dice 
    return (random.randint(1,6), random.randint(1,6))

## If the two dices are equal add to the total 
def dice_logic(rolled, previous_rolls):
    if rolled[0] == rolled[1]:
        previous_rolls.append(rolled)
        print(f"Number of doubles {len(previous_rolls)}")



def draw_dice(screen, dice_values, x, y):
    for i, value in enumerate(dice_values):
        die_art = DICE_ART[value]
        for row_index, row in enumerate(die_art):
            text_surface = font.render(row, True, (0, 0, 0))
            screen.blit(text_surface, (x + i * 200, y + row_index * 30))  # Offset for 2nd die

def draw_total(screen, dice_values):
    total = sum(dice_values)
    total_surface = value_font.render(f"Total: {total}", True, (0, 0, 0))
    screen.blit(total_surface, (screen_width//2 - total_surface.get_width()//2, 100))

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

running = True
rolled = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            ## If the mouse clicks on the button roll the dice
            if is_inside_circle(event.pos, circ_center, circ_rad):
                rolled = dice_roll()

    # Fill the background with white
    screen.fill((255, 255, 255))

    ## Make a button 
    pygame.draw.circle(screen, circ_color, circ_center, circ_rad)
    button_text = value_font.render("ROLL", True, (255, 255, 255))
    text_rect = button_text.get_rect(center=circ_center)
    screen.blit(button_text, text_rect)
    
    if rolled:
        draw_dice(screen, rolled, 200, 200)
        draw_total(screen, rolled)
    
    pygame.display.flip()

pygame.quit()




# def main():
#     last_rolls = []
    
#     for i in range(3):
#         rolled = dice_roll()
#         print(rolled)
#         dice_displayed = generate_dice_faces_diagram(rolled)
#         print(f"{dice_displayed}\n")        
#         dice_logic(rolled, last_rolls)


# if __name__ == "__main__":
#     main()

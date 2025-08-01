import pygame
import dice
import board_test
import sys

import os
import pygame
import ctypes

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

screen_width, screen_height = pygame.display.get_surface().get_size()

# Maximize the window (Windows only)
if os.name == 'nt':
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.ShowWindow(hwnd, 3)  # 3 = SW_MAXIMIZE
    
clock = pygame.time.Clock()
pygame.display.set_caption("Monopoly")
value_font = pygame.font.SysFont('Arial', 30)

spaces_names = [
    "GO", "MEDITERRANEAN AVENUE", "COMMUNITY CHEST", "BALTIC AVENUE",
    "INCOME TAX", "READING RAILROAD", "ORIENTAL AVENUE", "CHANCE",
    "VERTMONT AVENUE", "CONNETICUT AVENUE", "JUST VISITING", "ST. CHARLES PLACE",
    "ELECTRIC COMPANY", "STATES AVENUE", "VIRGINIA AVENUE", "PENNSYLVANIA RAILROAD",
    "ST. JAMES PLACE", "COMMUNITY CHEST", "TENNESSEE AVENUE", "NEW YORK AVENUE",
    "FREE PARKING", "KENTUCKY AVENUCE", "CHANCE", "INDIANA AVENUE", "ILLIONOIS AVENUE",
    "B. & O. RAILROAD", "ATLANTIC AVENUE", "VENTNOR AVENUE", "WATER WORKS",
    "MARVIN GARDENS", "GO TO JAIL", "PACIFIC AVENUE", "NORTH CAROLINA AVENUE", "COMMUNITY CHEST",
    "PENNSYLVANIA AVENUE", "SHORT LINE RAILROAD", "CHANCE", "PARK PLACE", "LUXURY TAX",
    "BOARDWALK"
]

# shorter for the boxes for now
spaces_names_2 = [
    "GO", "MA", "CC", "BA",       
    "Tax", "RR", "OA", "Ch", 
    "VA", "CA", "Just Visiting", "SCP",    
    "EC", "SA", "VA", "PRR", 
    "SJP", "CC", "TA", "NYA", 
    "Free Parking", "KA", "Ch", "IA", "ILA",  
    "B&O", "AA", "VA", "WC", 
    "MG", "Go To Jail", "PA", "NCA", "CC", 
    "PAA", "SL", "Ch", "PP", "LT", 
    "BW"
]

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

## Button Properties 
but_x = 1000
but_y = 600
but_width = 200
but_height = 80
but_color = (255, 0, 0)

but_rect = pygame.Rect(but_x, but_y, but_width, but_height)

circ_center = (1200, 375)
circ_rad = 50
circ_color = (255, 0, 0)

## Global Var to know how much to move
total_roll = None

def running_display():
    running = True
    rolled = None

    doubles_rolled = []
    is_double = False

    player_pos = 0  ## Starts at "GO"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                ## If the mouse clicks on the button roll the dice
                if dice.is_inside_circle(mouse_pos, circ_center, circ_rad):
                    rolled = dice.dice_roll()
                    is_doubles = dice.dice_logic(rolled, doubles_rolled)
                    roll_total = sum(rolled)
                    player_pos = (player_pos + roll_total) % 40     ## Added so it can only be 0 - 40

        ## Properties of the board
        board_size = int(min(screen_height, (5/8) * screen_width))
        corner_size = board_size // 7
        space_size = (board_size - 1.9 * corner_size) // 9

        board_test.board_game(screen_width, screen_height, board_size, corner_size, space_size)

        ## Make a button 
        dice.make_dice_button(screen, circ_color, circ_center, circ_rad)

        board_test.move_player(screen, player_pos, board_size, corner_size, space_size)

        ## Display dice roll and total 
        if rolled:
            dice.draw_dice(screen, rolled, circ_center[0] - 200, circ_center[1] - 200)
            dice.draw_total(screen, rolled, circ_center[0], circ_center[1] - 350, value_font)

            if is_doubles:
                doubles_text = value_font.render("You rolled doubles!", True, (0, 0, 0))
                screen.blit(doubles_text, (circ_center[0] - doubles_text.get_width()//2, circ_center[1] - 300)) # 100

            if len(doubles_rolled) >= 3:
                jail_text = value_font.render("Too Many Doubles Rolled, Go To Jail", True, (255, 0, 0))
                screen.blit(jail_text, (circ_center[0] - jail_text.get_width()//2, circ_center[1] - 250))    # 150
        

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    running_display()
    print(total_roll)

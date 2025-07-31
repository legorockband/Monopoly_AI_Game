#board.py
# reference link : https://www.pygame.org/docs/
import pygame
import ctypes
import os
import sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

# Maximize the window (Windows only)
if os.name == 'nt':
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.ShowWindow(hwnd, 3)  # 3 = SW_MAXIMIZE
clock = pygame.time.Clock()

pygame.display.flip()

pygame.display.set_caption("Monopoly")
font = pygame.font.SysFont(None, 16)

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
    "MA", "CC", "BA", "Tax", "RR", "OA", "Ch", "VA", "CA",      ## Bottom row   (0-8)
    "SCP", "EC", "SA", "VA", "PRR", "SJP", "CC", "TA", "NYA",   ## Left Row     (9-17)
    "KA", "Ch", "IA", "ILA", "B&O", "AA", "VA", "WC", "MG",     ## Top Row      (18-26)    
    "PA", "NCA", "CC", "PAA", "SL", "Ch", "PP", "LT", "BW"      ## Right Row    (27-35)
]

corner_names_short = [
    "GO", "Just Visiting", "Free Parking", "Go To Jail"
]

def board_game(screen_width:int, screen_height:int):
    screen.fill((255, 255, 255))

    ## Multiple the width by 5/8 because need space for the dice roll and player stats
    board_size = int(min(screen_height, (5/8) * screen_width))

    corner_size = board_size // 7
    space_size = (board_size - 1.9 * corner_size) // 9

    corner_positions = [
    (board_size - corner_size, board_size - corner_size),  # GO (bottom-right)
    (0, board_size - corner_size),                         # Just Visiting (bottom-left)
    (0, 0),                                                 # Free Parking (top-left)
    (board_size - corner_size, 0)                          # Go To Jail (top-right)
    ]

    for name, (x, y) in zip(corner_names_short, corner_positions):
        label = font.render(name, True, (0, 0, 0))
        label_rect = label.get_rect(center=(x + corner_size // 2, y + corner_size // 2))
        screen.blit(label, label_rect)

    # Bottom-right corner (GO)
    pygame.draw.rect(screen, (0, 0, 0), (corner_positions[0][0], corner_positions[0][1], corner_size, corner_size), 2) 

    # Bottom-left corner (Jail)
    pygame.draw.rect(screen, (0, 0, 0), (corner_positions[1][0], corner_positions[1][1], corner_size, corner_size), 2) 
    
    # Top-left corner (Free Parking)
    pygame.draw.rect(screen, (0, 0, 0), (corner_positions[2][0], corner_positions[2][1], corner_size, corner_size), 2)

    # Top-right corner (Go to Jail)
    pygame.draw.rect(screen, (0, 0, 0), (corner_positions[3][0], corner_positions[3][1], corner_size, corner_size), 2)

    # Bottom row : pygame.draw.rect(left, top, width, height) -> Rectangle
    ## Created Left to right
    for i in range(9):
        idx = i

        ## Starting position is after the bottom left corner 
        x = corner_size + (i) * space_size
        y = board_size - corner_size

        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, corner_size), 2)

        ## Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 40 + space_size // 2))
        screen.blit(label, rect)

    # Left row:
    ## Bottom to top 
    for i in range(9):
        idx = 9 + i
        x = 0
        y = board_size - corner_size - (i + 1) * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, corner_size, space_size), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # Top Row:
    ## Created Left to right
    for i in range(9):
        idx = 18 + i
        x = corner_size + i * space_size
        y = 0
        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, corner_size), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)


    # right row:
    ## Top to Bottom
    for i in range(9):
        idx = 27 + i
        x = board_size - corner_size
        y = corner_size + i * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, corner_size, space_size,), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 40 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

def create_board():
    running = True
    while running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ## Get the screen width and height for proper space creation
        screen_width, screen_height = pygame.display.get_surface().get_size()

        board_game(screen_width, screen_height)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    create_board()
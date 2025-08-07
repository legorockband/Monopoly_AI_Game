#board.py
# reference link : https://www.pygame.org/docs/
import pygame
import ctypes
import os
import sys

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
## (<Name>, <Cost for Property>, <Color of Property: (R, G, B)>)
spaces_names_2 = [
    ("MA", "$60", (150, 75, 0)), ("CC", None, None), ("BA", "$60", (150, 75, 0)), ("Tax", "Pay $200", None), ("RR", "$200", None), ("OA", "$100", (173, 216, 230)), ("Ch", None, None), ("VA", "$100", (173, 216, 230)), ("CA", "$120", (173, 216, 230)),     # Bottom row (0–8)
    ("SCP", "$140", (255, 0, 255)), ("EC", "$150", None), ("SA", "$140", (255, 0, 255)), ("VA", "$160", (255, 0, 255)), ("PRR", "$200", None), ("SJP", "$180", (255, 165, 0)), ("CC", None, None), ("TA", "$180", (255, 165, 0)), ("NYA", "$200", (255, 165, 0)),  # Left row (9–17)
    ("KA", "$220", (255, 0, 0)), ("Ch", None, None), ("IA", "$220", (255, 0, 0)), ("ILA", "$240", (255, 0, 0)), ("B&O", "$200", None), ("AA", "$260", (255, 255, 0)), ("VA", "$260", (255, 255, 0)), ("WW", "$150", None), ("MG", "$280", (255, 255, 0)),   # Top row (18–26)
    ("PA", "$300", (0, 255, 0)), ("NCA", "$300", (0, 255, 0)), ("CC", None, None), ("PAA", "$320", (0, 255, 0)), ("SL", "$200", None), ("Ch", None, None), ("PP", "$350", (0, 0, 139)), ("LT", "Pay $100", None), ("BW", "$400", (0, 0, 139))     # Right row (27–35)
]

corner_names_short = [
    "GO", "Just Visiting", "Free Parking", "Go To Jail"
]

def board_game(screen, font, board_size:int, corner_size:int, space_size:int):
    screen.fill((255, 255, 255))

    color_size = corner_size // 4

    corner_positions = [
    (board_size - corner_size, board_size - corner_size),  # GO (bottom-right)
    (0, board_size - corner_size),                         # Just Visiting (bottom-left)
    (0, 0),                                                 # Free Parking (top-left)
    (board_size - corner_size, 0)                          # Go To Jail (top-right)
    ]

    ## Display the corner text
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

    # Bottom row: Created Left to right
    for i in range(9):
        idx = i

        ## Starting position is after the bottom left corner 
        x = corner_size + (i) * space_size
        y = board_size - corner_size

        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, corner_size), 2)

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y, space_size, color_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y, space_size, color_size), 2) ## Border for the color square 

        ## Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 40 + space_size // 2))
        screen.blit(label, rect)

        ## Label for the cost of the property
        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 60 + space_size // 2))
        screen.blit(label, rect)

    # Left row: Bottom to top 
    for i in range(9):
        idx = 9 + i
        x = 0
        y = board_size - corner_size - (i + 1) * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, corner_size, space_size), 2)

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x + corner_size - color_size, y, color_size, space_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x + corner_size - color_size, y, color_size, space_size), 2) ## Border for the color square 

        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 30 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x  - 15 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # Top Row: Created Left to right
    for i in range(9):
        idx = 18 + i
        x = corner_size + i * space_size
        y = 0
        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, corner_size), 2)

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y + corner_size - color_size, space_size, color_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y + corner_size - color_size, space_size, color_size), 2) ## Border for the color square 

        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 15 + space_size // 2))
        screen.blit(label, rect)

        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y - 15 + space_size // 2))
        screen.blit(label, rect)

    # Right row: Top to Bottom
    for i in range(9):
        idx = 27 + i
        x = board_size - corner_size
        y = corner_size + i * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, corner_size, space_size,), 2)

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y, color_size, space_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y, color_size, space_size), 2) ## Border for the color square 

        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 30 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 60 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

def getPlayerPos(pos:int, board_size:int, corner_size:int, space_size:int):
    if pos == 0:            # GO
        x = board_size - corner_size
        y = board_size - corner_size

    elif 1 <= pos <= 9:     # Bottom row (Right to Left)
        x = board_size - corner_size - pos * space_size
        y = board_size - corner_size
    
    elif pos == 10:         # Just Visiting
        x = 0
        y = board_size - corner_size

    elif 11 <= pos <= 19:   # Left column (Bottom to Top)
        x = 0
        y = board_size - corner_size - (pos - 10) * space_size

    elif pos == 20:         # Free Parking
        x = 0
        y = 0

    elif 21 <= pos <= 29:   # Top row (Left to Right)
        x = corner_size + (pos - 21) * space_size
        y = 0

    elif pos == 30:         # Go To Jail
        x = board_size - corner_size
        y = 0

    elif 31 <= pos <= 39:   # Right column (Top to Bottom)
        x = board_size - corner_size
        y = corner_size + (pos - 31) * space_size   

    else:
        raise ValueError("Invalid Position on Board")
        
    return (x + 10, y + 10)  # slight offset for visual padding

## current_pos = [player1_pos, player2_pos, player3_pos, player4_pos]
def move_player(screen, players, board_size:int, corner_size:int, space_size:int):
    for idx, player in enumerate(players):
        x, y = getPlayerPos(player.position, board_size, corner_size, space_size)
        pygame.draw.rect(screen, player.color, (x + idx * 10, y + idx * 10, 20, 20))  # offset to avoid overlap
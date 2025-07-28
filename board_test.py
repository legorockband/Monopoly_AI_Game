#board.py
# reference link : https://www.pygame.org/docs/
import pygame
import sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1400,850))
clock = pygame.time.Clock()

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


def board_game():
    screen.fill((255, 255, 255))
    space_size = 62
    corner_size = 122
    side_space_height = 80

    # text
    for i in range(9):
        x = 120 + i * space_size
        y = 800 - space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, space_size), 2)

        name = spaces_names_2[i+1]
        label = font.render(name, True, (0,0,0))
        text_rect = label.get_rect(center=(x+space_size // 2, y + space_size // 2))
        screen.blit(label, text_rect)

  

    #bottom right
    pygame.draw.rect(screen, (0, 0, 0), (800 - corner_size, 800 - corner_size, corner_size, corner_size), 2)

    #bottom left
    pygame.draw.rect(screen, (0, 0, 0), (0, 800 - corner_size, corner_size, corner_size), 2)

    #top left
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, corner_size, corner_size), 2)

    #top right
    pygame.draw.rect(screen, (0, 0, 0), (800 - corner_size, 0, corner_size, corner_size), 2)

    # Bottom row : pygame.draw.rect(left, top, width, height) -> Rectangle
    for i in range(9):
        idx = i + 1
        x = 120 + i * space_size
        y = 800 - space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, space_size), 2)
        go_label = font.render(spaces_names_2[0], True, (0,0,0))
        go_rect = go_label.get_rect(center=(800-corner_size // 2, 800 - corner_size // 2))
        screen.blit(go_label, go_rect)

    for i, pos in zip([10, 20, 30], [(corner_size // 2, 800 - corner_size // 2), (corner_size // 2, corner_size // 2), (800 - corner_size // 2, corner_size // 2)]):
        label = font.render(spaces_names_2[i], True, (0, 0, 0))
        rect = label.get_rect(center=pos)
        screen.blit(label, rect)

    # Top Row:
    for i in range(9):
        idx = 19 + (8-i)
        x = corner_size + i * space_size
        y = 0
        pygame.draw.rect(screen, (0,0,0), (x, y, space_size, space_size), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # left row:
    for i in range(9):
        idx = 10 + i
        x = 0
        y = corner_size + i * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, side_space_height, space_size), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # right row:
    for i in range(9):
        idx = 28 + i
        x = 800 - space_size
        y = corner_size + i * space_size
        pygame.draw.rect(screen, (0,0,0), (x, y, side_space_height, space_size,), 2)
        label = font.render(spaces_names_2[idx], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

def create_board():
    running = True
    while running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        board_game()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    create_board()
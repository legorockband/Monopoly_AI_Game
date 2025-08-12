import pygame
from game_test import Player, Property, Railroad, Utility

COLOR_ORDER = [
    (150, 75, 0),    # Brown
    (173, 216, 230), # Light Blue
    (255, 0, 255),   # Pink (Magenta)
    (255, 165, 0),   # Orange
    (255, 0, 0),     # Red
    (255, 255, 0),   # Yellow
    (0, 255, 0),     # Green
    (0, 0, 139),     # Dark Blue
]

COLOR_INDEX = {rgb: i for i, rgb in enumerate(COLOR_ORDER)}

card_font = pygame.font.SysFont(None, 24)
value_font = pygame.font.SysFont('Arial', 30)

def owned_prop_sort_key(s):
    # Properties first, by color order, then board index (stable)
    if isinstance(s, Property):
        return (0, COLOR_INDEX.get(s.color_group, 99), getattr(s, "index", 999))
    # Railroads after properties
    if isinstance(s, Railroad):
        return (1, 0, getattr(s, "index", 999))
    # Utilities after railroads
    if isinstance(s, Utility):
        return (2, 0, getattr(s, "index", 999))
    # Fallback
    return (3, 0, getattr(s, "index", 999))

# def adjust_text_color(rgb):
#     r, g, b = rgb
#     brightness = (r + g + b) / 3
#     if brightness > 200:  # if it's very bright, darken it
#         factor = 0.7
#         return (int(r * factor), int(g * factor), int(b * factor))
#     return rgb

def prop_text_color(space):
    if isinstance(space, Property):
        return space.color_group
    if isinstance(space, Railroad):
        return (30, 30, 30)     # dark gray/black
    if isinstance(space, Utility):
        return (0, 0, 0)        # black
    return (0, 0, 0)

def create_player_card(screen: pygame.Surface, player:list[Player], player_idx:int, board_size: int, space_size: int, screen_width: int, screen_height: int):
    card_width = screen_width - board_size
    card_height = space_size * 3
    starting_pos = 475

    current_player = player[player_idx]
    money_value = current_player.money
    property_owned = current_player.properties_owned    # List of all properties owned by the current player

    # Sort the properties by the color 
    property_owned.sort(key=owned_prop_sort_key)

    # Large card for the current 
    pygame.draw.rect(screen, (100,100,100), (board_size, starting_pos, card_width, card_height))
    
    # Current Players Turn
    turn_text = value_font.render(f"{current_player.name}'s Turn", True, current_player.color)
    screen.blit(turn_text, (board_size + 10, starting_pos))

    # Money Total for the current player
    money_text = card_font.render(f"- Money: ${money_value}", True, (0, 255, 0))
    screen.blit(money_text, (board_size + 10, starting_pos + 45))
    
    # Render properties in columns
    line_h = 20  # vertical spacing
    padding_top = 75
    light_padding_top = 15
    padding_left = 10

    col = 0
    row = 0

    max_rows = 7  
    max_row_next_col = 10

    for prop in property_owned:
        if col == 0 and row >= max_rows:
            # move to next column
            col += 1
            row = 0
        elif col >= 1 and row >= max_row_next_col:
            # move to next column
            col += 1
            row = 0

        text_color = prop_text_color(prop)
        line_text = card_font.render(f"- {prop.name}", True, text_color)

        # Calculate position based on col/row
        x = board_size + padding_left + col * 220  # 200 px per column
        if col >= 1:
            y = starting_pos + light_padding_top + row * line_h 
        else:
            y = starting_pos + padding_top + row * line_h

        screen.blit(line_text, (x, y))

        row += 1

    # Make smaller cards below the big one 

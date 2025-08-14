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
    (0, 0, 0),       # Railroads
    (255, 255, 200)  # Utilies 
]

COLOR_INDEX = {rgb: i for i, rgb in enumerate(COLOR_ORDER)}

card_font = pygame.font.SysFont(None, 24)
money_font = pygame.font.SysFont('Arial', 26)
value_font = pygame.font.SysFont('Arial', 28)


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

def prop_text_color(space):
    if isinstance(space, Property):
        return space.color_group
    if isinstance(space, Railroad):
        return (30, 30, 30)     # dark gray/black
    if isinstance(space, Utility):
        return (0, 0, 0)        # black
    return (0, 0, 0)

SQUARE_SIZE = 11
SQUARE_GAP = 4        # gap between squares within the same color group
GROUP_GAP = 10        # extra gap between different color groups

def count_owned_items(properties):
    """Return a list of (type, color, count) in COLOR_ORDER order."""
    counts_list = []
    for color in COLOR_ORDER:
        # Detect type based on color
        if color == (0, 0, 0):
            count = sum(1 for p in properties if isinstance(p, Railroad))
            item_type = "railroad"
        elif color == (255, 255, 200):
            count = sum(1 for p in properties if isinstance(p, Utility))
            item_type = "utility"
        else:
            count = sum(1 for p in properties if isinstance(p, Property) and getattr(p, "color_group", None) == color)
            item_type = "property"

        if count > 0:
            counts_list.append((item_type, color, count))

    return counts_list

def draw_owned_icons(surface, start_x, start_y, max_width, owned_counts):
    """
    Draws shapes for each owned group.
    - Property: colored square
    - Railroad: black square
    - Utility: light yellow triangle
    """
    x = start_x
    y = start_y
    line_height = SQUARE_SIZE + SQUARE_GAP

    for item_type, color, count in owned_counts:
        for _ in range(count):
            if x + SQUARE_SIZE > start_x + max_width:
                x = start_x
                y += line_height

            if item_type == "utility":
                # Draw triangle
                points = [
                    (x + SQUARE_SIZE // 2, y),                  # top
                    (x, y + SQUARE_SIZE),                       # bottom-left
                    (x + SQUARE_SIZE, y + SQUARE_SIZE)           # bottom-right
                ]
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, (20, 20, 20), points, 1)  # border
            else:
                # Square (properties + railroads)
                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(surface, (20, 20, 20), (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)

            x += SQUARE_SIZE + SQUARE_GAP

        x += GROUP_GAP
        if x + SQUARE_SIZE > start_x + max_width:
            x = start_x
            y += line_height

def create_player_card(screen: pygame.Surface, player:list[Player], player_idx:int, board_size: int, space_size: int, screen_width: int, screen_height: int):
    card_width = screen_width - board_size
    card_height = space_size * 3
    starting_yPos = 475

    small_card_width = card_width// (len(player) - 1)
    small_card_height = screen_height - starting_yPos - card_height
    starting_small_yPos = starting_yPos + card_height

    current_player = player[player_idx]
    money_value = current_player.money
    property_owned = current_player.properties_owned    # List of all properties owned by the current player

    # Sort the properties by the color 
    property_owned.sort(key=owned_prop_sort_key)

    # Large card for the current 
    pygame.draw.rect(screen, (100,100,100), (board_size, starting_yPos, card_width, card_height))
    
    # Current Players Turn
    turn_text = value_font.render(f"{current_player.name}'s Turn", True, current_player.color)
    screen.blit(turn_text, (board_size + 10, starting_yPos - 35))

    # Money Total for the current player
    money_text = money_font.render(f"- Money: ${money_value}", True, (0, 255, 0))
    screen.blit(money_text, (board_size + 10, starting_yPos + 10))
    
    # Render properties in columns
    line_h = 20  # vertical spacing
    padding_top = 45
    light_padding_top = 10
    padding_left = 10

    col = 0
    row = 0

    max_rows = 8  
    max_row_next_col = 10

    for prop in property_owned:
        if col == 0 and row >= max_rows:
            # Move to next column
            col += 1
            row = 0
        elif col >= 1 and row >= max_row_next_col:
            # Move to next column
            col += 1
            row = 0

        text_color = prop_text_color(prop)
        line_text = card_font.render(f"- {prop.name}", True, text_color)

        # Calculate position based on col/row
        x = board_size + padding_left + col * 220  # 200 px per column
        if col >= 1:
            y = starting_yPos + light_padding_top + row * line_h 
        else:
            y = starting_yPos + padding_top + row * line_h

        screen.blit(line_text, (x, y))

        row += 1

    # Make smaller cards below the big one for every other player
    for i in range(1, len(player)):
        pygame.draw.rect(screen, (100, 100, 100), (board_size + small_card_width * (i - 1), starting_small_yPos, small_card_width + 3, small_card_height), 2)
        next_player = player[(player_idx + i) % len(player)]
        next_money = next_player.money
        next_player_text = value_font.render(f"{next_player.name}", True, next_player.color)
        screen.blit(next_player_text, (board_size + small_card_width * (i- 1) + 10, starting_small_yPos))   

        money_text = card_font.render(f"${next_money}", True, (0, 255, 0))
        screen.blit(money_text, (board_size + small_card_width * (i- 1) + 10, starting_small_yPos + 45))   

        property_owned = next_player.properties_owned  

        # Sort the properties by the color 
        property_owned.sort(key=owned_prop_sort_key)

        # Colored squares for owned properties (by color set) 
        squares_area_x = board_size + small_card_width * (i - 1) + 10
        squares_area_y = starting_small_yPos + 75
        squares_area_w = small_card_width - 20

        # Count only actual color properties (ignore railroads/utilities)
        color_counts = count_owned_items(property_owned)

        draw_owned_icons(
            screen,
            squares_area_x,
            squares_area_y,
            squares_area_w,
            color_counts
        )


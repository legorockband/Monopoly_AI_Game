#board.py
# reference link : https://www.pygame.org/docs/
import pygame
from game_test import Card

spaces_names = [
    "MEDITERRANEAN AVENUE", "COMMUNITY CHEST", "BALTIC AVENUE", "INCOME TAX", "READING RAILROAD", "ORIENTAL AVENUE", "CHANCE", "VERTMONT AVENUE", "CONNETICUT AVENUE", 
    "ST. CHARLES PLACE","ELECTRIC COMPANY", "STATES AVENUE", "VIRGINIA AVENUE", "PENNSYLVANIA RAILROAD", "ST. JAMES PLACE", "COMMUNITY CHEST", "TENNESSEE AVENUE", "NEW YORK AVENUE", 
    "KENTUCKY AVENUCE", "CHANCE", "INDIANA AVENUE", "ILLIONOIS AVENUE","B. & O. RAILROAD", "ATLANTIC AVENUE", "VENTNOR AVENUE", "WATER WORKS","MARVIN GARDENS", 
    "PACIFIC AVENUE", "NORTH CAROLINA AVENUE", "COMMUNITY CHEST","PENNSYLVANIA AVENUE", "SHORT LINE RAILROAD", "CHANCE", "PARK PLACE", "LUXURY TAX","BOARDWALK"
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
    space_rects= {}         # Contains all of the positons for the properties 
    # space_rects[0] = None 
    # space_rects[10] = None
    # space_rects[20] = None
    # space_rects[30] = None

    color_size = corner_size // 4

    corner_positions = [
        (board_size - corner_size, board_size - corner_size),  # GO (bottom-right)
        (0, board_size - corner_size),                         # Just Visiting (bottom-left)
        (0, 0),                                                # Free Parking (top-left)
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

    # Bottom row: Right to Left
    for idx in range(9):
        x = board_size - corner_size - (idx + 1) * space_size
        y = board_size - corner_size

        rect = pygame.Rect(x, y, space_size, corner_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)

        # Save position of the current sqaure 
        space_rects[1 + idx] = rect

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y, space_size, color_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y, space_size, color_size), 2) ## Border for the color square 

        # Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 40 + space_size // 2))
        screen.blit(label, rect)

        # Label for the cost of the property
        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 60 + space_size // 2))
        screen.blit(label, rect)

    # Left row: Bottom to top 
    for i in range(9):
        idx = 9 + i
        x = 0
        y = board_size - corner_size - (i + 1) * space_size
        rect = pygame.Rect(x, y, corner_size, space_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)

        # Save position of the current sqaure 
        space_rects[2 + idx] = rect

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x + corner_size - color_size, y, color_size, space_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x + corner_size - color_size, y, color_size, space_size), 2) ## Border for the color square 

        # Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 30 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

        # Label for the cost of the property
        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x  - 15 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # Top Row: Left to right
    for i in range(9):
        idx = 18 + i
        x = corner_size + i * space_size
        y = 0
        rect = pygame.Rect(x, y, space_size, corner_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)

        # Save position of the current sqaure 
        space_rects[3 + idx] = rect

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y + corner_size - color_size, space_size, color_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y + corner_size - color_size, space_size, color_size), 2) ## Border for the color square 
        
        # Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y + 15 + space_size // 2))
        screen.blit(label, rect)
        
        # Label for the cost of the property
        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + space_size // 2, y - 15 + space_size // 2))
        screen.blit(label, rect)

    # Right row: Top to Bottom
    for i in range(9):
        idx = 27 + i
        x = board_size - corner_size
        y = corner_size + i * space_size
        rect = pygame.Rect(x, y, corner_size, space_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        
        # Save position of the current sqaure 
        space_rects[4 + idx] = rect

        color_value = spaces_names_2[idx][2]

        if color_value != None: 
            pygame.draw.rect(screen, color_value, (x, y, color_size, space_size))  ## Color square
            pygame.draw.rect(screen, (0, 0, 0), (x, y, color_size, space_size), 2) ## Border for the color square 

        # Label All the Properties starting after Go and ending before Just Visting
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 25 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

        # Label for the cost of the property
        label = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        rect = label.get_rect(center=(x + 60 + space_size // 2, y + space_size // 2))
        screen.blit(label, rect)

    # Draw the visual decks for the chance and community chest cards
    draw_center_decks(screen, board_size, corner_size)
    return space_rects

def draw_card_deck(screen, center, size, angle, title, title_color, accent_color):
    """Draw a tilted card deck at center (cx, cy)."""
    cen_x, cen_y = center
    width, height = size

    # Make a surface with per‑pixel alpha so rotation keeps transparency
    surf = pygame.Surface((width, width), pygame.SRCALPHA)

    # Card background
    bg = (255, 255, 224)     # light parchment
    border = (0, 0, 0)
    pygame.draw.rect(surf, bg, (0, 0, width, height), border_radius=10)
    pygame.draw.rect(surf, border, (0, 0, width, height), 2, border_radius=10)

    # A simple “stack” hint (a smaller rectangle at top-left)
    pygame.draw.rect(surf, (245, 245, 210), (6, 6, width-12, height-12), border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0), (6, 6, width-12, height-12), 1, border_radius=8)

    # Title
    title_font = pygame.font.SysFont("Arial", 18, bold=True)
    title_surf = title_font.render(title, True, title_color)
    surf.blit(title_surf, ((width - title_surf.get_width()) // 2, 10))

    # Simple icon (question mark for Chance or a chest-ish box)
    icon_y = height // 2 - 8
    if "CHANCE" in title.upper():
        # Question mark
        q_font = pygame.font.SysFont("Arial", 44, bold=True)
        q = q_font.render("?", True, accent_color)
        surf.blit(q, ((width - q.get_width()) // 2, icon_y))
    else:
        # A little chest: base box + “hinge” line + lock
        box_rect = pygame.Rect(width//2 - 35, icon_y, 70, 40)
        pygame.draw.rect(surf, accent_color, box_rect, border_radius=6)
        pygame.draw.rect(surf, (0, 0, 0), box_rect, 2, border_radius=6)
        pygame.draw.line(surf, (0, 0, 0), (box_rect.left+8, box_rect.top+14), (box_rect.right-8, box_rect.top+14), 2)
        # lock
        pygame.draw.circle(surf, (0, 0, 0), (width//2, box_rect.centery+6), 5, 2)
        pygame.draw.rect(surf, (0, 0, 0), (width//2-2, box_rect.centery+6, 4, 8))

    # “Deck” thickness shadow
    shadow = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 40), (3, 3, width, height), border_radius=10)
    surf.blit(shadow, (0, 0))

    # Rotate and blit
    rotated = pygame.transform.rotate(surf, angle)
    rect = rotated.get_rect(center=(cen_x, cen_y))
    screen.blit(rotated, rect)

def draw_center_decks(screen, board_size, corner_size):
    """Draw only one Community Chest (upper-left) and one Chance (lower-right) in the center."""
    inner = pygame.Rect(corner_size, corner_size, board_size - 2*corner_size, board_size - 2*corner_size)

    pad = max(12, board_size // 60)
    card_size = (160, 105)  # width, height

    # Upper-left inner corner → Community Chest
    chest_pos = (inner.left + pad + 100, inner.top + pad + 100)
    draw_card_deck(screen, chest_pos, card_size, 45, "COMMUNITY CHEST", (0, 0, 0), (70, 130, 180))

    # Lower-right inner corner → Chance
    chance_pos = (inner.right - pad - 60, inner.bottom - pad - 60)
    draw_card_deck(screen, chance_pos, card_size, 45, "CHANCE", (0, 0, 0), (255, 140, 0))

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

def move_player(screen, players, board_size:int, corner_size:int, space_size:int):
    for idx, player in enumerate(players):
        x, y = getPlayerPos(player.position, board_size, corner_size, space_size)
        pygame.draw.rect(screen, player.color, (x + idx * 10, y + idx * 10, 20, 20))  # offset to avoid overlap

def display_card(screen, current_player, card, board_size, screen_height):
    card_width = 200
    card_height = 250
    card_x = board_size // 2 - card_width // 2
    card_y = screen_height // 2 - card_height // 2

    # Draw card background and border
    pygame.draw.rect(screen, (255, 255, 224), (card_x, card_y, card_width, card_height))  # Light yellow
    pygame.draw.rect(screen, (0, 0, 0), (card_x, card_y, card_width, card_height), 2)

    # Card Title 
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    descript_font = pygame.font.SysFont(None, 25)
    title_text = title_font.render(card.card_type.upper(), True, (0, 0, 0))
    screen.blit(title_text, (card_x + (card_width - title_text.get_width()) // 2, card_y + 10))

    # Card description 
    description_lines = wrap_text(card.description, descript_font, card_width - 20)
    for i, line in enumerate(description_lines):
        line_surface = descript_font.render(line, True, (0, 0, 0))
        screen.blit(line_surface, (card_x + 10, card_y + 50 + i * 22))

    # Show which player needs to do certain action
    player_text = descript_font.render(f"{current_player.name}", True, current_player.color)
    screen.blit(player_text, (card_x + (card_width - title_text.get_width()) // 2, card_y + card_height - 25))

def wrap_text(text, font, max_width):
    # Breaks text into lines that fit within max_width
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    return lines

def property_characteristic(screen, space, board_size, screen_height):
    ## When click on a property create a simple card display to show the rent and cost of houses/hotels etc
    
    card_width = 360
    card_height = 420
    card_x = board_size // 2 - card_width // 2
    card_y = screen_height // 2 - card_height // 2

    # Draw card background and border
    pygame.draw.rect(screen, (255, 255, 224), (card_x, card_y, card_width, card_height))  # Light yellow
    pygame.draw.rect(screen, (0, 0, 0), (card_x, card_y, card_width, card_height), 2)

    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    body_font  = pygame.font.SysFont(None, 22)
    mono_font  = pygame.font.SysFont("Courier New", 20)

    def line(y, text, color=(0,0,0), font=body_font):
        surf = font.render(text, True, color)
        screen.blit(surf, (card_x + 16, y))
        return y + surf.get_height() + 8

    y = card_y + 12
    # Title
    y = line(y, getattr(space, "name", "Space"), font=title_font)

    # Only show details for purchasable types
    stype = getattr(space, "type", "")
    if stype not in ("Property", "Railroad", "Utility"):
        y = line(y+6, "Not purchasable.", (120,0,0))
        return

    owner = getattr(space, "owner", None)
    if owner is None:
        y = line(y, "Owner: Unowned", (150, 0, 0))  
    else:
        owner_color = getattr(owner, "color", (0, 0, 0))
        owner_name  = getattr(owner, "name", "Unknown")
        y = line(y, f"Owner: {owner_name}", owner_color)

    # Common: cost & mortgage if available
    cost = getattr(space, "cost", None)
    if cost is not None:
        y = line(y+6, f"Purchase Cost: ${cost}")
    mort = getattr(space, "mortgage_value", None)
    if mort is not None:
        y = line(y,   f"Mortgage Value: ${mort}")

    if stype == "Property":
        # Uses rent_values: [base, 1 house, 2, 3, 4, hotel] and house_cost:contentReference[oaicite:3]{index=3}
        rents = getattr(space, "rent_values", [])
        house_cost = getattr(space, "house_cost", None)

        if rents:
            base = rents[0]
            y = line(y+10, "Rent (Unimproved):", (0,0,0), body_font)
            y = line(y, f"- No Monopoly: ${base}", font=mono_font)
            y = line(y, f"- With Monopoly: ${base*2}", font=mono_font)  # monopoly doubles base rent:contentReference[oaicite:4]{index=4}

            # Houses & hotel
            labels = ["1 House","2 Houses","3 Houses","4 Houses","Hotel"]
            y = line(y+5, "Rent with Houses/Hotel:", (0,0,0), body_font)
            for i, lbl in enumerate(labels, start=1):
                if i < len(rents):
                    y = line(y, f"- {lbl}: ${rents[i]}", font=mono_font)

        if house_cost is not None:
            y = line(y- 3, f"Cost per House: ${house_cost}", font=mono_font)

    elif stype == "Railroad":
        # Rent based on number of railroads owned:contentReference[oaicite:5]{index=5}
        y = line(y+10, "Rent by Railroads Owned:", (0,0,0), body_font)
        y = line(y, "- Owns 1: $25",  font=mono_font)
        y = line(y, "- Owns 2: $50",  font=mono_font)
        y = line(y, "- Owns 3: $100", font=mono_font)
        y = line(y, "- Owns 4: $200", font=mono_font)

    elif stype == "Utility":
        # Rent is 4× or 10× the dice sum depending on utilities owned:contentReference[oaicite:6]{index=6}
        y = line(y+10, "Rent Formula:", (0,0,0), body_font)
        y = line(y, "- Owns 1 Utility: 4 x dice sum",  font=mono_font)
        y = line(y, "- Owns 2 Utilities: 10 x dice sum", font=mono_font)

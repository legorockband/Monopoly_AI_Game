#board.py
# reference link : https://www.pygame.org/docs/
import pygame
from game_test import Game

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

def edge_for_pos(pos:int) -> str:
    """Which board edge does this position live on? ('bottom','left','top','right','corner')"""
    if pos in (0, 10, 20, 30):
        return "corner"
    if 1  <= pos <= 9:   return "bottom"
    if 11 <= pos <= 19:  return "left"
    if 21 <= pos <= 29:  return "top"
    if 31 <= pos <= 39:  return "right"
    raise ValueError("Invalid position")

def tile_center(pos:int, board_size:int, corner_size:int, space_size:int) -> tuple[int,int]:
    """Center (cx,cy) of the tile rect for a given board position."""
    if pos == 0:                # GO
        x = board_size - corner_size; y = board_size - corner_size + 25
        return x + corner_size//2, y + corner_size//2
    elif 1 <= pos <= 9:         # bottom (right -> left)
        x = board_size - corner_size - pos * space_size
        y = board_size - corner_size + 25
        return x + space_size//2, y + corner_size//2
    elif pos == 10:             # Jail / Just Visiting
        x = 0; y = board_size - corner_size + 25
        return x + corner_size//2, y + corner_size//2
    elif 11 <= pos <= 19:       # left (bottom -> top)
        x = 0
        y = board_size - corner_size - (pos - 10) * space_size
        return x + corner_size//2, y + space_size//2
    elif pos == 20:             # Free Parking
        x = 0; y = 0
        return x + corner_size//2, y + corner_size//2
    elif 21 <= pos <= 29:       # top (left -> right)
        x = corner_size + (pos - 21) * space_size
        y = 0
        return x + space_size//2, y + corner_size//2
    elif pos == 30:             # Go To Jail
        x = board_size - corner_size; y = 0
        return x + corner_size//2, y + corner_size//2
    elif 31 <= pos <= 39:       # right (top -> bottom)
        x = board_size - corner_size
        y = corner_size + (pos - 31) * space_size
        return x + corner_size//2, y + space_size//2
    else:
        raise ValueError("Invalid Position on Board")

def layout_offsets(n:int, orientation:str, token_size:int=26, gap:int=6):
    """
    Return up to 4 (dx,dy) offsets for n tokens, arranged:
      - orientation 'h' -> horizontal side-by-side
      - orientation 'v' -> vertical top-bottom
    The offsets are relative to the tile center.
    """
    half = token_size//2
    if orientation == 'h':
        # left/right first, then fill a 2x2 if needed
        base = [(-half - gap//2, 0), (half + gap//2, 0), (-half - gap//2, -token_size - gap), (half + gap//2, -token_size - gap)] #Player 1,2,3,4
    else:
        # top/bottom first, then 2x2 if needed
        base = [(0, -half - gap//2), (0,  half + gap//2),
                (-token_size - gap, -half - gap//2), (-token_size - gap,  half + gap//2)]
    return base[:max(1, n)]

def move_player(screen:pygame.Surface, players, board_size:int, corner_size:int, space_size:int):
    """
    Draw player tokens so that when multiple players share a tile:
      - bottom/top rows: tokens sit left/right of each other
      - left/right columns: tokens stack top/bottom
    """
    TOKEN = 26  # square token size
    # group players by board position
    groups = {}
    for p in players:
        groups.setdefault(p.position, []).append(p)

    for pos, group in groups.items():
        cx, cy = tile_center(pos, board_size, corner_size, space_size)
        edge = edge_for_pos(pos)
        # decide orientation
        if edge in ("bottom", "top"):
            orientation = 'h'  # left/right on rows
        elif edge in ("left", "right"):
            orientation = 'v'  # top/bottom on columns
        else:
            # corners: fall back to a neat 2x2
            orientation = 'h'

        offsets = layout_offsets(len(group), orientation, token_size=TOKEN, gap=6)

        # stable order: by player name (or keep input order)
        for (dx, dy), player in zip(offsets, group):
            x = int(cx + dx - TOKEN/2)
            y = int(cy + dy - TOKEN/2)
            pygame.draw.rect(screen, player.color, (x, y, TOKEN, TOKEN))
            # optional thin border for visibility
            pygame.draw.rect(screen, (0,0,0), (x, y, TOKEN, TOKEN), 1)

def display_card(screen:pygame.Surface, current_player, card, board_size, screen_height):
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

def property_characteristic(screen:pygame.Surface, space, board_size, screen_height):
    # When click on a property create a simple card display to show the rent and cost of houses/hotels etc
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
        y = line(y, "- Owns 1: 4 x dice sum",  font=mono_font)
        y = line(y, "- Owns 2: 10 x dice sum", font=mono_font)

def purchase_button_rects(cx, cy):
    w, h = 110, 44
    gap = 30
    buy = pygame.Rect(cx - w - gap//2, cy - h//2, w, h)
    skip = pygame.Rect(cx + gap//2, cy - h//2, w, h)
    return buy, skip

def draw_purchase_modal(screen:pygame.Surface, game, title_font, body_font, center_x, center_y):
    info = game.pending_purchase
    if not info:
        return
    prop = info["property"]
    player = info["player"]
    affordable = info.get("affordable", True)

    # card
    modal_w, modal_h = 360, 220
    x = center_x - modal_w // 2
    y = center_y - modal_h // 2
    pygame.draw.rect(screen, (255, 255, 224), (x, y, modal_w, modal_h))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, modal_w, modal_h), 2)

    # text
    title = title_font.render("Purchase Property?", True, (0,0,0))
    screen.blit(title, (x + (modal_w - title.get_width())//2, y + 10))

    name_text = body_font.render(prop.name, True, (0,0,0))
    cost_text = body_font.render(f"Cost: ${prop.cost}", True, (0,0,0))
    who_text = body_font.render(f"Player: {player.name}", True, (0,0,0))
    screen.blit(name_text, (x + 20, y + 60))
    screen.blit(cost_text, (x + 20, y + 90))
    screen.blit(who_text, (x + 20, y + 120))

    # buttons
    buy_rect, skip_rect = purchase_button_rects(center_x, center_y + 55)
    buy_color = (0,150,0) if affordable else (120,120,120)
    skip_color = (150,0,0)
    pygame.draw.rect(screen, buy_color, buy_rect)
    pygame.draw.rect(screen, skip_color, skip_rect)

    buy_lbl = body_font.render("BUY", True, (255,255,255)) if affordable else body_font.render("CAN'T BUY", True, (255,255,255))
    skip_lbl = body_font.render("SKIP", True, (255,255,255))
    screen.blit(buy_lbl, (buy_rect.centerx - buy_lbl.get_width()//2, buy_rect.centery - buy_lbl.get_height()//2))
    screen.blit(skip_lbl, (skip_rect.centerx - skip_lbl.get_width()//2, skip_rect.centery - skip_lbl.get_height()//2))

def draw_rent_modal(screen:pygame.Surface, game, title_font, body_font, cx, cy):
    info = game.pending_rent
    if not info: return
    p, o, prop, amt = info["player"], info["owner"], info["property"], info["amount"]

    w,h = 360, 200
    x,y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    t = title_font.render("Rent Due", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+10))
    a = body_font.render(f"{p.name} landed on {prop.name}", True, (0,0,0))
    b = body_font.render(f"Owes ${amt} to {o.name}", True, (0,0,0))
    screen.blit(a, (x+20, y+60)); screen.blit(b, (x+20, y+90))

    pay_rect = pygame.Rect(cx-55, cy+30, 110, 44)
    pygame.draw.rect(screen, (0,120,200), pay_rect)
    pay_lbl = body_font.render("PAY", True, (255,255,255))
    screen.blit(pay_lbl, (pay_rect.centerx - pay_lbl.get_width()//2,
                          pay_rect.centery - pay_lbl.get_height()//2))
    return pay_rect

def draw_build_modal(screen:pygame.Surface, game, title_font, body_font, cx, cy):
    info = game.pending_build
    if not info: return None, None, None
    prop = info["property"]; player = info["player"]
    can_house = info["can_house"]; can_hotel = info["can_hotel"]

    # Main card
    w,h = 420, 240
    x,y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    # Text on card
    t = title_font.render("Build on Your Property?", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+10))
    a = body_font.render(f"{prop.name}", True, (0,0,0))
    b = body_font.render(f"Houses: {prop.num_houses}  Hotel: {'Yes' if prop.has_hotel else 'No'}", True, (0,0,0))
    c = body_font.render(f"Cost per build: ${prop.house_cost}", True, (0,0,0))
    screen.blit(a, (x+20,y+60)); screen.blit(b,(x+20,y+90)); screen.blit(c,(x+20,y+120))

    # Buttons on card
    r_house = pygame.Rect(cx-180, cy+50, 120, 44)
    r_hotel = pygame.Rect(cx-60,  cy+50, 120, 44)
    r_skip  = pygame.Rect(cx+60,  cy+50, 120, 44)

    pygame.draw.rect(screen, (0,150,0) if can_house else (120,120,120), r_house)
    pygame.draw.rect(screen, (150,100,0) if can_hotel else (120,120,120), r_hotel)
    pygame.draw.rect(screen, (150,0,0), r_skip)

    def center(lbl, rect):
        screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))
    center(body_font.render("BUY HOUSE", True, (255,255,255)), r_house)
    center(body_font.render("BUY HOTEL", True, (255,255,255)), r_hotel)
    center(body_font.render("SKIP", True, (255,255,255)), r_skip)
    return r_house, r_hotel, r_skip

def draw_tax_modal(screen:pygame.Surface, game, title_font, body_font, cx, cy):
    info = game.pending_tax
    if not info: return None
    p = info["player"]; amt = info["amount"]; name = info.get("name", "Tax")

    w,h = 360, 180
    x,y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    t = title_font.render(f"{name}", True, (0,0,0))
    a = body_font.render(f"{p.name} must pay ${amt}", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+10))
    screen.blit(a, (x+20, y+60))

    pay_rect = pygame.Rect(cx-55, cy+30, 110, 44)
    pygame.draw.rect(screen, (0,120,200), pay_rect)
    pay_lbl = body_font.render("PAY", True, (255,255,255))
    screen.blit(pay_lbl, (pay_rect.centerx - pay_lbl.get_width()//2,
                          pay_rect.centery - pay_lbl.get_height()//2))
    return pay_rect

def draw_jail_modal(screen, game, title_font, body_font, cx, cy):
    info = game.pending_jail
    if not info: 
        return None
    p = info["player"]

    w,h = 360, 180
    x,y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    t = title_font.render("GO TO JAIL!", True, (200,0,0))
    a = body_font.render(f"{p.name} has been sent to Jail.", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+10))
    screen.blit(a, (x+20, y+60))

    ok_rect = pygame.Rect(cx-55, cy+30, 110, 44)
    pygame.draw.rect(screen, (0,120,200), ok_rect)
    ok_lbl = body_font.render("OK", True, (255,255,255))
    screen.blit(ok_lbl, (ok_rect.centerx - ok_lbl.get_width()//2,
                         ok_rect.centery - ok_lbl.get_height()//2))
    return ok_rect

def draw_property_build_badges(screen:pygame.Surface, game, space_rects):
    import pygame
    GREEN = (0, 180, 0)   # houses
    RED   = (220, 40, 40) # hotels

    size = 15  # triangle size; tweak to taste
    gap  = 3   # spacing between multiple houses
    pad  = 3   # padding away from the color band

    def side_for_pos(pos:int):
        # Matches how your board indexes map to edges
        if   1  <= pos <= 9:   return "bottom"  # right->left along bottom edge
        elif 11 <= pos <= 19:  return "left"    # bottom->top along left edge
        elif 21 <= pos <= 29:  return "top"     # left->right along top edge
        elif 31 <= pos <= 39:  return "right"   # top->bottom along right edge
        return None

    def tri_points(x, y, s, direction:str):
        # Triangles pointing toward the board interior (apex points toward the color band)
        if direction == "up":     # apex up
            return [(x, y + s), (x + s/2, y), (x + s, y + s)]
        if direction == "down":   # apex down
            return [(x, y), (x + s/2, y + s), (x + s, y)]
        if direction == "left":   # apex left
            return [(x + s, y), (x, y + s/2), (x + s, y + s)]
        if direction == "right":  # apex right
            return [(x, y), (x + s, y + s/2), (x, y + s)]
        raise ValueError("bad direction")

    for pos, rect in space_rects.items():
        sp = game.board.spaces[pos]
        if getattr(sp, "type", "") != "Property": 
            continue
        if getattr(sp, "owner", None) is None:
            continue

        side = side_for_pos(pos)
        if side is None:
            continue

        # Your color band is 1/4 of the short side on each tile — derive per-rect.
        color_size = min(rect.width, rect.height) // 4

        # Compute anchor & orientation so triangles sit just *inside* the band and point toward it.
        if side == "bottom":
            # band along the TOP of the tile; draw just below it, pointing UP
            x0 = rect.left + pad
            y0 = rect.top  + color_size - pad
            if getattr(sp, "has_hotel", True):
                x0 = x0 + color_size
                y0 = y0 - 10
            direction = "up"
            def nth_xy(i):  # lay houses in a row
                return x0 + i * (size + gap), y0

        elif side == "top":
            # band along the BOTTOM of the tile; draw just above it, pointing DOWN
            x0 = rect.left + pad
            y0 = rect.bottom - color_size + pad - size
            if getattr(sp, "has_hotel", True):
                x0 = x0 + color_size
            direction = "down"
            def nth_xy(i):
                return x0 + i * (size + gap), y0

        elif side == "left":
            # band along the RIGHT edge; draw just left of it, pointing RIGHT
            x0 = rect.right - color_size + pad - size
            y0 = rect.top + pad
            if getattr(sp, "has_hotel", True):
                y0 = y0 + color_size
            direction = "right"
            def nth_xy(i):  # stack vertically
                return x0, y0 + i * (size + gap)

        elif side == "right":
            # band along the LEFT edge; draw just right of it, pointing LEFT
            x0 = rect.left + color_size - pad
            y0 = rect.top + pad
            if getattr(sp, "has_hotel", True):
                y0 = y0 + color_size
                x0 = x0 - 10
            direction = "left"
            def nth_xy(i):
                return x0, y0 + i * (size + gap)

        # Draw hotel OR houses
        if getattr(sp, "has_hotel", False):
            # hotels: one red triangle, slightly larger
            s = size + 10
            pts = tri_points(x0, y0, s, direction)
            pygame.draw.polygon(screen, RED, pts)
            pygame.draw.polygon(screen, (0, 0, 0), pts, 1)
            continue

        n = int(getattr(sp, "num_houses", 0))
        for i in range(min(n, 4)):
            xi, yi = nth_xy(i)
            pts = tri_points(xi, yi, size, direction)
            pygame.draw.polygon(screen, GREEN, pts)
            pygame.draw.polygon(screen, (0, 0, 0), pts, 1)

def end_turn_button(screen:pygame.Surface, value_font, center_pos:tuple[int, int], enable:bool=True):
    cx,cy = center_pos
    # Position for the rectangle
    cx = cx + 140
    width = 140
    height = 50 
    end_rect = pygame.Rect(cx, cy, width, height)
    color = (200,0,0) if enable else (160,160,160)  # If you can't end turn, make grey or make red
    pygame.draw.rect(screen, color, end_rect)
    end_turn_text = value_font.render("End Turn", True, (0,0,0))
    screen.blit(end_turn_text, (cx + (width - end_turn_text.get_width())//2, cy + (height - end_turn_text.get_height())//2))
    return end_rect





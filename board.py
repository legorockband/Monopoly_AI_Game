#board.py
# reference link : https://www.pygame.org/docs/
import pygame
from game import Property, Railroad, Utility

def _trade_sort_key(s):
    # Properties first (grouped by board order), then Railroads, then Utilities
    t = 0 if isinstance(s, Property) else 1 if isinstance(s, Railroad) else 2
    return (t, getattr(s, "index", 999))

def _trade_prop_text_color(space):
    if isinstance(space, Property):
        return getattr(space, "color_group", (0,0,0))
    return (30, 30, 30)

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
    "GO", "Just Visiting/Jail", "Free Parking", "Go To Jail"
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
    inner = board_size - 2 * corner_size
    for idx in range(9):
        # default width for a tile
        w = space_size
        # for the LAST tile (next to the jail corner), absorb the leftover pixels
        if idx == 8:
            used = idx * space_size
            w = inner - used  # leftover fits perfectly

        # position this tile flush against the previous one from the right
        # cumulative width up to this tile from the right:
        prior = (idx * space_size) if idx < 8 else (inner - w)
        x = board_size - corner_size - prior - w
        y = board_size - corner_size

        rect = pygame.Rect(x, y, w, corner_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        space_rects[1 + idx] = rect

        color_value = spaces_names_2[idx][2]
        if color_value is not None:
            pygame.draw.rect(screen, color_value, (x, y, w, color_size))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, w, color_size), 2)

        # labels centered in this variable-width tile
        label = font.render(spaces_names_2[idx][0], True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(x + w // 2, y + corner_size // 2 - 10)))
        price = font.render(spaces_names_2[idx][1], True, (0, 0, 0))
        screen.blit(price, price.get_rect(center=(x + w // 2, y + corner_size // 2 + 12)))

    # Left row: Bottom to top
    for i in range(9):
        h = space_size
        if i == 8:
            used = i * space_size
            h = inner - used

        prior = (i * space_size) if i < 8 else (inner - h)
        x = 0
        y = board_size - corner_size - prior - h

        rect = pygame.Rect(x, y, corner_size, h)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        space_rects[2 + (9 + i)] = rect  # positions 11..19

        color_value = spaces_names_2[9 + i][2]
        if color_value is not None:
            band_x = x + corner_size - color_size
            pygame.draw.rect(screen, color_value, (band_x, y, color_size, h))
            pygame.draw.rect(screen, (0, 0, 0), (band_x, y, color_size, h), 2)

        label = font.render(spaces_names_2[9 + i][0], True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(x + corner_size // 2, y + h // 2 - 10)))
        price = font.render(spaces_names_2[9 + i][1], True, (0, 0, 0))
        screen.blit(price, price.get_rect(center=(x + corner_size // 2, y + h // 2 + 12)))

    # Top Row: Left to right
    for i in range(9):
        w = space_size
        if i == 8:
            used = i * space_size
            w = inner - used

        prior = (i * space_size) if i < 8 else (inner - w)
        x = corner_size + prior
        y = 0

        rect = pygame.Rect(x, y, w, corner_size)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        space_rects[3 + (18 + i)] = rect  # positions 21..29

        color_value = spaces_names_2[18 + i][2]
        if color_value is not None:
            band_y = y + corner_size - color_size
            pygame.draw.rect(screen, color_value, (x, band_y, w, color_size))
            pygame.draw.rect(screen, (0, 0, 0), (x, band_y, w, color_size), 2)

        label = font.render(spaces_names_2[18 + i][0], True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(x + w // 2, y + corner_size // 2 - 10)))
        price = font.render(spaces_names_2[18 + i][1], True, (0, 0, 0))
        screen.blit(price, price.get_rect(center=(x + w // 2, y + corner_size // 2 + 12)))

    # Right row: Top to Bottom
    for i in range(9):
        h = space_size
        if i == 8:
            used = i * space_size
            h = inner - used

        prior = (i * space_size) if i < 8 else (inner - h)
        x = board_size - corner_size
        y = corner_size + prior

        rect = pygame.Rect(x, y, corner_size, h)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        space_rects[4 + (27 + i)] = rect  # positions 31..39

        color_value = spaces_names_2[27 + i][2]
        if color_value is not None:
            pygame.draw.rect(screen, color_value, (x, y, color_size, h))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, color_size, h), 2)

        label = font.render(spaces_names_2[27 + i][0], True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(x + corner_size // 2, y + h // 2 - 10)))
        price = font.render(spaces_names_2[27 + i][1], True, (0, 0, 0))
        screen.blit(price, price.get_rect(center=(x + corner_size // 2, y + h // 2 + 12)))

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
        if p is None:                
            continue
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
    card_height = 450
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
    if hasattr(space, "is_mortgaged"):
        y = line(y, f"Mortgaged: {'Yes' if space.is_mortgaged else 'No'}",
            (150,0,0) if space.is_mortgaged else (0,120,0))

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
    can_sell_house = info.get("can_sell_house", False)
    can_sell_hotel = info.get("can_sell_hotel", False)
    can_mortgage   = info.get("can_mortgage", False)
    can_unmortgage = info.get("can_unmortgage", False)

    # Main card
    w,h = 700, 360    
    x,y = cx - w//2, cy - h//2
    but_gap_x = 130
    but_gap_y = 60
    but_x, but_y = cx - 240, cy + 50
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    # Text on card
    t = title_font.render("Manage Buildings", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+10))
    
    a = body_font.render(f"{prop.name}", True, (0,0,0))
    b = body_font.render(f"Houses: {prop.num_houses}  Hotel: {'Yes' if prop.has_hotel else 'No'}", True, (0,0,0))
    c = body_font.render(f"Build/Sell price per step: ${prop.house_cost}", True, (0,0,0))    
    screen.blit(a, (x+20,y+60)); screen.blit(b,(x+20,y+90)); screen.blit(c,(x+20,y+120))
    
    d = body_font.render(f"Mortgaged: {'Yes' if getattr(prop, 'is_mortgaged', False) else 'No'}", True, (150,0,0) if getattr(prop,'is_mortgaged',False) else (0,120,0))
    screen.blit(a, (x+20,y+60)); screen.blit(b, (x+20,y+90)); screen.blit(c, (x+20,y+120)); screen.blit(d, (x+20,y+150))

    house_remain = body_font.render(
        f"Bank: Houses Left {game.houses_remaining}", True, (0,0,0)
    )
    hotel_remain = body_font.render(
        f"Bank: Hotel Left {game.hotels_remaining}", True, (0,0,0)
    )

    screen.blit(house_remain, (x+20, y+180))
    screen.blit(hotel_remain, (x+20, y+180+house_remain.get_height()))

    can_house = can_house and (game.houses_remaining > 0)       # NEW
    can_hotel = can_hotel and (game.hotels_remaining > 0)       # NEW
    can_sell_hotel = can_sell_hotel and (game.houses_remaining >= 4)

    # Buttons on card
    r_house = pygame.Rect(but_x, but_y, 120, 44)
    r_hotel = pygame.Rect(but_x + but_gap_x,  but_y, 120, 44)

    r_sell_house = pygame.Rect(but_x, but_y + but_gap_y, 120, 44)
    r_sell_hotel = pygame.Rect(but_x + but_gap_x,  but_y + but_gap_y, 120, 44)


    pygame.draw.rect(screen, (0,150,0) if can_house else (120,120,120), r_house)
    pygame.draw.rect(screen, (150,100,0) if can_hotel else (120,120,120), r_hotel)
    pygame.draw.rect(screen, (0,120,200) if can_sell_house else (120,120,120), r_sell_house)
    pygame.draw.rect(screen, (0,120,200) if can_sell_hotel else (120,120,120), r_sell_hotel)

    def center(lbl, rect):
        screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))
    center(body_font.render("BUY HOUSE", True, (255,255,255)), r_house)
    center(body_font.render("BUY HOTEL", True, (255,255,255)), r_hotel)
    center(body_font.render("SELL HOUSE",  True, (255,255,255)), r_sell_house)
    center(body_font.render("SELL HOTEL",  True, (255,255,255)), r_sell_hotel)
    
    # Mortgage / Unmortgage buttons
    r_mortgage   = pygame.Rect(but_x + 2 * but_gap_x,  but_y, 140, 44)
    r_unmortgage = pygame.Rect(but_x + 2 * but_gap_x,  but_y + but_gap_y, 140, 44)

    pygame.draw.rect(screen, (120,120,120) if not can_mortgage else (180,70,0), r_mortgage)
    pygame.draw.rect(screen, (120,120,120) if not can_unmortgage else (0,150,0), r_unmortgage)
    center(body_font.render("MORTGAGE",   True, (255,255,255)), r_mortgage)
    center(body_font.render("UNMORTGAGE", True, (255,255,255)), r_unmortgage)

    # Skip button on the right
    r_skip  = pygame.Rect(cx+220, cy+80, 120, 44)
    pygame.draw.rect(screen, (150,0,0), r_skip)
    center(body_font.render("SKIP", True, (255,255,255)), r_skip)

    # return all rects a caller might need
    return {
        "buy_house": r_house,
        "buy_hotel": r_hotel,
        "sell_house": r_sell_house,
        "sell_hotel": r_sell_hotel,
        "mortgage": r_mortgage,
        "unmortgage": r_unmortgage,
        "skip": r_skip,
    }

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

def trade_button(screen, value_font, center_pos, enable=True):
    """Draw a 'Trade' button directly ABOVE End Turn and return its rect."""
    cx, cy = center_pos
    cx = cx + 230
    # End Turn is +30; its height is 50. Put Trade one height (50) above with a tidy gap.
    cy = cy - 30
    w, h = 140, 50
    r = pygame.Rect(cx, cy, w, h)
    color = (0, 120, 200) if enable else (160,160,160)
    pygame.draw.rect(screen, color, r)
    lbl = value_font.render("Trade", True, (0,0,0))
    screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))
    return r

def manage_button(screen, value_font, center_pos, enable=True):
    """Draw a 'Manage' button above Trade; returns its rect."""
    cx, cy = center_pos
    cx = cx + 230
    cy = cy - 90  # stack above Trade/End Turn
    w, h = 140, 50
    r = pygame.Rect(cx, cy, w, h)
    color = (0, 120, 200) if enable else (160,160,160)
    pygame.draw.rect(screen, color, r)
    lbl = value_font.render("Manage", True, (0,0,0))
    screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))
    return r

def draw_manage_select_modal(screen, player, board, cx, cy):
    """
    Modal: pick one of the current player's owned properties to manage.
    Returns (prop_btn_rects:list[(Rect, property_obj)], cancel_rect:Rect)
    """
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    body_font  = pygame.font.SysFont(None, 22)

    # Shell
    W, H = 770, 660
    x, y = cx - W//2, cy - H//2
    pygame.draw.rect(screen, (255,255,224), (x,y,W,H))
    pygame.draw.rect(screen, (0,0,0), (x,y,W,H), 2)

    t = title_font.render(f"Manage Buildings", True, (0,0,0))
    screen.blit(t, (x + (W - t.get_width())//2, y + 12))

    # Filter to real buildable properties (ignore RR/Utility)
    owned_props = [sp for sp in player.properties_owned if isinstance(sp, Property)]
    if not owned_props:
        none_lbl = body_font.render("You do not own any color properties.", True, (120,0,0))
        screen.blit(none_lbl, (x + (W - none_lbl.get_width())//2, y + 80))

    # Grid of buttons
    btns = []
    bx, by = x + 20, y + 60
    bw, bh = 230, 36
    gap_x, gap_y = 20, 25
    per_row = 3

    for i, sp in enumerate(owned_props):
        col = i % per_row
        row = i // per_row
        rx = bx + col * (bw + gap_x)
        ry = by + row * (bh + gap_y)
        r = pygame.Rect(rx, ry, bw, bh)
        pygame.draw.rect(screen, (220,220,220), r, border_radius=8)
        pygame.draw.rect(screen, (0,0,0), r, 2, border_radius=8)

        text_w, text_h = body_font.size(sp.name)

        blit_text_with_outline(screen, body_font, sp.name, (r.centerx - text_w//2, r.centery - text_h//2),
                       getattr(sp, "color_group", (0,0,0)), outline_color=(0,0,0), outline_width=2)
        
        btns.append((r, sp))

        # Small status (Houses/Hotel)
        status = body_font.render(f"Houses: {sp.num_houses}  Hotel: {'Yes' if sp.has_hotel else 'No'}", True, (40,40,40))
        screen.blit(status, (rx + 8, ry + bh + 5))

    # Cancel
    cancel_rect  = pygame.Rect(x + W//2 - 70, y + H - 60, 140, 44)
    pygame.draw.rect(screen, (150,0,0), cancel_rect)
    c2 = body_font.render("CANCEL",  True, (255,255,255))
    screen.blit(c2, (cancel_rect.centerx - c2.get_width()//2,  cancel_rect.centery  - c2.get_height()//2))

    return btns, cancel_rect

def draw_trade_select_modal(screen, players, selected_idxs, cx, cy):
    """
    Modal: choose exactly two players.
    selected_idxs: set[int] (mutated by caller based on clicks)
    Returns (player_btn_rects:list[Rect], confirm_rect:Rect, cancel_rect:Rect)
    """
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    body_font  = pygame.font.SysFont(None, 22)

    w, h = 460, 320
    x, y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    t = title_font.render("Choose 2 Players to Trade", True, (0,0,0))
    screen.blit(t, (x + (w - t.get_width())//2, y + 12))

    btn_rects = []
    bx, by = x + 20, y + 60
    bw, bh = 190, 42
    gap_x, gap_y = 20, 14
    per_row = 2

    for i, p in enumerate(players):
        col = i % per_row
        row = i // per_row
        rx = bx + col*(bw + gap_x)
        ry = by + row*(bh + gap_y)
        r = pygame.Rect(rx, ry, bw, bh)
        active = (i in selected_idxs)
        fill = (0,180,120) if active else (220,220,220)
        pygame.draw.rect(screen, fill, r, border_radius=10)
        pygame.draw.rect(screen, (0,0,0), r, 2, border_radius=10)
        name = body_font.render(p.name, True, getattr(p, "color", (0,0,0)))
        screen.blit(name, (r.centerx - name.get_width()//2, r.centery - name.get_height()//2))
        btn_rects.append(r)

    confirm_enabled = (len(selected_idxs) == 2)
    confirm_rect = pygame.Rect(x + w - 140 - 20, y + h - 50 - 16, 140, 50)
    cancel_rect  = pygame.Rect(x + 20, y + h - 50 - 16, 140, 50)

    pygame.draw.rect(screen, (0,150,0) if confirm_enabled else (150,150,150), confirm_rect)
    pygame.draw.rect(screen, (150,0,0), cancel_rect)
    c1 = body_font.render("CONFIRM", True, (255,255,255))
    c2 = body_font.render("CANCEL",  True, (255,255,255))
    screen.blit(c1, (confirm_rect.centerx - c1.get_width()//2, confirm_rect.centery - c1.get_height()//2))
    screen.blit(c2, (cancel_rect.centerx  - c2.get_width()//2,  cancel_rect.centery  - c2.get_height()//2))
    return btn_rects, confirm_rect, cancel_rect

def draw_trade_editor_modal(screen, p_left, p_right, offer, cx, cy):
    """
    Modal: pick items to trade and confirm.
    p_left, p_right: Player
    offer = {
        "left": {"cash": int, "gojf": int, "props": set()},   # props holds object ids
        "right":{"cash": int, "gojf": int, "props": set()},
    }
    Returns dict of rects for click handling.
    """
    rects = {}
    # Modal shell
    W, H = 740, 460
    x, y = cx - W//2, cy - H//2
    pygame.draw.rect(screen, (255,255,224), (x, y, W, H))
    pygame.draw.rect(screen, (0,0,0), (x, y, W, H), 2)

    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    body_font  = pygame.font.SysFont(None, 22)

    # Headers
    title = title_font.render("Trade", True, (0,0,0))
    screen.blit(title, (x + (W - title.get_width())//2, y + 10))

    # Columns
    col_w = (W - 60) // 2
    left_x  = x + 20
    right_x = x + 40 + col_w
    top_y   = y + 50

    # CASH & GOJF controls
    def draw_cash_gojf(side, player, col_x):
        # Cash row
        cash_y = top_y
        gap = 30
        dx = 120
        cash_lbl = body_font.render(f"Cash: ${offer[side]['cash']}", True, (0,0,0))
        screen.blit(cash_lbl, (col_x, cash_y))
        minus = pygame.Rect(col_x + dx, cash_y - 4, 26, 26)
        plus  = pygame.Rect(col_x + dx + gap, cash_y - 4, 26, 26)
        pygame.draw.rect(screen, (200,200,200), minus); pygame.draw.rect(screen, (0,0,0), minus, 2)
        pygame.draw.rect(screen, (200,200,200), plus);  pygame.draw.rect(screen, (0,0,0), plus,  2)
        m = body_font.render("-", True, (0,0,0)); p = body_font.render("+", True, (0,0,0))
        screen.blit(m, (minus.centerx - m.get_width()//2, minus.centery - m.get_height()//2))
        screen.blit(p, (plus.centerx  - p.get_width()//2,  plus.centery  - p.get_height()//2))
        rects[f"{side}_cash_minus"] = minus
        rects[f"{side}_cash_plus"]  = plus

        # GOJF row
        gojf_y = cash_y + 34
        gojf_dx = 230
        gojf_lbl = body_font.render(f"Get Out of Jail Free: {offer[side]['gojf']}/{player.get_out_of_jail_free_cards}", True, (0,0,0))
        screen.blit(gojf_lbl, (col_x, gojf_y))
        minus = pygame.Rect(col_x + gojf_dx, gojf_y - 4, 26, 26)
        plus  = pygame.Rect(col_x + gojf_dx + gap, gojf_y - 4, 26, 26)
        pygame.draw.rect(screen, (200,200,200), minus); pygame.draw.rect(screen, (0,0,0), minus, 2)
        pygame.draw.rect(screen, (200,200,200), plus);  pygame.draw.rect(screen, (0,0,0), plus,  2)
        m = body_font.render("-", True, (0,0,0)); p = body_font.render("+", True, (0,0,0))
        screen.blit(m, (minus.centerx - m.get_width()//2, minus.centery - m.get_height()//2))
        screen.blit(p, (plus.centerx  - p.get_width()//2,  plus.centery  - p.get_height()//2))
        rects[f"{side}_gojf_minus"] = minus
        rects[f"{side}_gojf_plus"]  = plus

        return gojf_y + 40  # content y after controls

    content_top_left  = draw_cash_gojf("left",  p_left,  left_x)
    content_top_right = draw_cash_gojf("right", p_right, right_x)

    # Properties grid per side, wraps into columns within the side panel
    def draw_prop_grid(side, player, col_x, start_y):
        # List properties by their board position to keep a stable UI order
        props = list(player.properties_owned)
        # Some spaces might not be tradable; filter by having a 'name'
        props = [sp for sp in props if hasattr(sp, "name")]
        # prop_color = props.
        props.sort(key=lambda sp: getattr(sp, "position", getattr(sp, "board_position", 0)))

        row_h = 24
        # Area for properties: from start_y to (y + H - 90) to leave room for confirm/cancel
        list_top = start_y
        list_bottom = y + H - 90
        avail_h = max(0, list_bottom - list_top)
        max_rows = max(10, avail_h // row_h)  # at least 10 rows to keep density reasonable
        if max_rows <= 0:
            max_rows = 10

        # Determine number of columns to fit all props within the side panel
        import math
        n = len(props)
        num_cols = max(1, math.ceil(n / max_rows))
        # Column width inside side panel
        gap_x = 10
        per_col_w = (col_w - (num_cols - 1) * gap_x)
        if num_cols > 0:
            per_col_w //= num_cols
        # Clamp to minimum width
        per_col_w = max(90, per_col_w)

        def trunc(text, max_px):
            # truncate text to fit in max_px using the current font
            if body_font.size(text)[0] <= max_px:
                return text
            s = text
            ell = "..."
            while s and body_font.size(s + ell)[0] > max_px:
                s = s[:-1]
            return s + ell if s else ell

        for idx, sp in enumerate(props):
            col = idx // max_rows
            row = idx % max_rows
            base_x = col_x + col * (per_col_w + gap_x)
            base_y = list_top + row * row_h
            # Small checkbox (visual)
            box = pygame.Rect(base_x, base_y + 3, 16, 16)
            pygame.draw.rect(screen, (255,255,255), box); pygame.draw.rect(screen, (0,0,0), box, 2)

            pid = id(sp)
            is_checked = pid in offer[side]["props"]
            if is_checked:
                # draw a cross
                pygame.draw.line(screen, (0,0,0), (box.left+3, box.top+3), (box.right-3, box.bottom-3), 2)
                pygame.draw.line(screen, (0,0,0), (box.left+3, box.bottom-3), (box.right-3, box.top+3), 2)

            # Text label
            color = getattr(sp, "color_group", (0,0,0))
            name_txt = trunc(sp.name, per_col_w - 28)

            if sp.type == "Utility":
                color = (255, 255, 200)        # Light Yellow
            elif sp.type == "Railroad":
                color = (60, 60, 60)

            blit_text_with_outline(screen, body_font, name_txt, (box.right + 6, base_y + 3),
                       color, outline_color=(0,0,0), outline_width=1)
        
            # Hit area covers box + text row for easy clicking
            hit = pygame.Rect(base_x, base_y, per_col_w, row_h)
            rects[f"box_{side}_{pid}"] = box
            rects[f"hit_{side}_{pid}"] = hit

        # Title
        t = title_font.render(f"{player.name}'s items", True, (0,0,0))
        screen.blit(t, (col_x, start_y - 30))

    draw_prop_grid("left",  p_left,  left_x,  content_top_left)
    draw_prop_grid("right", p_right, right_x, content_top_right)

    # --- Valuation summary (cash + GOJF*100 + sum(property.cost)) ---
    GOJF_VALUE = 100

    def selected_props_for(side, player):
        ids = offer[side]["props"]
        return [sp for sp in player.properties_owned if id(sp) in ids]

    def prop_value(sp):
        # Properties, Railroads, and Utilities all have a .cost in your model:contentReference[oaicite:1]{index=1}
        return getattr(sp, "cost", 0)

    def side_value(side, player):
        cash = offer[side]["cash"]
        gojf = offer[side]["gojf"] * GOJF_VALUE
        props = sum(prop_value(sp) for sp in selected_props_for(side, player))
        return cash + gojf + props

    left_total  = side_value("left",  p_left)
    right_total = side_value("right", p_right)
    delta = right_total - left_total  # positive => better for RIGHT, negative => better for LEFT

    # Labels under each column
    total_font = pygame.font.SysFont("Arial", 22, bold=True)
    small_font = pygame.font.SysFont(None, 16)

    def draw_total(col_x, who, total):
        lbl1 = total_font.render(f"{who.name} offer value:", True, (0,0,0))
        lbl2 = total_font.render(f"${total}", True, (0,0,0))
        y_line = y + H - 100
        screen.blit(lbl1, (col_x, y_line))
        screen.blit(lbl2, (col_x, y_line + 26))
        note = small_font.render("(Cash + Property cost + GOJF)", True, (60,60,60))
        screen.blit(note, (col_x, y_line + 52))

    draw_total(left_x,  p_left,  left_total)
    draw_total(right_x + 175, p_right, right_total)

    # Centered net indicator between columns
    net_text = f"Net to Right: ${delta}" if delta != 0 else "Even trade"
    net_color = (0,140,0) if delta > 0 else ((180,0,0) if delta < 0 else (20,20,20))
    net_lbl = total_font.render(net_text, True, net_color)
    screen.blit(net_lbl, (x + (W - net_lbl.get_width())//2, y + H - 140))

    # Confirm / Cancel
    confirm_rect = pygame.Rect(x + W//2 + 10, y + H - 70, 160, 50)
    cancel_rect  = pygame.Rect(x + W//2 - 170, y + H - 70, 160, 50)
    pygame.draw.rect(screen, (0,150,0), confirm_rect); pygame.draw.rect(screen, (0,0,0), confirm_rect, 2)
    pygame.draw.rect(screen, (150,0,0), cancel_rect);  pygame.draw.rect(screen, (0,0,0), cancel_rect,  2)
    c1 = title_font.render("CONFIRM", True, (255,255,255))
    c2 = title_font.render("CANCEL",  True, (255,255,255))
    screen.blit(c1, (confirm_rect.centerx - c1.get_width()//2, confirm_rect.centery - c1.get_height()//2))
    screen.blit(c2, (cancel_rect.centerx  - c2.get_width()//2,  cancel_rect.centery  - c2.get_height()//2))
    rects["confirm"] = confirm_rect
    rects["cancel"]  = cancel_rect
    return rects

def draw_jail_turn_choice_modal(screen, game, title_font, body_font, cx, cy):
    """
    Shows three buttons for a player who's starting/continuing a jail turn:
    - Use Get Out of Jail Free (if any)
    - Pay $50 (if they can afford it)
    - Roll for Doubles
    Returns a dict of rects: {"use":Rect or None, "pay":Rect or None, "roll":Rect}
    """
    info = getattr(game, "pending_jail_turn", None)
    if not info:
        return {"use": None, "pay": None, "roll": None}

    p = info["player"]

    w, h = 460, 240
    x, y = cx - w//2, cy - h//2
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h))
    pygame.draw.rect(screen, (0,0,0), (x,y,w,h), 2)

    t = title_font.render("You're in Jail", True, (0,0,0))
    s = body_font.render(f"{p.name}: choose how to get out", True, (0,0,0))
    screen.blit(t, (x + (w - t.get_width())//2, y + 12))
    screen.blit(s, (x + (w - s.get_width())//2, y + 48))

    # Buttons / availability
    can_use  = p.get_out_of_jail_free_cards > 0
    can_pay  = p.money >= 50

    r_use  = pygame.Rect(x + 20,       y + 90, 130, 46)
    r_pay  = pygame.Rect(x + 20 + 150, y + 90, 130, 46)
    r_roll = pygame.Rect(x + 20 + 300, y + 90, 130, 46)

    def draw_btn(rect, label, enabled, bg_on=(0,150,0), bg_off=(150,150,150)):
        pygame.draw.rect(screen, bg_on if enabled else bg_off, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        lbl = body_font.render(label, True, (255,255,255))
        screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                          rect.centery - lbl.get_height()//2))

    draw_btn(r_use,  "Use GOJF", can_use)
    draw_btn(r_pay,  "Pay $50",  can_pay)
    draw_btn(r_roll, "Roll",     True)

    # Note about forced pay on 3rd attempt will still be enforced server-side logic
    note = body_font.render(f"Jail turn: {p.jail_turns + 1} of 3", True, (40,40,40))
    screen.blit(note, (x + (w - note.get_width())//2, y + h - 40))

    return {"use": (r_use if can_use else None),
            "pay": (r_pay if can_pay else None),
            "roll": r_roll}

def draw_property_build_badges(screen, game, space_rects):
    """
    Houses/hotel triangles:
      - Apex still extends into the color strip (±15px) to touch the band
      - Flat side alignment is FIXED by using a constant height from the strip
      - Width along the strip adapts to fit N houses cleanly
    """
    HOUSE_COLOR = (0, 180, 0)
    HOTEL_COLOR = (220, 40, 40)

    # --- helpers ---
    def side_for_pos(pos:int):
        if   1  <= pos <= 9:   return "bottom"  # band at TOP of tile (horizontal)
        elif 11 <= pos <= 19:  return "left"    # band at RIGHT edge (vertical)
        elif 21 <= pos <= 29:  return "top"     # band at BOTTOM of tile (horizontal)
        elif 31 <= pos <= 39:  return "right"   # band at LEFT edge (vertical)
        return None

    def tri_from_apex(ax, ay, base_w, height, direction:str, apex_off:int=15):
        """
        Build an isosceles triangle given:
          - apex on the band edge but nudged INTO the band by apex_off
          - a BASE of width `base_w` that sits exactly `height` away from the band edge
        `ay`/`ax` are the inner edge coordinates of the color strip.
        """
        bw = float(base_w)
        h  = float(height)

        if direction == "up":       # band above; apex goes upward into band
            apex = (ax, ay - apex_off)
            base_y = ay + h
            return [(ax - bw/2, base_y), apex, (ax + bw/2, base_y)]

        if direction == "down":     # band below; apex goes downward into band
            apex = (ax, ay + apex_off)
            base_y = ay - h
            return [(ax - bw/2, base_y), apex, (ax + bw/2, base_y)]

        if direction == "left":     # band on left; apex goes left into band
            apex = (ax - apex_off, ay)
            base_x = ax + h
            return [(base_x, ay - bw/2), apex, (base_x, ay + bw/2)]

        if direction == "right":    # band on right; apex goes right into band
            apex = (ax + apex_off, ay)
            base_x = ax - h
            return [(base_x, ay - bw/2), apex, (base_x, ay + bw/2)]

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

        # Strip thickness (matches board drawing)
        strip_thickness = min(rect.width, rect.height) // 4
        pad = max(2, strip_thickness // 8)  # breathing room inside the tile

        # FIX: constant triangle height from the band, so the flat side lines up everywhere
        tri_height = max(6, strip_thickness - 2 * pad)

        # Which edge + layout axis
        if side in ("bottom", "top"):
            # inner edge y and pointing dir
            if side == "bottom":
                apex_y = rect.top + strip_thickness
                direction = "up"
            else:
                apex_y = rect.bottom - strip_thickness
                direction = "down"
            start_coord = rect.left + pad
            end_coord   = rect.right - pad
            axis = "x"
        else:
            if side == "left":
                apex_x = rect.right - strip_thickness
                direction = "right"
            else:
                apex_x = rect.left + strip_thickness
                direction = "left"
            start_coord = rect.top + pad
            end_coord   = rect.bottom - pad
            axis = "y"

        # Count to draw
        n_houses = int(getattr(sp, "num_houses", 0))
        has_hotel = bool(getattr(sp, "has_hotel", False))
        count = 1 if has_hotel else min(4, n_houses)
        if count == 0 and not has_hotel:
            continue

        # Width along the strip adapts to fit; gaps proportional to thickness
        gap = max(2, strip_thickness // 5)
        run_len = end_coord - start_coord
        base_w_max_from_run = (run_len - (count - 1) * gap) / max(1, count)

        # Keep base width reasonable versus height; don’t let it get needle-thin or super wide
        base_w = int(max(6, min(base_w_max_from_run, tri_height * 1.2)))
        if has_hotel:
            base_w = int(base_w * 1.25)

        # Center the group along the run
        total_used = count * base_w + (count - 1) * gap
        origin = start_coord + max(0, (run_len - total_used) // 2)

        def centers_1d(o, c, w, g):
            xs = []
            p = o
            for _ in range(c):
                xs.append(int(p + w / 2))
                p += w + g
            return xs

        if axis == "x":
            xs = centers_1d(origin, count, base_w, gap)
            for cx in xs:
                color = HOTEL_COLOR if has_hotel else HOUSE_COLOR
                pts = tri_from_apex(cx, apex_y, base_w, tri_height, direction, apex_off=15)
                pygame.draw.polygon(screen, color, pts)
                pygame.draw.polygon(screen, (0, 0, 0), pts, 1)
        else:
            ys = centers_1d(origin, count, base_w, gap)
            for cy in ys:
                color = HOTEL_COLOR if has_hotel else HOUSE_COLOR
                pts = tri_from_apex(apex_x, cy, base_w, tri_height, direction, apex_off=15)
                pygame.draw.polygon(screen, color, pts)
                pygame.draw.polygon(screen, (0, 0, 0), pts, 1)

def end_turn_button(screen:pygame.Surface, value_font, center_pos:tuple[int, int], enable:bool=True):
    cx,cy = center_pos
    # Position for the rectangle
    cx = cx + 230
    cy = cy + 30
    width = 140
    height = 50 
    end_rect = pygame.Rect(cx, cy, width, height)
    color = (200,0,0) if enable else (160,160,160)  # If you can't end turn, make grey or make red
    pygame.draw.rect(screen, color, end_rect)
    end_turn_text = value_font.render("End Turn", True, (0,0,0))
    screen.blit(end_turn_text, (cx + (width - end_turn_text.get_width())//2, cy + (height - end_turn_text.get_height())//2))
    return end_rect

def draw_mortgage_badges(screen, game, space_rects):
    badge_font = pygame.font.SysFont(None, 18)
    for sp in game.board.spaces:
        if not hasattr(sp, "is_mortgaged") or not sp.is_mortgaged:
            continue
        rect = space_rects.get(sp.index)
        if not rect: 
            continue
        # small red badge in top-left of the tile
        bx, by = rect.left + 4, rect.top + 4
        bw, bh = 18, 18
        pygame.draw.rect(screen, (180, 40, 40), (bx, by, bw, bh), border_radius=4)
        pygame.draw.rect(screen, (0,0,0), (bx, by, bw, bh), 1, border_radius=4)
        m = badge_font.render("M", True, (255,255,255))
        screen.blit(m, (bx + (bw - m.get_width())//2, by + (bh - m.get_height())//2))

def draw_debt_modal(screen, game, title_font, body_font, cx, cy):
    info = game.pending_debt
    if not info: return None, None
    p   = info["player"]
    amt = info["amount"]
    cred = info["creditor"]
    who  = cred.name if cred else "Bank"

    w,h = 420, 220
    but_w, but_h = 110, 44
    
    x,y = cx - w//2, cy - h//2
    but_x = x + 20
    but_gap = 140
    pygame.draw.rect(screen, (255,255,224), (x,y,w,h)); pygame.draw.rect(screen,(0,0,0),(x,y,w,h),2)

    t = title_font.render("Debt Due", True, (0,0,0))
    screen.blit(t, (x+(w-t.get_width())//2, y+12))
    a = body_font.render(f"{p.name} owes ${amt} to {who}", True, (0,0,0))
    b = body_font.render(info.get("reason",""), True, (60,60,60))
    c = body_font.render(f"Cash: ${p.money}", True, (0,0,0))
    screen.blit(a, (x+20,y+60)); screen.blit(b,(x+20,y+90)); screen.blit(c,(x+20,y+120))

    pay_rect = pygame.Rect(but_x,  y+150, but_w, but_h)
    manage_rect = pygame.Rect(but_x + but_gap, y+150, but_w - 10, but_h)
    bk_rect  = pygame.Rect(but_x + 2 * but_gap - 10, y+150, but_w, but_h)
    can_pay  = p.money >= amt


    pygame.draw.rect(screen, (0,150,0) if can_pay else (150,150,150), pay_rect)
    pygame.draw.rect(screen, (0,120,200), manage_rect)
    pygame.draw.rect(screen, (180,0,0), bk_rect)

    pl = body_font.render("PAY NOW", True, (255,255,255))
    ml = body_font.render("MANAGE",  True, (255,255,255))
    bl = body_font.render("BANKRUPT", True, (255,255,255))
    screen.blit(pl, (pay_rect.centerx - pl.get_width()//2, pay_rect.centery - pl.get_height()//2))
    screen.blit(ml, (manage_rect.centerx - ml.get_width()//2, manage_rect.centery - ml.get_height()//2))
    screen.blit(bl, (bk_rect.centerx  - bl.get_width()//2,  bk_rect.centery  - bl.get_height()//2))
    return pay_rect, bk_rect, manage_rect

def draw_bankrupt_notice(screen, game, title_font, body_font, cx, cy):
    info = getattr(game, "pending_bankrupt_notice", None)
    if not info: 
        return None
    
    debtor = info.get("debtor", "A player")
    cred   = info.get("creditor", None)

    w, h = 480, 200
    x, y = cx - w // 2, cy - h // 2

    # Card background
    pygame.draw.rect(screen, (255, 255, 224), (x, y, w, h))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h), 2)

    # Title
    title = title_font.render("Bankruptcy", True, (180, 0, 0))
    screen.blit(title, (x + (w - title.get_width()) // 2, y + 10))

    # Body text
    body1 = body_font.render(f"{debtor} is bankrupt.", True, (0, 0, 0))
    if cred:
        body2 = body_font.render(f"All assets transferred to {cred}.", True, (0, 0, 0))
    else:
        body2 = body_font.render("All assets returned to the Bank.", True, (0, 0, 0))

    screen.blit(body1, (x + 20, y + 70))
    screen.blit(body2, (x + 20, y + 100))

    # OK button
    ok_rect = pygame.Rect(cx - 55, cy + 40, 110, 44)
    pygame.draw.rect(screen, (0, 120, 200), ok_rect)
    ok_lbl = body_font.render("OK", True, (255, 255, 255))
    screen.blit(ok_lbl, (ok_rect.centerx - ok_lbl.get_width() // 2,
                         ok_rect.centery - ok_lbl.get_height() // 2))

    return ok_rect

def draw_winner_modal(screen, game, title_font, body_font, cx, cy):
    """
    Big modal that announces the winner. Returns the OK button rect.
    """
    w, h = 560, 260
    x, y = cx - w // 2, cy - h // 2

    # Backdrop card
    pygame.draw.rect(screen, (255, 255, 224), (x, y, w, h))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h), 2)

    title = title_font.render("Game Over", True, (0, 0, 0))
    screen.blit(title, (x + (w - title.get_width()) // 2, y + 18))

    if getattr(game, "winner", None) is not None:
        name = game.winner.name
        color = getattr(game.winner, "color", (0, 0, 0))
        msg = body_font.render(f"{name} has won the game!", True, color)
    else:
        msg = body_font.render("We have a winner!", True, (0, 0, 0))

    screen.blit(msg, (x + (w - msg.get_width()) // 2, y + 90))

    ok_rect = pygame.Rect(cx - 70, cy + 60, 140, 48)
    pygame.draw.rect(screen, (0, 120, 200), ok_rect)
    ok_lbl = body_font.render("OK", True, (255, 255, 255))
    screen.blit(ok_lbl, (ok_rect.centerx - ok_lbl.get_width() // 2,
                         ok_rect.centery - ok_lbl.get_height() // 2))
    return ok_rect

def blit_text_with_outline(surface, font, text, pos, color, outline_color=(0,0,0), outline_width=2):
    x, y = pos
    base = font.render(text, True, color)
    if outline_width <= 0:
        surface.blit(base, (x, y))
        return
    # draw outline by offsetting around the center
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx*dx + dy*dy == 0:
                continue
            shadow = font.render(text, True, outline_color)
            surface.blit(shadow, (x+dx, y+dy))
    surface.blit(base, (x, y))

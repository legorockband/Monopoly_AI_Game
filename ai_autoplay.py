# ai_autoplay.py
from ai_manage import AIMonopolyPropertyManager

def weighted_title_value(sp):
    t = getattr(sp, "type", "")
    if t == "Railroad":
        return getattr(sp, "cost", 0) * 1.05
    if t == "Utility":
        return getattr(sp, "cost", 0) * 0.35
    if t == "Property":
        COLOR_WEIGHTS = {
            (255, 165, 0): 1.30,  # Orange
            (255, 0, 0): 1.20,    # Red
            (173, 216, 230): 1.12,# Light Blue
            (255, 255, 0): 1.00,  # Yellow
            (0, 255, 0): 0.95,    # Green
            (255, 0, 255): 0.90,  # Pink
            (150, 75, 0): 0.85,   # Brown
            (0, 0, 139): 0.75,    # Dark Blue
        }
        w = COLOR_WEIGHTS.get(getattr(sp, "color_group", None), 0.8)
        return getattr(sp, "cost", 0) * w
    return getattr(sp, "cost", 0) or 0

def ai_wants_to_buy(cur, prop):
    """
    Mirrors your inline _ai_wants_to_buy, using dynamic cash buffer and
    light color weighting, but keeps main_display clean.
    """
    mgr = AIMonopolyPropertyManager()
    game = cur.board.game
    needed = mgr._cash_buffer_needed(game, cur)  # dynamic, threat-aware buffer
    t = getattr(prop, "type", "")
    cost = int(getattr(prop, "cost", 0) or 0)

    OVERREACH = 40  # small slack for good opportunities

    if t == "Railroad":
        return (cur.money - cost) >= (needed - OVERREACH)

    if t == "Utility":
        return (cur.money - cost) >= needed

    if t == "Property":
        mates = [s for s in cur.board.spaces
                 if getattr(s, "type", "") == "Property"
                 and getattr(s, "color_group", None) == getattr(prop, "color_group", None)]
        owned = sum(1 for s in mates if getattr(s, "owner", None) is cur)
        completes = (owned + 1) == len(mates)
        makes_pair = (owned + 1) == 2 and len(mates) > 2

        w = weighted_title_value(prop) / max(1, cost)

        slack = 0
        if completes:     slack += 70
        elif makes_pair:  slack += 40
        if w >= 1.15:     slack += 30
        elif w >= 1.08:   slack += 15

        return (cur.money - cost) >= (needed - slack)

    return False
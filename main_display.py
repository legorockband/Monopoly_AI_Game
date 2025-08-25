import pygame
import sys
import os
import ctypes

import dice
from board import *
import title_screen
import player_cards
from game import Game
from ai_mcts import MCTSMonopolyBot

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

# Maximize the window (Windows only)
if os.name == 'nt':
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.ShowWindow(hwnd, 3)  # 3 = SW_MAXIMIZE

clock = pygame.time.Clock()
pygame.display.set_caption("Monopoly")
value_font = pygame.font.SysFont('Arial', 30)
text_font = pygame.font.SysFont(None, 20)

screen_width, screen_height = pygame.display.get_surface().get_size()

# Properties of the board
board_size = int(min(screen_height, (5/8) * screen_width))
corner_size = board_size // 7

# Each edge has 9 spaces between corners
inner = board_size - 2 * corner_size
space_size = max(1, inner // 9)

circ_center = (board_size + (screen_width - board_size)//3, 375)

circ_rad = 50
circ_color = (255, 0, 0)

player_colors = [(0,0,255), (0,255,0), (255,0,0), (0, 255, 255)]

board_center = (board_size//2, board_size//2)

# --- Global popup delay (ms). You can override at runtime via env or by passing a param to running_display ---
DEFAULT_POPUP_DELAY_MS = int(os.getenv("POPUP_DELAY_MS", "800"))  # set to "0" for instant


# Local helper for rough property value (used in trade AI inside this file)
def _weighted_title_value(sp):
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


def running_display(player_names: list[str], popup_delay_ms: int | None = None):
    game = Game(player_names=player_names)
    bot = MCTSMonopolyBot(name_prefix="AI")  # instantiate once

    game._trade_attempted_this_turn = set()

    # Resolve the actual delay (env-backed default; per-call override allowed)
    AUTO_DELAY_MS = DEFAULT_POPUP_DELAY_MS if popup_delay_ms is None else max(0, int(popup_delay_ms))

    # --- Centered roll-off with per-player delay, full order display, and tie re-roll for first place ---
    def roll_for_first(game, screen, board_center, value_font):
        players_in_order = list(game.players)   # preserve initial order for stable tie-breaking
        roll_sum = {p: None for p in players_in_order}

        def draw_round(rows, subtitle=None):
            # rows: list of (name, sum) already rolled this sequence
            screen.fill((255, 255, 255))
            header = value_font.render("Rolling for turn order…", True, (0, 0, 0))
            screen.blit(header, (screen_width//2 - header.get_width() // 2,
                                 screen_height//2 - 120))
            y = -60
            for name, s in rows:
                line = value_font.render(f"{name} rolled {s}", True, (0, 0, 0))
                screen.blit(line, (screen_width//2 - line.get_width() // 2,
                                   screen_height//2 + y))
                y += 36
            if subtitle:
                sub = value_font.render(subtitle, True, (160, 0, 0))
                screen.blit(sub, (screen_width//2 - sub.get_width() // 2,
                                  screen_height//2 + 100))
            pygame.display.flip()

        # First round: everyone rolls, show each roll centered with a pause
        round_rows = []
        for p in players_in_order:
            s, _ = game.dice.roll()
            roll_sum[p] = s
            round_rows.append((p.name, s))
            draw_round(round_rows)
            pygame.time.delay(1000)  # delay between each player's roll

        # Break ties *within each score group only* so rerolls don't change cross-group order.
        # We keep each group's base score and add a tiny epsilon to preserve group ranking globally.
        def break_local_ties():
            nonlocal roll_sum

            # Group by the original integer roll result
            score_to_players = {}
            for p, s in roll_sum.items():
                base = int(s)
                score_to_players.setdefault(base, []).append(p)

            # Process from highest base score to lowest so higher groups keep their precedence
            for base_score in sorted(score_to_players.keys(), reverse=True):
                group = score_to_players[base_score]
                if len(group) <= 1:
                    continue  # nothing to break here

                # Keep rolling this group's players until their *within-group* results are unique
                while True:
                    # UI hint
                    draw_round(round_rows, f"Tie at {base_score}. Re-rolling tied players…")
                    pygame.time.delay(1000)

                    new_vals = {}
                    mini_rows = []
                    for p in group:
                        s_new, _ = game.dice.roll()
                        new_vals[p] = s_new
                        mini_rows.append((p.name, s_new))

                        # Show *this player's* roll immediately
                        screen.fill((255, 255, 255))
                        header = value_font.render("Tie-break rolls…", True, (0, 0, 0))
                        screen.blit(header, (screen_width//2 - header.get_width() // 2,
                                            screen_height//2 - 120))
                        y = -60
                        for name, s2 in mini_rows:
                            line = value_font.render(f"{name} rolled {s2}", True, (0, 0, 0))
                            screen.blit(line, (screen_width//2 - line.get_width() // 2,
                                            screen_height//2 + y))
                            y += 36
                        pygame.display.flip()
                        pygame.time.delay(1000)  # delay between each tied player’s roll

                    # Check uniqueness within this group
                    counts = {}
                    for v in new_vals.values():
                        counts[v] = counts.get(v, 0) + 1
                    if all(c == 1 for c in counts.values()):
                        # Unique — assign tiny eps to fix their relative order inside this base band
                        ordered_group = sorted(group, key=lambda p: new_vals[p], reverse=True)
                        n = len(ordered_group)
                        for rank, p in enumerate(ordered_group):
                            eps = (n - rank) / 100.0
                            roll_sum[p] = base_score + eps
                        break  # resolved this group; move to next
                    # else: loop again until unique

        break_local_ties()

        # Build final turn order: sort by roll_sum desc, stable for non-top ties
        ordered_players = sorted(players_in_order, key=lambda p: roll_sum[p], reverse=True)
        ordered_rows = [(p.name, int(roll_sum[p])) for p in ordered_players]

        # Show final order centered
        screen.fill((255, 255, 255))
        title = value_font.render("Turn order", True, (0, 0, 0))
        screen.blit(title, (screen_width//2 - title.get_width() // 2,
                            screen_height//2 - 140))
        y = -80
        for i, (name, r) in enumerate(ordered_rows, start=1):
            line = value_font.render(f"{i}. {name} ({r})", True, (0, 0, 0))
            screen.blit(line, (screen_width//2 - line.get_width() // 2,
                               screen_height//2 + y))
            y += 36
        pygame.display.flip()
        pygame.time.delay(1800)

        return ordered_players

    # Run the centered, delayed roll-off and apply the order
    ordered_players = roll_for_first(game, screen, board_center, value_font)
    game.players = ordered_players

    # Prevents clicks during the ordering screen
    pygame.event.clear()

    # Assign player colors in the new order so UI reflects turn order
    for i, player in enumerate(game.players):
        player.color = player_colors[i % len(player_colors)]

    running = True
    rolled = None
    space_rects = {}
    trade_rect = {}
    manage_rect = {}
    end_rect = {}

    # --- AI Timers ---
    ai_jail_notice_started_at = None
    ai_jail_turn_started_at = None
    ai_rent_started_at = None
    ai_tax_started_at = None
    ai_bankrupt_started_at = None
    ai_card_started_at = None
    ai_purchase_started_at = None
    ai_trade_started_at = None
    ai_tax_started_at = None
    ai_build_started_at = None
    ai_debt_started_at = None

    # --- Human timers  ---
    human_card_started_at = None
    human_purchase_started_at = None
    human_rent_started_at = None
    human_tax_started_at = None
    human_jail_notice_started_at = None
    human_jail_turn_started_at = None
    human_bankrupt_started_at = None
    human_trade_started_at = None
    human_debt_started_at = None

    def elapsed(start):
        return start is not None and (pygame.time.get_ticks() - start) >= AUTO_DELAY_MS

    def ready(start):
        # Clicks are allowed immediately if delay==0, else after min read time
        return (AUTO_DELAY_MS == 0) or elapsed(start)

    is_doubles = False
    has_rolled = False

    player_idx = 0
    selected_space = None

    manage_select_open = False
    trade_select_open = False         # player picker modal
    trade_selected = set()            # set of two indices
    trade_edit_open = False           # editor modal
    trade_editor_rects = None
    trade_offer = {
        "left":  {"cash": 0, "gojf": 0, "props": set()},  # store prop ids here; resolve to objects on confirm
        "right": {"cash": 0, "gojf": 0, "props": set()},
    }
    trade_pair = None  # (left_idx, right_idx) when editing/confirming

    def can_end_turn():
        # Check if you didn't roll doubles or in a popup menu
        return has_rolled and (not is_doubles) and not (game.pending_build or game.pending_rent or game.pending_purchase or game.last_drawn_card or game.pending_debt or game.pending_jail_turn or game.pending_bankrupt_notice)

    def advance_to_next():
        nonlocal player_idx, rolled, is_doubles, has_rolled
        nonlocal ai_jail_notice_started_at, ai_jail_turn_started_at, ai_rent_started_at, ai_tax_started_at, ai_bankrupt_started_at, ai_card_started_at, ai_purchase_started_at
        nonlocal human_card_started_at, human_purchase_started_at, human_rent_started_at, human_tax_started_at
        nonlocal human_jail_notice_started_at, human_jail_turn_started_at, human_bankrupt_started_at

        if len(game.players) == 0:
            return
        player_idx = (player_idx + 1) % len(game.players)
        rolled = None; is_doubles = False; has_rolled = False

        # reset timers each turn
        ai_card_started_at = None
        ai_purchase_started_at = None
        ai_jail_notice_started_at = ai_jail_turn_started_at = None
        ai_rent_started_at = ai_tax_started_at = ai_bankrupt_started_at = None
        ai_build_started_at = None
        ai_debt_started_at = None

        human_card_started_at = human_purchase_started_at = None
        human_rent_started_at = human_tax_started_at = None
        human_jail_notice_started_at = human_jail_turn_started_at = None
        human_bankrupt_started_at = None

        game.current_player_index = player_idx
        nxt = game.players[player_idx]
        if nxt.in_jail and not game.pending_jail_turn:
            game.start_jail_turn(nxt)

        # Allow trades again next turn
        if hasattr(game, "_trade_attempted_this_turn"):
            game._trade_attempted_this_turn.clear()

    def is_ai_player(p):
        return isinstance(getattr(p, "name", None), str) and p.name.strip().lower().startswith("ai")

    while running:
        # Check if any popups are going to happen
        def any_modal_open():
            cur = game.players[player_idx] if game.players else None
            jail_notice_blocks = bool(game.pending_jail and game.pending_jail.get("player") is cur)
            jail_turn_blocks   = bool(game.pending_jail_turn and game.pending_jail_turn.get("player") is cur)
            return (
                game.pending_purchase or game.pending_rent or game.pending_tax or
                game.pending_build or jail_notice_blocks or jail_turn_blocks or
                game.pending_debt or trade_select_open or trade_edit_open or
                manage_select_open
            )

        cur = game.players[player_idx] if game.players else None
        if cur and is_ai_player(cur):
            # 1) If the "Go To Jail" modal is up, acknowledge it after delay (drawn below)
            if game.pending_jail:
                p = game.pending_jail.get("player")
                if p is cur and ai_jail_notice_started_at is None:
                    ai_jail_notice_started_at = pygame.time.get_ticks()

            # 2) Jail turn choice -> wait, then act
            if game.pending_jail_turn and game.pending_jail_turn.get("player") is cur:
                now = pygame.time.get_ticks()
                if ai_jail_turn_started_at is None:
                    ai_jail_turn_started_at = now
                elif now - ai_jail_turn_started_at >= AUTO_DELAY_MS:
                    # --- Board saturation -> phase detection ---
                    props = [s for s in game.board.spaces if getattr(s, "type", "") == "Property"]
                    total_props = len(props) or 1
                    owned_props = sum(1 for s in props if getattr(s, "owner", None) is not None)
                    owned_ratio = owned_props / total_props
                    EARLY = owned_ratio < 0.50
                    forced_third = (cur.jail_turns >= 2)

                    if EARLY:
                        if cur.get_out_of_jail_free_cards > 0:
                            game.use_gojf_and_exit(cur)
                        elif cur.money >= 50:
                            game.pay_fine_and_exit(cur)
                        else:
                            game.roll_for_doubles_from_jail(cur)
                            rolled = (game.dice.die1_value, game.dice.die2_value)
                            is_doubles = (rolled[0] == rolled[1])
                            has_rolled = True
                            if cur.in_jail:
                                advance_to_next()
                                ai_jail_turn_started_at = None
                                continue
                    else:
                        if forced_third:
                            if cur.get_out_of_jail_free_cards > 0:
                                game.use_gojf_and_exit(cur)
                            elif cur.money >= 50:
                                game.pay_fine_and_exit(cur)
                            else:
                                game.roll_for_doubles_from_jail(cur)
                                rolled = (game.dice.die1_value, game.dice.die2_value)
                                is_doubles = (rolled[0] == rolled[1])
                                has_rolled = True
                                if cur.in_jail:
                                    advance_to_next()
                                    ai_jail_turn_started_at = None
                                    continue
                        else:
                            game.roll_for_doubles_from_jail(cur)
                            rolled = (game.dice.die1_value, game.dice.die2_value)
                            is_doubles = (rolled[0] == rolled[1])
                            has_rolled = True
                            if cur.in_jail:
                                advance_to_next()
                                ai_jail_turn_started_at = None
                                continue

                    # clear the timer after acting
                    ai_jail_turn_started_at = None

        # === Stamp timers at the start of the frame so both humans and AIs see consistent delays ===
        now = pygame.time.get_ticks()

        # Cards (Chance / Community Chest)
        if game.last_drawn_card:
            p = game.pending_card["player"]
            if is_ai_player(p):
                if ai_card_started_at is None:
                    ai_card_started_at = now
            else:
                if human_card_started_at is None:
                    human_card_started_at = now

        # Purchase
        if game.pending_purchase:
            p = game.pending_purchase.get("player")
            if p:
                if is_ai_player(p):
                    if ai_purchase_started_at is None:
                        ai_purchase_started_at = now
                else:
                    if human_purchase_started_at is None:
                        human_purchase_started_at = now

        # Rent
        if game.pending_rent:
            p = game.pending_rent.get("player")
            if p and is_ai_player(p):
                if ai_rent_started_at is None:
                    ai_rent_started_at = now
            else:
                if human_rent_started_at is None:
                    human_rent_started_at = now

        # Tax
        if game.pending_tax:
            p = game.pending_tax.get("player")
            if p and is_ai_player(p):
                if ai_tax_started_at is None:
                    ai_tax_started_at = now
            else:
                if human_tax_started_at is None:
                    human_tax_started_at = now

        # Go-To-Jail notice
        if game.pending_jail:
            p = game.pending_jail.get("player")
            if p and is_ai_player(p):
                if ai_jail_notice_started_at is None:
                    ai_jail_notice_started_at = now
            else:
                if human_jail_notice_started_at is None:
                    human_jail_notice_started_at = now

        # "You're in Jail" choice
        if game.pending_jail_turn:
            p = game.pending_jail_turn.get("player")
            if p and is_ai_player(p):
                if ai_jail_turn_started_at is None:
                    ai_jail_turn_started_at = now
            else:
                if human_jail_turn_started_at is None:
                    human_jail_turn_started_at = now

        # Bankruptcy notice
        if game.pending_bankrupt_notice:
            if ai_bankrupt_started_at is None:
                ai_bankrupt_started_at = now
            if human_bankrupt_started_at is None:
                human_bankrupt_started_at = now

        # Trade review timer stamping
        if game.pending_trade:
            responder = game.pending_trade.get("responder")
            if responder and is_ai_player(responder):
                if ai_trade_started_at is None:
                    ai_trade_started_at = now
            else:
                if human_trade_started_at is None:
                    human_trade_started_at = now

        # Debt
        if game.pending_debt:
            p = game.pending_debt.get("player")
            if p and is_ai_player(p):
                if ai_debt_started_at is None:
                    ai_debt_started_at = now
            else:
                if human_debt_started_at is None:
                    human_debt_started_at = now

        # === Auto-resolve AI popups AFTER the minimum read delay =========
        if cur and is_ai_player(cur):
            # 1) Chance / Community Chest card
            if game.last_drawn_card and ai_card_started_at is not None and elapsed(ai_card_started_at):
                pending_card = game.pending_card
                game.last_drawn_card = None
                game.pending_card = None
                ai_card_started_at = None
                if pending_card:
                    card = pending_card["card"]
                    player_card = pending_card["player"]
                    card.execute(player_card, game)
                    if pending_card["type"] == "Chance":
                        game.chance_cards.append(card)
                    else:
                        game.community_chest_cards.append(card)

            # 2) Rent
            if game.pending_rent and ai_rent_started_at is not None and elapsed(ai_rent_started_at):
                game.settle_rent()
                ai_rent_started_at = None

            # 3) Tax
            if game.pending_tax and ai_tax_started_at is not None and elapsed(ai_tax_started_at):
                game.confirm_tax()
                ai_tax_started_at = None

            # 4) Go To Jail notice (acknowledge after showing it)
            if game.pending_jail and ai_jail_notice_started_at is not None and elapsed(ai_jail_notice_started_at):
                p = game.pending_jail.get("player")
                if p is cur:
                    p.in_jail = True
                    p.position = game.board.jail_space_index
                    p.jail_turns = 0
                    game.pending_jail = None
                    ai_jail_notice_started_at = None
                    advance_to_next()

            # 5) Purchase decision (simple fallback: buy if affordable & keep $100 buffer)
            if game.pending_purchase and ai_purchase_started_at is not None and elapsed(ai_purchase_started_at):
                info = game.pending_purchase
                if info and info.get("player") is cur:
                    affordable = info.get("affordable", True)
                    prop = info.get("property")
                    # Conservative default: buy if affordable and leaves ~$100 buffer.
                    want_buy = bool(affordable and (cur.money - getattr(prop, "cost", 0) >= 100))
                    game.confirm_purchase(want_buy)
                ai_purchase_started_at = None

            # 6) Debt (raise cash in priority, then pay or bankrupt)
            if game.pending_debt and ai_debt_started_at is not None and elapsed(ai_debt_started_at):
                info = game.pending_debt
                p = info.get("player")
                if p is cur:
                    amt  = int(info.get("amount", 0))
                    cred = info.get("creditor")

                    # If we already can pay, do it.
                    if p.money >= amt:
                        p.pay_money(amt)
                        if cred: cred.collect_money(amt)
                        game.clear_debt()
                        ai_debt_started_at = None
                    else:
                        from ai_manage import AIMonopolyPropertyManager
                        from game import Property, Railroad, Utility
                        mgr = AIMonopolyPropertyManager()

                        progressed = True
                        # 1) Utilities/Railroads/Unimproved properties (strict order via manager)
                        while p.money < amt and progressed:
                            progressed = False
                            cands = mgr._non_core_mortgage_candidates(game, p)  # utilities/railroads first, then loose, then unimproved-in-monopoly
                            for _, sp in cands:
                                if p.money >= amt:
                                    break
                                if isinstance(sp, Property):
                                    ok, _ = sp.can_mortgage(p, game.board)
                                    if ok:
                                        sp.mortgage(p)
                                        progressed = True
                                elif isinstance(sp, (Railroad, Utility)):
                                    ok, _ = sp.can_mortgage(p)
                                    if ok:
                                        sp.mortgage(p)
                                        progressed = True

                        # 2) Last resort: sell houses/hotels (keeps even‑selling via can_* rules)
                        if p.money < amt:
                            # Try houses first, then hotels (or vice versa—both are "fourth" tier).
                            # We loop until we either reach amt or can’t sell any further.
                            changed = True
                            while p.money < amt and changed:
                                changed = False
                                # Sell one house if allowed anywhere
                                for sp in list(p.properties_owned):
                                    if hasattr(sp, "can_sell_house") and sp.can_sell_house(p, game.board)[0]:
                                        sp.sell_house(p)
                                        changed = True
                                        if p.money >= amt: break
                                if p.money >= amt: break
                                # Then try hotels
                                for sp in list(p.properties_owned):
                                    if hasattr(sp, "can_sell_hotel") and sp.can_sell_hotel(p, game.board)[0]:
                                        sp.sell_hotel(p)
                                        changed = True
                                        if p.money >= amt: break

                        # Pay if we made it; else bankrupt
                        if p.money >= amt:
                            p.pay_money(amt)
                            if cred: cred.collect_money(amt)
                            game.clear_debt()
                        else:
                            # Remove debtor, transfer assets, and show the standard notice
                            debtor = p
                            was_current = (game.players and game.players[player_idx] is debtor)
                            game.declare_bankruptcy(debtor, cred)
                            game.clear_debt()
                            # If the AI disappeared and it was their turn, start next player cleanly
                            if was_current and not game.game_over:
                                rolled = None
                                is_doubles = False
                                has_rolled = False
                                if 0 <= player_idx < len(game.players):
                                    nxt = game.players[player_idx]
                                    if nxt.in_jail and not game.pending_jail_turn:
                                        game.start_jail_turn(nxt)

                        ai_debt_started_at = None

            # 7) Bankrupt notice (close after delay so it's readable)
            if game.pending_bankrupt_notice and ai_bankrupt_started_at is not None and elapsed(ai_bankrupt_started_at):
                game.pending_bankrupt_notice = None
                ai_bankrupt_started_at = None

        # --- Click Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Winner modal blocks everything else
                if game.game_over:
                    cx, cy = board_center
                    ok_rect = draw_winner_modal(screen, game, value_font, value_font, cx, cy)
                    if ok_rect and ok_rect.collidepoint(mouse_pos):
                        running = False
                    continue

                # Show the Chance/ CC Card
                if game.last_drawn_card:
                    p = game.pending_card["player"]
                    # Humans click to continue; AI resolves elsewhere automatically
                    if not is_ai_player(p):
                        if not ready(human_card_started_at):
                            continue
                        pending_card = game.pending_card
                        game.last_drawn_card = None
                        game.pending_card = None
                        if pending_card:
                            card = pending_card["card"]
                            player_card = pending_card["player"]
                            card.execute(player_card, game)
                            if pending_card["type"] == "Chance":
                                game.chance_cards.append(card)
                            else:
                                game.community_chest_cards.append(card)
                    continue  # block other clicks this frame

                # Rent
                if game.pending_rent:
                    cx, cy = board_center
                    pay_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                    p = game.pending_rent.get("player")
                    if p and not is_ai_player(p) and not ready(human_rent_started_at):
                        continue
                    if pay_rect.collidepoint(mouse_pos):
                        game.settle_rent()
                        human_rent_started_at = None
                    continue

                # Tax
                if game.pending_tax:
                    tp = game.pending_tax.get("player")
                    if tp and not is_ai_player(tp):
                        if not ready(human_tax_started_at):
                            continue
                        cx, cy = board_center
                        pay_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                        if pay_rect.collidepoint(mouse_pos):
                            game.confirm_tax()
                            human_tax_started_at = None
                    continue

                # If BUILD/MANAGE modal is up: only allow its buttons
                if game.pending_build:
                    cx, cy = board_center
                    rects = draw_build_modal(screen, game, value_font, text_font, cx, cy)
                    if rects:  # click handling
                        if rects["buy_house"].collidepoint(mouse_pos) and game.pending_build["can_house"]:
                            game.confirm_build("house")
                        elif rects["buy_hotel"].collidepoint(mouse_pos) and game.pending_build["can_hotel"]:
                            game.confirm_build("hotel")
                        elif rects["sell_house"].collidepoint(mouse_pos) and game.pending_build.get("can_sell_house"):
                            game.confirm_build("sell_house")
                        elif rects["sell_hotel"].collidepoint(mouse_pos) and game.pending_build.get("can_sell_hotel"):
                            game.confirm_build("sell_hotel")
                        elif rects["mortgage"].collidepoint(mouse_pos) and game.pending_build.get("can_mortgage"):
                            game.confirm_build("mortgage")
                        elif rects["unmortgage"].collidepoint(mouse_pos) and game.pending_build.get("can_unmortgage"):
                            game.confirm_build("unmortgage")
                        elif rects["skip"].collidepoint(mouse_pos):
                            game.confirm_build("skip")
                    continue

                # If a purchase is pending, only handle BUY / SKIP clicks
                if game.pending_purchase:
                    buy_rect, skip_rect = purchase_button_rects(board_center[0], board_center[1] + 55)
                    is_human = not is_ai_player(game.pending_purchase["player"])
                    if is_human and not ready(human_purchase_started_at):
                        continue

                    affordable = game.pending_purchase.get("affordable", True)

                    if buy_rect.collidepoint(mouse_pos):
                        if affordable:   # ignore clicks if not affordable (greyed out)
                            game.confirm_purchase(True)
                            if is_human: human_purchase_started_at = None

                    elif skip_rect.collidepoint(mouse_pos):
                        game.confirm_purchase(False)
                        if is_human: human_purchase_started_at = None
                    continue

                # Jail popup
                if game.pending_jail:
                    cx, cy = board_center
                    ok_rect = draw_jail_modal(screen, game, value_font, text_font, cx, cy)
                    p = game.pending_jail["player"]
                    if p and not is_ai_player(p) and not ready(human_jail_notice_started_at):
                        continue
                    if ok_rect.collidepoint(mouse_pos):
                        p.in_jail = True
                        p.position = game.board.jail_space_index
                        p.jail_turns = 0
                        game.pending_jail = None
                        human_jail_notice_started_at = None
                        advance_to_next()
                    continue

                # Jail-turn choice modal blocks everything else
                if game.pending_jail_turn:
                    cx, cy = board_center
                    rects = draw_jail_turn_choice_modal(screen, game, value_font, text_font, cx, cy)
                    r_use, r_pay, r_roll = rects["use"], rects["pay"], rects["roll"]
                    p = game.pending_jail_turn["player"]
                    if p and not is_ai_player(p) and not ready(human_jail_turn_started_at):
                        continue

                    if r_use and r_use.collidepoint(mouse_pos):
                        game.use_gojf_and_exit(p)
                        human_jail_turn_started_at = None
                        rolled = None; is_doubles = False; has_rolled = False
                        continue

                    if r_pay and r_pay.collidepoint(mouse_pos):
                        game.pay_fine_and_exit(p)
                        human_jail_turn_started_at = None
                        rolled = None; is_doubles = False; has_rolled = False
                        continue

                    if r_roll and r_roll.collidepoint(mouse_pos):
                        game.roll_for_doubles_from_jail(p)
                        human_jail_turn_started_at = None
                        rolled = (game.dice.die1_value, game.dice.die2_value)
                        is_doubles = (rolled[0] == rolled[1])
                        has_rolled = True
                        if p.in_jail:
                            advance_to_next()
                        continue

                # --- DEBT MODAL (blocks all other clicks while open) ---
                if game.pending_debt:
                    info = game.pending_debt
                    p   = info["player"]
                    amt = info["amount"]
                    cred = info["creditor"]  # could be None (Bank)

                    cx, cy = board_center
                    pay_r, bk_r, mg_r = draw_debt_modal(screen, game, value_font, text_font, cx, cy)

                    if mg_r and mg_r.collidepoint(mouse_pos):
                        # open Manage picker; debt stays pending
                        manage_select_open = True
                    elif pay_r and pay_r.collidepoint(mouse_pos):
                        info = game.pending_debt
                        p   = info["player"]; amt = info["amount"]; cred = info["creditor"]
                        if p.money >= amt:
                            p.pay_money(amt)
                            if cred: cred.collect_money(amt)
                            game.clear_debt()

                    elif bk_r and bk_r.collidepoint(mouse_pos):
                        info = game.pending_debt
                        debtor = info["player"]; cred = info["creditor"]

                        # Was the debtor the current player *before* we modify the list?
                        was_current = (0 <= player_idx < len(game.players) and game.players[player_idx] is debtor)

                        game.declare_bankruptcy(debtor, cred)
                        game.clear_debt()

                        # If the bankrupt player was the current player, the players list shrank
                        # and player_idx now points at the next player. Start their turn fresh.
                        if was_current and not game.game_over:
                            rolled = None
                            is_doubles = False
                            has_rolled = False
                            # If that next player starts in jail, open their jail modal now
                            if 0 <= player_idx < len(game.players):
                                nxt = game.players[player_idx]
                                if nxt.in_jail and not game.pending_jail_turn:
                                    game.start_jail_turn(nxt)

                        # keep UI sane if the current player just disappeared
                        if player_idx >= len(game.players):
                            player_idx = 0

                        manage_select_open = trade_select_open = trade_edit_open = False

                        # block all other clicks
                        continue

                if game.pending_bankrupt_notice:
                    cx, cy = board_center
                    ok_rect = draw_bankrupt_notice(screen, game, value_font, text_font, cx, cy)
                    if not ready(human_bankrupt_started_at):
                        continue

                    if ok_rect and ok_rect.collidepoint(mouse_pos):
                        game.pending_bankrupt_notice = None
                        human_bankrupt_started_at = None
                    continue

                # --- TRADE REVIEW modal blocks everything else ---
                if game.pending_trade and not trade_edit_open:
                    responder = game.pending_trade.get("responder")
                    cx, cy = board_center
                    acc_r, rej_r, ctr_r = draw_trade_review_modal(
                        screen, game, value_font, text_font, cx, cy
                    )

                    # Enforce min read time for humans
                    if responder and (not is_ai_player(responder)) and (not ready(human_trade_started_at)):
                        continue

                    if acc_r.collidepoint(mouse_pos):
                        ok, msg = game.accept_trade()
                        print(msg)
                        human_trade_started_at = None
                    elif rej_r.collidepoint(mouse_pos):
                        ok, msg = game.reject_trade()
                        print(msg)
                        human_trade_started_at = None

                    elif ctr_r.collidepoint(mouse_pos):
                        # Open the editor prefilled for COUNTER by the responder.
                        # We make responder the left side in the editor for clarity.
                        # Figure out indices and seed 'trade_offer' sets from current proposal.
                        t = game.pending_trade
                        iL = game.players.index(responder)
                        # Find the other participant:
                        other = t["left"] if responder is t["right"] else t["right"]
                        iR = game.players.index(other)
                        trade_pair = (iL, iR)
                        trade_edit_open = True
                        trade_editor_rects = draw_trade_editor_modal(
                            screen, game.players[iL], game.players[iR], trade_offer, board_center[0], board_center[1]
                        )

                        # Prefill with current "what responder gives/gets" mirrored to editor sides
                        trade_offer = {"left":{"cash":0,"gojf":0,"props":set()},
                                       "right":{"cash":0,"gojf":0,"props":set()}}

                        if responder is t["right"]:
                            # Responder (right) becomes editor 'left'
                            trade_offer["left"]["cash"] = t["offer_right"].get("cash",0)
                            trade_offer["left"]["gojf"] = t["offer_right"].get("gojf",0)
                            trade_offer["left"]["props"] = { id(sp) for sp in t["offer_right"].get("props",[]) }

                            trade_offer["right"]["cash"] = t["offer_left"].get("cash",0)
                            trade_offer["right"]["gojf"] = t["offer_left"].get("gojf",0)
                            trade_offer["right"]["props"] = { id(sp) for sp in t["offer_left"].get("props",[]) }
                        else:
                            # Responder (left) becomes editor 'left'
                            trade_offer["left"]["cash"] = t["offer_left"].get("cash",0)
                            trade_offer["left"]["gojf"] = t["offer_left"].get("gojf",0)
                            trade_offer["left"]["props"] = { id(sp) for sp in t["offer_left"].get("props",[]) }

                            trade_offer["right"]["cash"] = t["offer_right"].get("cash",0)
                            trade_offer["right"]["gojf"] = t["offer_right"].get("gojf",0)
                            trade_offer["right"]["props"] = { id(sp) for sp in t["offer_right"].get("props",[]) }

                        # Close the review modal visually (but keep negotiation going in editor).
                        # The editor's Confirm click will call game.counter_trade(...) or start_trade_proposal(...)
                        # game.pending_trade = None
                        human_trade_started_at = None
                    continue  # block others while trade modal is up

                if selected_space is not None:
                    selected_space = None
                    continue

                # Clicked on a space when their isn't a popup
                if not any_modal_open() and space_rects:  # populated below each frame
                    for pos, rect in space_rects.items():
                        if rect.collidepoint(mouse_pos):
                            sp = game.board.spaces[pos]
                            if getattr(sp, "type", "") in ("Property", "Railroad", "Utility"):
                                selected_space = sp
                            break
                    
                    if selected_space is not None:
                        continue  # don't treat as dice click

                # --- TRADE: editor modal blocks everything ---
                if trade_edit_open and trade_pair is not None:
                    cx, cy = board_center
                    iL, iR = trade_pair
                    pL, pR = game.players[iL], game.players[iR]
                    rects = trade_editor_rects or {}
                    if not rects:
                        trade_editor_rects = draw_trade_editor_modal(screen, pL, pR, trade_offer, board_center[0], board_center[1])

                    def adjust(side, key, delta, max_val=None):
                        if key == "cash":
                            trade_offer[side]["cash"] = max(0, trade_offer[side]["cash"] + delta)
                        elif key == "gojf":
                            cap = max_val if max_val is not None else 0
                            newv = trade_offer[side]["gojf"] + delta
                            newv = max(0, min(cap, newv))
                            trade_offer[side]["gojf"] = newv

                    # Cash/GOJF controls
                    if rects["left_cash_minus"].collidepoint(mouse_pos):  adjust("left",  "cash", -10)
                    elif rects["left_cash_plus"].collidepoint(mouse_pos): adjust("left",  "cash", +10)
                    elif rects["right_cash_minus"].collidepoint(mouse_pos):adjust("right", "cash", -10)
                    elif rects["right_cash_plus"].collidepoint(mouse_pos): adjust("right", "cash", +10)
                    elif rects["left_gojf_minus"].collidepoint(mouse_pos): adjust("left",  "gojf", -1, pL.get_out_of_jail_free_cards)
                    elif rects["left_gojf_plus"].collidepoint(mouse_pos):  adjust("left",  "gojf", +1, pL.get_out_of_jail_free_cards)
                    elif rects["right_gojf_minus"].collidepoint(mouse_pos):adjust("right", "gojf", -1, pR.get_out_of_jail_free_cards)
                    elif rects["right_gojf_plus"].collidepoint(mouse_pos): adjust("right", "gojf", +1, pR.get_out_of_jail_free_cards)

                    # Property checkboxes: look for any key starting with "box_" or "hit_"
                    else:
                        clicked_box = None
                        for key, r in rects.items():
                            if (key.startswith("hit_") or key.startswith("box_")) and r.collidepoint(mouse_pos):
                                clicked_box = key; break

                        if clicked_box:
                            _, side, pid_str = clicked_box.split("_", 2)
                            pid = int(pid_str)
                            s = trade_offer[side]["props"]
                            if pid in s: s.remove(pid)
                            else: s.add(pid)

                        elif rects["confirm"].collidepoint(mouse_pos):
                            # Build concrete offers using id->object resolution
                            left_props  = [sp for sp in game.players[iL].properties_owned if id(sp) in trade_offer["left"]["props"]]
                            right_props = [sp for sp in game.players[iR].properties_owned if id(sp) in trade_offer["right"]["props"]]

                            offerL = {"cash": trade_offer["left"]["cash"],  "gojf": trade_offer["left"]["gojf"],  "props": left_props}
                            offerR = {"cash": trade_offer["right"]["cash"], "gojf": trade_offer["right"]["gojf"], "props": right_props}

                            # If a trade is already pending and *this* user is the responder, this is a COUNTER.
                            if game.pending_trade and game.pending_trade.get("responder") is game.players[iL]:
                                ok, msg = game.counter_trade(offerL, offerR)
                                print(msg)
                            else:
                                # Fresh proposal (iL proposes to iR)
                                game.start_trade_proposal(game.players[iL], game.players[iR], offerL, offerR)
                                print(f"{game.players[iL].name} proposed a trade to {game.players[iR].name}.")

                            # After creating/countering a proposal, block further new trades this turn
                            if hasattr(game, "_trade_attempted_this_turn"):
                                game._trade_attempted_this_turn.update({ game.players[iL], game.players[iR] })

                            # Reset UI (close editor)
                            trade_editor_rects = None
                            trade_edit_open = False
                            trade_pair = None
                            trade_selected.clear()
                            trade_offer = {"left":{"cash":0,"gojf":0,"props":set()}, "right":{"cash":0,"gojf":0,"props":set()}}

                        elif rects["cancel"].collidepoint(mouse_pos):
                            trade_edit_open = False
                            trade_pair = None
                            trade_selected.clear()
                            trade_offer = {"left":{"cash":0,"gojf":0,"props":set()}, "right":{"cash":0,"gojf":0,"props":set()}}
                            trade_editor_rects = None
                    continue  # block all other clicks while editor is open

                # --- TRADE: selection modal blocks everything ---
                if trade_select_open:
                    cx, cy = board_center
                    btn_rects, confirm_rect, cancel_rect = draw_trade_select_modal(
                        screen, game.players, trade_selected, cx, cy
                    )
                    for i, r in enumerate(btn_rects):
                        if r.collidepoint(mouse_pos):
                            if i in trade_selected: trade_selected.remove(i)
                            else:
                                if len(trade_selected) < 2: trade_selected.add(i)
                            break
                    else:
                        if confirm_rect.collidepoint(mouse_pos) and len(trade_selected) == 2:
                            iL, iR = sorted(list(trade_selected))
                            trade_pair = (iL, iR)
                            trade_edit_open = True
                            trade_editor_rects = draw_trade_editor_modal(
                                screen, game.players[iL], game.players[iR], trade_offer, board_center[0], board_center[1]
                            )
                            trade_select_open = False
                        elif cancel_rect.collidepoint(mouse_pos):
                            trade_select_open = False
                            trade_selected.clear()
                    continue  # block others while selection is open

                # --- MANAGE: selection modal blocks everything ---
                if manage_select_open:
                    cx, cy = board_center
                    prop_btns, cancel_rect = draw_manage_select_modal(screen, game.players[player_idx], game.board, board_center[0], board_center[1])
                    clicked_any = False
                    for r, sp in prop_btns:
                        if r.collidepoint(mouse_pos):
                            # Compute flags for this property and open the same build modal
                            p = game.players[player_idx]
                            can_house, _ = sp.can_build_house(p, game.board)
                            can_hotel, _ = sp.can_build_hotel(p, game.board)
                            can_sell_house, _ = sp.can_sell_house(p, game.board)
                            can_sell_hotel, _ = sp.can_sell_hotel(p, game.board)
                            can_mortgage, _    = sp.can_mortgage(p, game.board)
                            can_unmortgage, _  = sp.can_unmortgage(p)

                            game.pending_build = {
                                "player": p,
                                "property": sp,
                                "can_house": can_house,
                                "can_hotel": can_hotel,
                                "can_sell_house": can_sell_house,
                                "can_sell_hotel": can_sell_hotel,
                                "can_mortgage": can_mortgage,
                                "can_unmortgage": can_unmortgage,
                                "cost": sp.house_cost,
                            }
                            manage_select_open = False
                            clicked_any = True
                            break
                    if not clicked_any:
                        if cancel_rect.collidepoint(mouse_pos):
                            manage_select_open = False
                    continue  # block other clicks while manage picker is open

                # --- Trade button click (only when no other modals are up) ---
                if trade_rect and trade_rect.collidepoint(mouse_pos):
                    trade_select_open = True
                    trade_selected.clear()
                    continue

                # --- Manage button click ---
                if manage_rect and manage_rect.collidepoint(mouse_pos):
                    # Only open if NOT in the middle of another decision
                    if not (game.pending_build or game.pending_rent or game.pending_purchase or game.pending_tax or game.pending_jail or game.last_drawn_card or trade_select_open or trade_edit_open):
                        manage_select_open = True
                    continue

                # End Turn button click
                if end_rect and end_rect.collidepoint(mouse_pos):
                    if can_end_turn():
                        advance_to_next()
                    continue

                if not dice.is_inside_circle(mouse_pos, circ_center, circ_rad):
                    continue

                player = game.players[player_idx]

                if player.in_jail:
                    if not game.pending_jail_turn:
                        game.start_jail_turn(player)
                    continue

                # If you haven't rolled yet or you have doubles, you can roll again
                if (not has_rolled or is_doubles) and not player.in_jail:
                    roll_total, is_doubles = game.dice.roll()
                    has_rolled = True
                    rolled = (game.dice.die1_value, game.dice.die2_value)
                    player.move(roll_total, game.board)

                # What to do if there are doubles
                if is_doubles:
                    player.doubles_rolled_consecutive += 1
                    if player.doubles_rolled_consecutive == 3:
                        print(f"{player.name} rolled 3 doubles! Go to jail.")
                        game.pending_jail = {"player": player}
                        player.doubles_rolled_consecutive = 0
                        rolled = None
                        is_doubles = False
                        has_rolled = False
                else:
                    player.doubles_rolled_consecutive = 0

        # Draw the Board
        space_rects = board_game(screen, text_font, board_size, corner_size, space_size)
        draw_mortgage_badges(screen, game, space_rects)

        # --- SAFETY: players list may have changed this frame (e.g., bankruptcy) ---
        if not game.players:
            # No one left; end safely (Game.declare_bankruptcy should normally set game_over/winner)
            running = False
            pygame.display.flip()
            break  # or 'return' if you prefer exiting the function

        if player_idx >= len(game.players):
            # Clamp to the new list length (wrap to 0 is fine for turn order)
            player_idx %= len(game.players)

        # game.current_player_index = player_idx
        current_player = game.players[player_idx]

        enable_dice = ((not has_rolled or is_doubles) and not current_player.in_jail and not game.game_over)

        # --- AI driver: let the bot act automatically (when it’s an AI’s turn) ---
        if bot.is_ai(current_player):
            # If any modal is open, let UI handle it + delay; DO NOT step the bot now.
            modals_open = (
                game.last_drawn_card or game.pending_purchase or game.pending_rent or
                game.pending_tax or game.pending_build or game.pending_debt or
                game.pending_jail or game.pending_jail_turn or game.pending_bankrupt_notice or
                game.pending_trade
            )
            if not modals_open:
                intent = bot.step(game, current_player, iterations=300)
                if intent.get("want_roll") and enable_dice:
                    roll_total, is_doubles = game.dice.roll()
                    has_rolled = True
                    rolled = (game.dice.die1_value, game.dice.die2_value)
                    current_player.move(roll_total, game.board)

            # End turn automatically if allowed
            if (has_rolled and (not is_doubles) and not (game.pending_build or game.pending_rent or game.pending_purchase or game.last_drawn_card or game.pending_debt or game.pending_jail_turn or game.pending_bankrupt_notice or game.pending_trade)):
                advance_to_next()

        # Make interactable buttons
        dice.make_dice_button(screen, circ_color, circ_center, circ_rad, enable=enable_dice)
        end_rect = end_turn_button(screen, value_font, circ_center, enable=can_end_turn())
        trade_rect = trade_button(screen, value_font, circ_center, enable=True)
        manage_rect = manage_button(screen, value_font, circ_center, enable=True)

        # Draw the houses or hotels
        draw_property_build_badges(screen, game, space_rects)

        move_player(screen, game.players, board_size, corner_size, space_size)

        # Show the player stats
        player_cards.create_player_card(screen, game.players, player_idx, board_size, space_size, screen_width, screen_height, game)

        # Display dice roll and total
        if rolled:
            dice.draw_dice(screen, rolled, circ_center[0] - 200, circ_center[1] - 200)
            dice.draw_total(screen, rolled, circ_center[0], circ_center[1] - 350, value_font)

            if is_doubles:
                doubles_text = value_font.render("You rolled doubles!", True, (0, 0, 0))
                screen.blit(doubles_text, (circ_center[0] - doubles_text.get_width()//2, circ_center[1] - 300))

        # If there is a pending display, draw one of them
        if game.game_over:
            cx, cy = board_center
            draw_winner_modal(screen, game, value_font, value_font, cx, cy)

        # Show what chance card the player gets
        elif game.last_drawn_card:
            p = game.pending_card["player"]
            card = game.pending_card["card"]

            # Always draw the card (humans + AIs get to read it)
            display_card(screen, p, card, board_size, screen_height)

            if is_ai_player(p):
                # auto-execute after delay
                if ai_card_started_at is None:
                    ai_card_started_at = pygame.time.get_ticks()
                elif elapsed(ai_card_started_at):
                    pending = game.pending_card
                    game.last_drawn_card = None
                    game.pending_card = None
                    ai_card_started_at = None

                    if pending:
                        c = pending["card"]; pl = pending["player"]
                        c.execute(pl, game)
                        if pending["type"] == "Chance":
                            game.chance_cards.append(c)
                        else:
                            game.community_chest_cards.append(c)
            else:
                # Human: click to continue (mouse handler already enforces delay via ready(human_card_started_at))
                if human_card_started_at is None:
                    human_card_started_at = pygame.time.get_ticks()

        elif game.pending_purchase:
            draw_purchase_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

            p = game.pending_purchase.get("player")
            affordable = game.pending_purchase.get("affordable", True)
            prop = game.pending_purchase.get("property")

            if is_ai_player(p):
                if ai_purchase_started_at is None:
                    ai_purchase_started_at = pygame.time.get_ticks()
                elif elapsed(ai_purchase_started_at):
                    # Heuristic: buy if affordable AND keep a small buffer
                    want_buy = bool(affordable and (p.money - getattr(prop, "cost", 0) >= 100))
                    game.confirm_purchase(want_buy)
                    ai_purchase_started_at = None
            else:
                if human_purchase_started_at is None:
                    human_purchase_started_at = pygame.time.get_ticks()

        elif game.pending_rent:
            draw_rent_modal(screen, game, value_font, text_font, board_center[0], board_center[1])
            p = game.pending_rent.get("player")
            if p and is_ai_player(p):
                if ai_rent_started_at is None:
                    ai_rent_started_at = pygame.time.get_ticks()
                elif elapsed(ai_rent_started_at):
                    game.settle_rent()
                    ai_rent_started_at = None
            else:
                if human_rent_started_at is None:
                    human_rent_started_at = pygame.time.get_ticks()

        elif game.pending_build:
            draw_build_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

            # Auto-resolve for AI after the same read delay pattern as other popups
            info = game.pending_build
            p = info.get("player")
            if p and is_ai_player(p):
                if ai_build_started_at is None:
                    ai_build_started_at = pygame.time.get_ticks()
                elif elapsed(ai_build_started_at):
                    # prefer house -> hotel -> else skip
                    if info.get("can_house"):
                        game.confirm_build("house")
                    elif info.get("can_hotel"):
                        game.confirm_build("hotel")
                    else:
                        game.confirm_build("skip")
                    ai_build_started_at = None

        elif game.pending_tax:
            tp = game.pending_tax.get("player")
            if tp and is_ai_player(tp):
                if ai_tax_started_at is None:
                    ai_tax_started_at = pygame.time.get_ticks()
                elif elapsed(ai_tax_started_at):
                    game.confirm_tax()
                    ai_tax_started_at = None
            else:
                if human_tax_started_at is None:
                    human_tax_started_at = pygame.time.get_ticks()
                draw_tax_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_jail:
            p = game.pending_jail.get("player")
            draw_jail_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

            if p and is_ai_player(p):
                if ai_jail_notice_started_at is None:
                    ai_jail_notice_started_at = pygame.time.get_ticks()
                elif elapsed(ai_jail_notice_started_at):
                    p.in_jail = True
                    p.position = game.board.jail_space_index
                    p.jail_turns = 0
                    game.pending_jail = None
                    ai_jail_notice_started_at = None
                    advance_to_next()
            else:
                if human_jail_notice_started_at is None:
                    human_jail_notice_started_at = pygame.time.get_ticks()

        elif game.pending_jail_turn:
            p = game.pending_jail_turn.get("player")
            draw_jail_turn_choice_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

            if p and is_ai_player(p):
                # Start timer (once)
                if ai_jail_turn_started_at is None:
                    ai_jail_turn_started_at = pygame.time.get_ticks()
                # After min read time, make the AI choice automatically
                elif elapsed(ai_jail_turn_started_at):
                    # --- Phase detection: early vs late game
                    props = [s for s in game.board.spaces if getattr(s, "type", "") == "Property"]
                    total_props = len(props) or 1
                    owned_props = sum(1 for s in props if getattr(s, "owner", None) is not None)
                    owned_ratio = owned_props / total_props
                    EARLY = owned_ratio < 0.50
                    forced_third = (p.jail_turns >= 2)

                    if EARLY:
                        if p.get_out_of_jail_free_cards > 0:
                            game.use_gojf_and_exit(p)
                        elif p.money >= 50:
                            game.pay_fine_and_exit(p)
                        else:
                            game.roll_for_doubles_from_jail(p)
                            rolled = (game.dice.die1_value, game.dice.die2_value)
                            is_doubles = (rolled[0] == rolled[1])
                            has_rolled = True
                            if p.in_jail:
                                advance_to_next()
                                ai_jail_turn_started_at = None
                    else:
                        if forced_third:
                            if p.get_out_of_jail_free_cards > 0:
                                game.use_gojf_and_exit(p)
                            elif p.money >= 50:
                                game.pay_fine_and_exit(p)
                            else:
                                game.roll_for_doubles_from_jail(p)
                                rolled = (game.dice.die1_value, game.dice.die2_value)
                                is_doubles = (rolled[0] == rolled[1])
                                has_rolled = True
                                if p.in_jail:
                                    advance_to_next()
                                    ai_jail_turn_started_at = None
                        else:
                            game.roll_for_doubles_from_jail(p)
                            rolled = (game.dice.die1_value, game.dice.die2_value)
                            is_doubles = (rolled[0] == rolled[1])
                            has_rolled = True
                            if p.in_jail:
                                advance_to_next()
                                ai_jail_turn_started_at = None

                    # Clear timer after acting
                    ai_jail_turn_started_at = None

            else:
                if human_jail_turn_started_at is None:
                    human_jail_turn_started_at = pygame.time.get_ticks()

        elif game.pending_debt:
            draw_debt_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_bankrupt_notice:
            draw_bankrupt_notice(screen, game, value_font, text_font, board_center[0], board_center[1])

            # Start timers if needed
            if ai_bankrupt_started_at is None:
                ai_bankrupt_started_at = pygame.time.get_ticks()
            if human_bankrupt_started_at is None:
                human_bankrupt_started_at = pygame.time.get_ticks()

            # AI auto-dismiss
            if elapsed(ai_bankrupt_started_at):
                game.pending_bankrupt_notice = None
                ai_bankrupt_started_at = None
            # Human: click handler already gates on ready(human_bankrupt_started_at)

        elif game.pending_trade and not trade_edit_open:
            # Draw the review; AI auto-decides after min read time below.
            acc_r, rej_r, ctr_r = draw_trade_review_modal(
                screen, game, value_font, text_font, board_center[0], board_center[1]
            )
            responder = game.pending_trade.get("responder")

            # Start minimum read timers
            if responder and is_ai_player(responder):
                if ai_trade_started_at is None:
                    ai_trade_started_at = pygame.time.get_ticks()

                elif elapsed(ai_trade_started_at):
                    # Simple AI policy: accept if favorable; else try a small mirrored counter; else reject
                    t = game.pending_trade
                    me = responder

                    # Determine my side in current pending offer
                    if me is t["left"]:
                        my_now = t["offer_left"]
                        opp_now = t["offer_right"]
                    else:
                        my_now = t["offer_right"]
                        opp_now = t["offer_left"]

                    # Accept if engine says it's >= 0 for me
                    try:
                        delta_for_me = game.rough_trade_delta_for(me)
                    except Exception:
                        delta_for_me = 0

                    if delta_for_me >= 0:
                        ok, msg = game.accept_trade()
                        print(msg)
                        ai_trade_started_at = None

                    else:
                        # Build a small counter by mirroring and nudging cash by -$50 on my side
                        new_offer_left  = dict(t["offer_right"])
                        new_offer_right = dict(t["offer_left"])

                        # If I was left in the current trade, in the mirrored counter I become right
                        my_counter_side = "right" if (me is t["left"]) else "left"

                        if my_counter_side == "left":
                            new_offer_left["cash"]  = int(new_offer_left.get("cash", 0)) - 50
                        else:
                            new_offer_right["cash"] = int(new_offer_right.get("cash", 0)) - 50

                        ok, msg = game.counter_trade(new_offer_left, new_offer_right)
                        print(msg)
                        ai_trade_started_at = None
                    
                    # Block fresh trades by either side for the rest of this turn
                    t2 = game.pending_trade or t  # if trade closed, use last known t
                    left_p, right_p = t2["left"], t2["right"]
                    if hasattr(game, "_trade_attempted_this_turn"):
                        game._trade_attempted_this_turn.update({ left_p, right_p })

            else:
                if human_trade_started_at is None:
                    human_trade_started_at = pygame.time.get_ticks()

        elif selected_space is not None:
            property_characteristic(screen, selected_space, board_size, screen_height)

        if manage_select_open:
            draw_manage_select_modal(
                screen, game.players[player_idx], game.board,
                board_center[0], board_center[1]
            )

        if trade_select_open:
            draw_trade_select_modal(screen, game.players, trade_selected, board_center[0], board_center[1])

        if trade_edit_open and trade_pair is not None:
            iL, iR = trade_pair
            trade_editor_rects = draw_trade_editor_modal(
                screen,
                game.players[iL], game.players[iR],
                trade_offer,
                board_center[0], board_center[1]
            )
        
        else:
            # Ensure stale rects are cleared when the editor closes
            trade_editor_rects = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # names_or_count = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    # if isinstance(names_or_count, list):
    #     player_names = names_or_count
    # else:
    #     # fallback: old flow where only number was returned
    #     player_names = [f"Player {i+1}" for i in range(int(names_or_count))]

    # player_names = ["AI 1", "Troy", "Thomas", "Tenzin"]
    player_names = ["AI 1", "AI 2", "AI 3", "AI 4"]
    running_display(player_names, popup_delay_ms=0)

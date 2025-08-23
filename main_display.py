import pygame
import sys
import os
import ctypes

import dice
from board_test import *
import title_screen
import player_cards
from game_test import Game

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

def running_display(player_names: list[str]):
    game = Game(player_names=player_names)

    # --- Centered roll-off with per-player delay, full order display, and tie re-roll for first place ---
    def roll_for_first(game, screen, board_center, value_font):
        import pygame
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

        # Break ties for FIRST place only (keep re-rolling tied-top until unique)
        def break_top_tie():
            nonlocal roll_sum
            while True:
                top = max(roll_sum.values())
                tied = [p for p, s in roll_sum.items() if s == top]
                if len(tied) <= 1:
                    return
                # re-roll only the players tied for top; show mini sequence
                mini_rows = []
                draw_round(round_rows, "Tie! Re-rolling tied players…")
                pygame.time.delay(900)
                for p in tied:
                    s, _ = game.dice.roll()
                    roll_sum[p] = s
                    mini_rows.append((p.name, s))
                    # show the re-rolls right in the center (fresh view)
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
                    pygame.time.delay(900)

        break_top_tie()

        # Build final turn order: sort by roll_sum desc, stable for non-top ties
        ordered_players = sorted(players_in_order, key=lambda p: roll_sum[p], reverse=True)
        ordered_rows = [(p.name, roll_sum[p]) for p in ordered_players]

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

    # Assign player colors in the new order so UI reflects turn order
    for i, player in enumerate(game.players):
        player.color = player_colors[i % len(player_colors)]

    running = True
    rolled = None

    doubles_rolled = []
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
        if len(game.players) == 0:
            return
        # Step to next player
        player_idx = (player_idx + 1) % len(game.players)
        # Reset per-turn flags
        rolled = None
        is_doubles = False
        has_rolled = False
        # Keep the Game object’s index in sync in case any logic reads it
        game.current_player_index = player_idx
        # If next player is in jail, open their jail-turn modal immediately
        nxt = game.players[player_idx]
        if nxt.in_jail and not game.pending_jail_turn:
            game.start_jail_turn(nxt)

    while running:
        # Check if any popups are going to happen
        def any_modal_open():
            return (
                game.pending_purchase or game.pending_rent or game.pending_tax or
                game.pending_build or game.pending_jail or game.pending_jail_turn or
                game.pending_debt or trade_select_open or trade_edit_open or
                manage_select_open
            )


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
                        # Close the app (or you could jump back to a title screen if you have one)
                        running = False
                    continue

                # Show the Chance/ CC Card
                if game.last_drawn_card:
                    pending_card = game.pending_card
                    game.last_drawn_card = None
                    game.pending_card = None

                    # Execute the card effect
                    if pending_card:
                        card = pending_card["card"]
                        player_card = pending_card["player"]
                        card.execute(player_card, game)

                        # Move the card drawn to the bottom of the deck
                        if pending_card["type"] == "Chance":
                            game.chance_cards.append(card)
                        else:
                            game.community_chest_cards.append(card)

                    continue

                # Rent
                if game.pending_rent:
                    cx, cy = board_center
                    pay_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                    if pay_rect.collidepoint(mouse_pos):
                        game.settle_rent()

                    # block all other clicks while modal is visible
                    continue

                # Tax
                if game.pending_tax:
                    cx, cy = board_center
                    pay_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                    if pay_rect.collidepoint(mouse_pos):
                        game.confirm_tax()
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
                    # block other clicks while this modal is open
                    continue

                # If a purchase is pending, only handle BUY / SKIP clicks
                if game.pending_purchase:
                    buy_rect, skip_rect = purchase_button_rects(board_center[0], board_center[1] + 55)
                    affordable = game.pending_purchase.get("affordable", True)

                    if buy_rect.collidepoint(mouse_pos):
                        if affordable:   # ignore clicks if not affordable (greyed out)
                            game.confirm_purchase(True)

                    elif skip_rect.collidepoint(mouse_pos):
                        game.confirm_purchase(False)

                    continue
                
                # Jail popup
                if game.pending_jail:
                    cx, cy = board_center
                    ok_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                    if ok_rect.collidepoint(mouse_pos):
                        # Now send the player to Jail
                        p = game.pending_jail["player"]
                        p.in_jail = True
                        p.position = game.board.jail_space_index
                        p.jail_turns = 0
                        print(f"{p.name} has been moved to Jail.")
                        game.pending_jail = None

                        # Advance to next player so the jail-choice modal won't appear this turn
                        advance_to_next()
                    continue

                # Jail-turn choice modal blocks everything else
                if game.pending_jail_turn:
                    cx, cy = board_center
                    # Recreate rects for hit-testing to match the draw function layout
                    rects = draw_jail_turn_choice_modal(
                        screen, game, value_font, text_font, cx, cy
                    )
                    r_use, r_pay, r_roll = rects["use"], rects["pay"], rects["roll"]
                    p = game.pending_jail_turn["player"]
                    if r_use and r_use.collidepoint(mouse_pos):
                        game.use_gojf_and_exit(p)
                        # player is now free; keep their turn so they can roll from space 10
                        rolled = None
                        is_doubles = False
                        has_rolled = False
                        continue

                    if r_pay and r_pay.collidepoint(mouse_pos):
                        game.pay_fine_and_exit(p)
                        # player is now free; keep their turn so they can roll from space 10
                        rolled = None
                        is_doubles = False
                        has_rolled = False
                        continue
                    if r_roll and r_roll.collidepoint(mouse_pos):
                        game.roll_for_doubles_from_jail(p)
                        # If still in jail, their turn ends immediately; advance to next player
                        rolled = (game.dice.die1_value, game.dice.die2_value)
                        is_doubles = (rolled[0] == rolled[1])
                        has_rolled = True
                        if p.in_jail:
                            player_idx = (player_idx + 1) % len(game.players)
                            is_doubles = False
                            has_rolled = False
                            nxt = game.players[player_idx]
                            if nxt.in_jail and not game.pending_jail_turn:
                                game.start_jail_turn(nxt)
                        # If freed, they've already rolled & moved; let normal flow continue (may trigger other modals)
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
                    if ok_rect and ok_rect.collidepoint(mouse_pos):
                        # Just dismiss. Do NOT advance here—flags were handled on click.
                        game.pending_bankrupt_notice = None
                    continue

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

                    # Property checkboxes: look for any key starting with "box_"
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
                            ok, msg = game.execute_trade(
                                game.players[iL], game.players[iR],
                                {"cash": trade_offer["left"]["cash"],  "gojf": trade_offer["left"]["gojf"],  "props": left_props},
                                {"cash": trade_offer["right"]["cash"], "gojf": trade_offer["right"]["gojf"], "props": right_props},
                            )
                            print(msg)
                            # Reset UI regardless; if failed, user can re-open and try again.
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
                
                # If you have haven't rolled yet or you have doubles, you can yoll again
                if (not has_rolled or is_doubles) and not player.in_jail:
                    roll_total, is_doubles = game.dice.roll()
                    has_rolled = True
                    rolled = (game.dice.die1_value, game.dice.die2_value)
                    player.move(roll_total, game.board)

                # What the do if there are doubles 
                if is_doubles:
                    player.doubles_rolled_consecutive += 1
                    if player.doubles_rolled_consecutive == 3:
                        print(f"{player.name} rolled 3 doubles! Go to jail.")
                        game.pending_jail = {"player": player}
                        player.doubles_rolled_consecutive = 0
                        rolled = None
                        is_doubles = False
                        has_rolled = False
                        advance_to_next()                
                else:
                    player.doubles_rolled_consecutive = 0

        # ----Dev Testing------
        # game.players[0].properties_owned = [game.board.spaces[i] for i in [1, 3, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 34, 35, 37, 39]]
        # for prop in game.players[0].properties_owned:
        #     prop.owner = game.players[0]
        #     prop.num_houses = 4

        # Draw the Board
        space_rects = board_game(screen, text_font, board_size, corner_size, space_size)
        draw_mortgage_badges(screen, game, space_rects)

        game.current_player_index = player_idx
        current_player = game.players[player_idx]

        enable_dice = ((not has_rolled or is_doubles) and not current_player.in_jail)

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

        # Show what chance card the player gets 
        if game.last_drawn_card:
            display_card(screen, game.players[player_idx], game.last_drawn_card, board_size, screen_height)

        # Display dice roll and total 
        if rolled:
            dice.draw_dice(screen, rolled, circ_center[0] - 200, circ_center[1] - 200)
            dice.draw_total(screen, rolled, circ_center[0], circ_center[1] - 350, value_font)

            if is_doubles:
                doubles_text = value_font.render("You rolled doubles!", True, (0, 0, 0))
                screen.blit(doubles_text, (circ_center[0] - doubles_text.get_width()//2, circ_center[1] - 300)) # 100

            if len(doubles_rolled) >= 3:
                jail_text = value_font.render("Too Many Doubles Rolled, Go To Jail", True, (255, 0, 0))
                screen.blit(jail_text, (circ_center[0] - jail_text.get_width()//2, circ_center[1] - 250))    # 150
         
        # If there is a pending display, draw one of them 

        if game.game_over:
            cx, cy = board_center
            draw_winner_modal(screen, game, value_font, value_font, cx, cy)

        elif game.pending_purchase:
            draw_purchase_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_rent: 
            draw_rent_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_build:
            draw_build_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_tax:
            draw_tax_modal(screen, game, value_font, text_font, board_center[0], board_center[1])
        
        elif game.pending_jail:
            draw_jail_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_jail_turn:
            draw_jail_turn_choice_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_debt:
            draw_debt_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_bankrupt_notice:           
            draw_bankrupt_notice(screen, game, value_font, text_font,
                         board_center[0], board_center[1])

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
    names_or_count = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    if isinstance(names_or_count, list):
        player_names = names_or_count
    else:
        # fallback: old flow where only number was returned
        player_names = [f"Player {i+1}" for i in range(int(names_or_count))]
    running_display(player_names)

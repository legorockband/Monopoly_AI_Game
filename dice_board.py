import pygame
import sys
import os
import ctypes

import dice
import board_test
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
space_size = (board_size - 1.9 * corner_size) // 9
circ_center = (board_size + (screen_width - board_size)//2, 375)

circ_rad = 50
circ_color = (255, 0, 0)

player_colors = [(0,0,255), (0,255,0), (255,0,0), (0, 255, 255)]

board_center = (board_size//2, board_size//2)

def running_display(num_players: int):
    game = Game(player_names=[f"Player {i+1}" for i in range(num_players)])
    for i, player in enumerate(game.players):
        player.color = player_colors[i % len(player_colors)]

    running = True
    rolled = None

    doubles_rolled = []
    is_doubles = False
    has_rolled = False

    player_idx = 0
    selected_space = None

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
        return has_rolled and (not is_doubles) and not (game.pending_build or game.pending_rent or game.pending_purchase or game.last_drawn_card)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

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
                        info = game.pending_rent
                        debtor, owner, amount = info["player"], info["owner"], info["amount"]
                        debtor.pay_money(amount)
                        owner.collect_money(amount)
                        game.pending_rent = None

                    # block all other clicks while modal is visible
                    continue

                # Tax
                if game.pending_tax:
                    cx, cy = board_center
                    pay_rect = pygame.Rect(cx - 55, cy + 30, 110, 44)
                    if pay_rect.collidepoint(mouse_pos):
                        game.confirm_tax()
                    continue

                # If BUILD modal is up: only allow HOUSE / HOTEL / SKIP
                if game.pending_build:
                    cx, cy = board_center
                    r_house = pygame.Rect(cx - 180, cy + 50, 120, 44)
                    r_hotel = pygame.Rect(cx - 60,  cy + 50, 120, 44)
                    r_skip  = pygame.Rect(cx + 60,  cy + 50, 120, 44)

                    can_house = game.pending_build["can_house"]
                    can_hotel = game.pending_build["can_hotel"]

                    if r_house.collidepoint(mouse_pos) and can_house:
                        game.confirm_build("house")

                    elif r_hotel.collidepoint(mouse_pos) and can_hotel:
                        game.confirm_build("hotel")

                    elif r_skip.collidepoint(mouse_pos):
                        game.confirm_build("skip")

                    continue

                # If a purchase is pending, only handle BUY / SKIP clicks
                if game.pending_purchase:
                    buy_rect, skip_rect = board_test.purchase_button_rects(board_center[0], board_center[1] + 55)
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
                    continue

                if selected_space is not None:
                    selected_space = None
                    continue

                if space_rects:  # populated below each frame
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
                    btn_rects, confirm_rect, cancel_rect = board_test.draw_trade_select_modal(
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

                # --- Trade button click (only when no other modals are up) ---
                if trade_rect and trade_rect.collidepoint(mouse_pos):
                    trade_select_open = True
                    trade_selected.clear()
                    continue

                # End Turn button click
                if end_rect and end_rect.collidepoint(mouse_pos):
                    if can_end_turn():
                        player_idx = (player_idx + 1) % num_players
                        rolled = None
                        is_doubles = False
                        has_rolled = False
                    continue

                if not dice.is_inside_circle(mouse_pos, circ_center, circ_rad):
                    continue
               
                player = game.players[player_idx]
                
                if player.in_jail:
                    game.handle_jail_turn(player)
                    if not player.in_jail and not (game.pending_purchase or game.pending_rent or game.pending_build):                      
                        player_idx = (player_idx + 1) % num_players
                    continue
                
                # If you have haven't rolled yet or you have doubles, you can yoll again
                if not has_rolled or is_doubles:
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
                        player_idx = (player_idx + 1) % num_players
                
                else:
                    player.doubles_rolled_consecutive = 0

        # Give Player 1 all properties
        # game.players[0].properties_owned = [game.board.spaces[i] for i in [1, 3, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 34, 35, 37, 39]]
        # for prop in game.players[0].properties_owned:
        #     prop.owner = game.players[0]
        #     prop.num_houses = 4

        # Draw the Board
        space_rects = board_test.board_game(screen, text_font, board_size, corner_size, space_size)

        # Make interactable buttons
        dice.make_dice_button(screen, circ_color, circ_center, circ_rad, enable=(not has_rolled or is_doubles))
        end_rect = board_test.end_turn_button(screen, value_font, circ_center, enable=can_end_turn())
        trade_rect = board_test.trade_button(screen, value_font, circ_center, enable=True)                

        # Draw the houses or hotels 
        board_test.draw_property_build_badges(screen, game, space_rects)

        board_test.move_player(screen, game.players, board_size, corner_size, space_size)
        
        # Show the player stats
        player_cards.create_player_card(screen, game.players, player_idx, board_size, space_size, screen_width, screen_height)

        # Show what chance card the player gets 
        if game.last_drawn_card:
            board_test.display_card(screen, game.players[player_idx - 1], game.last_drawn_card, board_size, screen_height)

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
        if game.pending_purchase:
            board_test.draw_purchase_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_rent: 
            board_test.draw_rent_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_build:
            board_test.draw_build_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif game.pending_tax:
            board_test.draw_tax_modal(screen, game, value_font, text_font, board_center[0], board_center[1])
        
        elif game.pending_jail:
            board_test.draw_jail_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        elif selected_space is not None:
            board_test.property_characteristic(screen, selected_space, board_size, screen_height)
        
        if trade_select_open:
            board_test.draw_trade_select_modal(screen, game.players, trade_selected, board_center[0], board_center[1])

        if trade_edit_open and trade_pair is not None:
            iL, iR = trade_pair
            trade_editor_rects = board_test.draw_trade_editor_modal(
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
    #num_players = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    num_players = 4
    running_display(num_players)
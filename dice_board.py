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
                    roll_total = 30
                    player.move(roll_total, game.board)

                    sp = game.board.spaces[player.position]
                    if getattr(sp, "type", "") == "GoToJail":
                        board_test.jail_tax_display(screen, player, sp, board_size, screen_height)

                # What the do if there are doubles 
                if is_doubles:
                    player.doubles_rolled_consecutive += 1
                    if player.doubles_rolled_consecutive == 3:
                        print(f"{player.name} rolled 3 doubles! Go to jail.")
                        player.in_jail = True
                        player.position = game.board.jail_space_index
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

        elif selected_space is not None:
            board_test.property_characteristic(screen, selected_space, board_size, screen_height)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    #num_players = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    num_players = 4
    running_display(num_players)
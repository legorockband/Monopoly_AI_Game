import pygame
import sys
import os
import ctypes

import dice
import board_test
import title_screen
import player_cards
from game_test import Game, Board

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
## Properties of the board
board_size = int(min(screen_height, (5/8) * screen_width))
corner_size = board_size // 7
space_size = (board_size - 1.9 * corner_size) // 9
circ_center = (board_size + (screen_width - board_size)//2, 375)

circ_rad = 50
circ_color = (255, 0, 0)

player_colors = [(0,0,255), (0,255,0), (255,0,0), (0, 255, 255)]

board_center = (board_size//2, board_size//2)

# Helper Functions
def purchase_button_rects(cx, cy):
    w, h = 110, 44
    gap = 30
    buy = pygame.Rect(cx - w - gap//2, cy - h//2, w, h)
    skip = pygame.Rect(cx + gap//2, cy - h//2, w, h)
    return buy, skip

def draw_purchase_modal(screen, game, title_font, body_font, center_x, center_y):
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

def running_display(num_players: int):
    game = Game(player_names=[f"Player {i+1}" for i in range(num_players)])
    for i, player in enumerate(game.players):
        player.color = player_colors[i % len(player_colors)]

    running = True
    rolled = None

    doubles_rolled = []
    is_doubles = False

    player_idx = 0

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

                        if pending_card["type"] == "Chance":
                            game.chance_cards.append(card)
                        else:
                            game.community_chest_cards.append(card)

                    continue

                ## If a purchase is pending, only handle BUY / SKIP clicks
                if game.pending_purchase:
                    buy_rect, skip_rect = purchase_button_rects(board_center[0], board_center[1] + 55)
                    affordable = game.pending_purchase.get("affordable", True)

                    if buy_rect.collidepoint(mouse_pos):
                        if affordable:   # ignore clicks if not affordable (greyed out)
                            game.confirm_purchase(True)
                            # advance turn if no doubles
                            if not is_doubles:
                                player_idx = (player_idx + 1) % num_players
                    elif skip_rect.collidepoint(mouse_pos):
                        game.confirm_purchase(False)
                        if not is_doubles:
                            player_idx = (player_idx + 1) % num_players
                    continue
                
                if not dice.is_inside_circle(mouse_pos, circ_center, circ_rad):
                    continue
                player = game.players[player_idx]
                
                if player.in_jail:
                    game.handle_jail_turn(player)
                    if not player.in_jail and not game.pending_purchase:
                        player_idx = (player_idx + 1) % num_players
                    continue
     
                roll_total, is_doubles = game.dice.roll()
                rolled = (game.dice.die1_value, game.dice.die2_value)

                player.move(roll_total, game.board)

                if is_doubles:
                    player.doubles_rolled_consecutive += 1
                    if player.doubles_rolled_consecutive == 3:
                        print(f"{player.name} rolled 3 doubles! Go to jail.")
                        player.in_jail = True
                        player.position = game.board.jail_space_index
                        player.doubles_rolled_consecutive = 0
                        player_idx = (player_idx + 1) % num_players
                else:
                    player.doubles_rolled_consecutive = 0
                    if not game.pending_purchase:
                        player_idx = (player_idx + 1) % num_players

        # # Give Player 1 the properties at spaces 1, 3, 6, 8 (Mediterranean, Baltic, Oriental, Vermont)
        # game.players[0].properties_owned = [game.board.spaces[i] for i in [1, 3, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 34, 35, 37, 39]]
        # for prop in game.players[0].properties_owned:
        #     prop.owner = game.players[0]

        board_test.board_game(screen, text_font, board_size, corner_size, space_size)

        ## Make a button 
        dice.make_dice_button(screen, circ_color, circ_center, circ_rad)

        board_test.move_player(screen, game.players, board_size, corner_size, space_size)

        player_cards.create_player_card(screen, game.players, player_idx, board_size, space_size, screen_width, screen_height)

        # Show what chance card the player gets 
        if game.last_drawn_card:
            board_test.display_card(screen, game.players[player_idx - 1], game.last_drawn_card, board_size, screen_height)

        ## Display dice roll and total 
        if rolled:
            dice.draw_dice(screen, rolled, circ_center[0] - 200, circ_center[1] - 200)
            dice.draw_total(screen, rolled, circ_center[0], circ_center[1] - 350, value_font)

            if is_doubles:
                doubles_text = value_font.render("You rolled doubles!", True, (0, 0, 0))
                screen.blit(doubles_text, (circ_center[0] - doubles_text.get_width()//2, circ_center[1] - 300)) # 100

            if len(doubles_rolled) >= 3:
                jail_text = value_font.render("Too Many Doubles Rolled, Go To Jail", True, (255, 0, 0))
                screen.blit(jail_text, (circ_center[0] - jail_text.get_width()//2, circ_center[1] - 250))    # 150
         
        if game.pending_purchase:
            draw_purchase_modal(screen, game, value_font, text_font, board_center[0], board_center[1])

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    #num_players = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    num_players = 4
    running_display(num_players)
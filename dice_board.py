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

## Properties of the board
board_size = int(min(screen_height, (5/8) * screen_width))
corner_size = board_size // 7
space_size = (board_size - 1.9 * corner_size) // 9
circ_center = (board_size + (screen_width - board_size)//2, 375)

circ_rad = 50
circ_color = (255, 0, 0)

player_colors = [(0,0,255), (0,255,0), (255,0,0), (0, 255, 255)]

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

                ## If the mouse clicks on the button roll the dice
                if dice.is_inside_circle(mouse_pos, circ_center, circ_rad):
                    player = game.players[player_idx]
                    
                    if player.in_jail:
                        game.handle_jail_turn(player)
                        if not player.in_jail:
                            player_idx = (player_idx) + 1 % num_players
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
                        player.doubles_rolled_consecutive =0
                        player_idx = (player_idx + 1) % num_players

        board_test.board_game(screen, text_font, board_size, corner_size, space_size)

        ## Make a button 
        dice.make_dice_button(screen, circ_color, circ_center, circ_rad)

        board_test.move_player(screen, game.players, board_size, corner_size, space_size)

        # Test player 2 money value
        # game.players[1].money = 500
        game.players[0].properties_owned = [0, 2, 5]   # Player 1 owns MA, BA, OA
        game.players[1].properties_owned = [10, 11]    # Player 2 owns SCP, EC

        player_cards.create_player_card(screen, game.players, player_idx, board_size, space_size, screen_width, screen_height)

        # board_test.display_card(screen, chance[0], board_size, screen_height)

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
           

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    #num_players = title_screen.run_title_screen(screen, clock, screen_width, screen_height)
    num_players = 4
    running_display(num_players)

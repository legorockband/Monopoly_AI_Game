import pygame

# Display the a large player card for the current player 

card_font = pygame.font.SysFont(None, 24)

def create_player_card(screen: pygame.Surface, idx_player: int, board_size: int, space_size: int, screen_width: int, screen_height: int):
    card_width = screen_width - board_size
    card_height = space_size * 3
    starting_pos = 475

    # Large card for the current 
    pygame.draw.rect(screen, (0,0,0), (board_size, starting_pos, card_width, card_height), 2)
    
    # TODO: Change this to each players specific number
    money_value = 1000

    money_text = card_font.render(f"Money: ${money_value}", True, (0, 255, 0))
    screen.blit(money_text, (board_size + 10, starting_pos + 10))


    # match idx_player:
    #     case 1:
            
    #     case 2:

    #     case 3:

    #     case 4:

    #     case 5:

    #     case 6:

    #     case _:
    #         raise ValueError("Unknown Player")
    
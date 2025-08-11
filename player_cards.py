import pygame
from game_test import Player


# Display the a large player card for the current player 

card_font = pygame.font.SysFont(None, 24)
value_font = pygame.font.SysFont('Arial', 30)

def create_player_card(screen: pygame.Surface, player:list[Player], player_idx:int, board_size: int, space_size: int, screen_width: int, screen_height: int):
    card_width = screen_width - board_size
    card_height = space_size * 3
    starting_pos = 475

    current_player = player[player_idx]
    money_value = current_player.money
    property_owned = current_player.properties_owned

    # Large card for the current 
    pygame.draw.rect(screen, (0,0,0), (board_size, starting_pos, card_width, card_height), 2)
    
    # Current Players Turn
    turn_text = value_font.render(f"{current_player.name}'s Turn", True, current_player.color)
    screen.blit(turn_text, (board_size + 10, starting_pos))

    # Money Total for the current player
    money_text = card_font.render(f"- Money: ${money_value}", True, (0, 255, 0))
    screen.blit(money_text, (board_size + 10, starting_pos + 45))
    
    # Render properties line-by-line
    for idx, prop in enumerate(property_owned):
        prop_name = prop.name

        if hasattr(prop, "cost") and isinstance(prop.cost, int):
            cost_text = f" (${prop.cost})"
        else:
            cost_text = ""
        text_color = (0, 0, 0)

        line_text = card_font.render(f"- {prop_name}{cost_text}", True, text_color)
        screen.blit(line_text, (board_size + 10, starting_pos + 75 + idx * 20))
        


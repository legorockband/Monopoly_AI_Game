# title_screen.py
import pygame
import sys

def run_title_screen(screen, clock, screen_width, screen_height):
    pygame.font.init()
    input_active = False
    user_text = ''
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    button_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 40, 300, 80)

    while True:
        screen.fill((20, 20, 40))

        title_text = font_large.render("Monopoly", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 150))

        pygame.draw.rect(screen, (0, 120, 215), button_rect)
        button_text = font_small.render("Number of Players", True, (255, 255, 255))
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                  button_rect.centery - button_text.get_height() // 2))

        if input_active:
            input_text = font_small.render("Enter number of players (2-6): " + user_text, True, (255, 255, 255))
            screen.blit(input_text, (screen_width // 2 - input_text.get_width() // 2, screen_height // 2 + 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    input_active = True
                    user_text = ''

            if input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_text.isdigit():
                        num = int(user_text)
                        if 2 <= num <= 6:
                            return num
                        else:
                            user_text = ''
                    else:
                        user_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.unicode.isdigit():
                    user_text += event.unicode

        pygame.display.flip()
        clock.tick(60)

# title_screen.py
import pygame
import sys

def run_title_screen(screen, clock, screen_width, screen_height):
    pygame.font.init()
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    font_input = pygame.font.SysFont(None, 32)

    # States
    picking_count = True
    showing_rules = False
    input_active = False
    user_text = ''

    button_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 40, 300, 80)
    rules_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 80, 200, 60)

    # When moving to name entry
    num_players = None
    name_boxes = []
    active_box = 0  # index of focused box

    def make_name_boxes(n):
        boxes = []
        start_y = screen_height // 2 - (n * 60) // 2
        for i in range(n):
            rect = pygame.Rect(screen_width // 2 - 200, start_y + i * 60, 400, 44)
            boxes.append({"rect": rect, "text": f"Player {i+1}"})
        return boxes

    while True:
        screen.fill((20, 20, 40))
        title_text = font_large.render("Monopoly", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 120))

        if picking_count:
            # Main menu
            if not showing_rules:
                pygame.draw.rect(screen, (0, 120, 215), button_rect)
                button_text = font_small.render("Number of Players", True, (255, 255, 255))
                screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                          button_rect.centery - button_text.get_height() // 2))

                pygame.draw.rect(screen, (200, 120, 0), rules_button_rect)
                rules_text = font_small.render("Rules", True, (255, 255, 255))
                screen.blit(rules_text, (rules_button_rect.centerx - rules_text.get_width() // 2,
                                         rules_button_rect.centery - rules_text.get_height() // 2))

                if input_active:
                    input_text = font_small.render("Enter number of players (2-4): " + user_text, True, (255, 255, 255))
                    screen.blit(input_text, (screen_width // 2 - input_text.get_width() // 2, button_rect.bottom + 120))

            else:
                # Rules modal
                modal_w, modal_h = screen_width - 200, screen_height - 200
                modal_rect = pygame.Rect(100, 100, modal_w, modal_h)
                pygame.draw.rect(screen, (240, 240, 220), modal_rect)
                pygame.draw.rect(screen, (0, 0, 0), modal_rect, 2)
                rules = [
                    "Monopoly Rules (Simplified):",
                    "- Roll dice and move clockwise around the board.",
                    "- Buy properties you land on if unowned.",
                    "- Pay rent when landing on other players' properties.",
                    "- Collect $200 each time you pass GO.",
                    "- Build when you own a full color set.",
                    "- Go to Jail on 'Go To Jail' or 3 doubles.",
                    "- Trade cash, properties, Get Out of Jail Free cards.",
                    "- Last player not bankrupt wins!",
                ]
                y = 120
                for line in rules:
                    txt = font_small.render(line, True, (0, 0, 0))
                    screen.blit(txt, (120, y))
                    y += 40
                back_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 120, 150, 50)
                pygame.draw.rect(screen, (200, 0, 0), back_rect)
                back_text = font_small.render("Back", True, (255, 255, 255))
                screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2,
                                        back_rect.centery - back_text.get_height() // 2))

        else:
            # Name entry screen
            prompt = font_small.render(f"Enter player names (max 10 characters):", True, (255, 255, 255))
            screen.blit(prompt, (screen_width // 2 - prompt.get_width() // 2, 180))

            for i, box in enumerate(name_boxes):
                rect = box["rect"]
                focused = (i == active_box)
                pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=6)
                pygame.draw.rect(screen, (0, 120, 215) if focused else (0, 0, 0), rect, 2, border_radius=6)
                label = font_input.render(box["text"], True, (0, 0, 0))
                screen.blit(label, (rect.x + 10, rect.y + (rect.height - label.get_height()) // 2))

            # Start button
            start_rect = pygame.Rect(screen_width // 2 - 100, name_boxes[-1]["rect"].bottom + 40, 200, 50)
            pygame.draw.rect(screen, (0, 170, 0), start_rect, border_radius=10)
            start_lbl = font_small.render("Start Game", True, (255, 255, 255))
            screen.blit(start_lbl, (start_rect.centerx - start_lbl.get_width() // 2,
                                    start_rect.centery - start_lbl.get_height() // 2))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if picking_count:
                if not showing_rules:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(event.pos):
                            input_active = True
                            user_text = ''
                        elif rules_button_rect.collidepoint(event.pos):
                            showing_rules = True

                    if input_active and event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if user_text.isdigit():
                                num = int(user_text)
                                if 2 <= num <= 4:
                                    num_players = num
                                    name_boxes = make_name_boxes(num_players)
                                    picking_count = False  # go to name entry
                                user_text = ''
                            else:
                                user_text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                        elif event.unicode.isdigit():
                            user_text += event.unicode

                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        back_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 120, 150, 50)
                        if back_rect.collidepoint(event.pos):
                            showing_rules = False

            else:
                # Name entry interactions
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, box in enumerate(name_boxes):
                        if box["rect"].collidepoint(event.pos):
                            active_box = i
                            break
                    start_rect = pygame.Rect(screen_width // 2 - 100, name_boxes[-1]["rect"].bottom + 40, 200, 50)
                    if start_rect.collidepoint(event.pos):
                        # sanitize names & return
                        names = []
                        for i, box in enumerate(name_boxes):
                            text = box["text"].strip()[:10]  # cap at 10
                            if not text:
                                text = f"Player {i+1}"
                            names.append(text)
                        return names  # <— NEW: return list of names

                if event.type == pygame.KEYDOWN:
                    # typing into the active box
                    if event.key == pygame.K_TAB:
                        active_box = (active_box + 1) % len(name_boxes)
                    elif event.key == pygame.K_RETURN:
                        active_box = (active_box + 1) % len(name_boxes)
                    elif event.key == pygame.K_BACKSPACE:
                        name_boxes[active_box]["text"] = name_boxes[active_box]["text"][:-1]
                    else:
                        ch = event.unicode
                        if ch and ch.isprintable() and ch != '\r' and ch != '\n':
                            if len(name_boxes[active_box]["text"]) < 10:  # 10-char limit
                                name_boxes[active_box]["text"] += ch

        pygame.display.flip()
        clock.tick(60)

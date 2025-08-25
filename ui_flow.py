# ui_flow.py
import pygame

def is_ai_player(p):
    return isinstance(getattr(p, "name", None), str) and p.name.strip().lower().startswith("ai")

class JailHelpers:
    """Encapsulate jail modal bookkeeping used by main_display."""
    def __init__(self, game, same_player_fn):
        self.game = game
        self._same = same_player_fn

    def jail_notice_for(self, cur):
        if not cur: return None
        for j in self.game.pending_jail:
            if self._same(j.get("player"), cur):
                return j
        return None

    def jail_turn_for(self, p):
        if not p: return None
        for j in self.game.pending_jail_turn:
            if self._same(j.get("player"), p):
                return j
        return None

    def remove_jail_notice_for(self, p):
        self.game.pending_jail = [j for j in self.game.pending_jail
                                  if not self._same(j.get("player"), p)]

    def remove_jail_turn_for(self, p):
        self.game.pending_jail_turn = [j for j in self.game.pending_jail_turn
                                       if not self._same(j.get("player"), p)]

def roll_for_first(game, screen, screen_width, screen_height, value_font):
    """
    Your 'rolling for turn order…' screen pulled intact from main_display,
    with small parameterization so main_display just calls this.
    """
    players_in_order = list(game.players)
    roll_sum = {p: None for p in players_in_order}

    def draw_round(rows, subtitle=None):
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

    # First round
    round_rows = []
    for p in players_in_order:
        s, _ = game.dice.roll()
        roll_sum[p] = s
        round_rows.append((p.name, s))
        draw_round(round_rows)
        pygame.time.delay(1000)

    # Break ties locally
    def break_local_ties():
        nonlocal roll_sum
        score_to_players = {}
        for p, s in roll_sum.items():
            base = int(s)
            score_to_players.setdefault(base, []).append(p)

        for base_score in sorted(score_to_players.keys(), reverse=True):
            group = score_to_players[base_score]
            if len(group) <= 1:
                continue
            while True:
                draw_round(round_rows, f"Tie at {base_score}. Re-rolling tied players…")
                pygame.time.delay(1000)
                new_vals = {}
                mini_rows = []
                for p in group:
                    s_new, _ = game.dice.roll()
                    new_vals[p] = s_new
                    mini_rows.append((p.name, s_new))
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
                    pygame.time.delay(1000)

                counts = {}
                for v in new_vals.values():
                    counts[v] = counts.get(v, 0) + 1
                if all(c == 1 for c in counts.values()):
                    ordered_group = sorted(group, key=lambda p: new_vals[p], reverse=True)
                    n = len(ordered_group)
                    for rank, p in enumerate(ordered_group):
                        eps = (n - rank) / 100.0
                        roll_sum[p] = base_score + eps
                    break

    break_local_ties()
    ordered = sorted(players_in_order, key=lambda p: roll_sum[p], reverse=True)
    ordered_rows = [(p.name, int(roll_sum[p])) for p in ordered]

    # Show final order
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
    return ordered
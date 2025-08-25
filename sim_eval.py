# sim_eval.py
import argparse, csv, random, time
from collections import Counter
from game import Game
from ai_mcts import MCTSMonopolyBot, ActionModel, mcts_decide

# --- Simple scripted "human proxy" opponents -------------------------------
class BuyAllBot:      # always buys if it can; never trades
    name = "BuyAll"
class CautiousBot:    # keeps big cash buffer; under-builds
    name = "Cautious"
class GreedyBuilder:  # builds aggressively; risks cash crunch
    name = "Greedy"

def is_ai(p): return str(getattr(p, "name", "")).lower().startswith("ai")

def resolve_all_modals(game, current):
    """Resolve Chance/CC, tax, rent, jail notices, debt, and purchase/build.
       This mirrors your UI auto-resolution so sims can run headless."""
    changed = True
    while changed:
        changed = False

        # Card popups
        if getattr(game, "last_drawn_card", None):
            pending = game.pending_card
            game.last_drawn_card = None; game.pending_card = None
            if pending:
                card, player = pending["card"], pending["player"]
                card.execute(player, game)
                (game.chance_cards if pending["type"]=="Chance" else game.community_chest_cards).append(card)
            changed = True; continue

        # Rent
        if getattr(game, "pending_rent", None):
            game.settle_rent()
            changed = True; continue

        # Tax
        if getattr(game, "pending_tax", None):
            game.confirm_tax()
            changed = True; continue

        # Go to Jail notice
        if getattr(game, "pending_jail", None):
            p = game.pending_jail["player"]
            p.in_jail = True
            p.position = game.board.jail_space_index
            p.jail_turns = 0
            game.pending_jail = None
            changed = True; continue

        # Debt handling (AI-like priority path)
        if getattr(game, "pending_debt", None):
            info = game.pending_debt; p = info["player"]; amt = info["amount"]; cred = info.get("creditor")
            if p.money >= amt:
                p.pay_money(amt); 
                if cred: cred.collect_money(amt)
                game.clear_debt()
                changed = True; continue
            else:
                # Try AI's management path via ActionModel repeatedly
                model = ActionModel(game, p)
                # Keep invoking "RAISE_CASH" if offered, otherwise break
                legal = model.legal_actions()
                if any(a.kind=="RAISE_CASH" for a in legal):
                    model.apply([a for a in legal if a.kind=="RAISE_CASH"][0])
                    changed = True; continue
                # If still short, bankrupt
                game.declare_bankruptcy(p, cred); game.clear_debt()
                changed = True; continue

        # Purchase / Build: let the AI choose using MCTS action model
        for flag, k in [(getattr(game,"pending_purchase",None), "purchase"),
                        (getattr(game,"pending_build",None), "build"),
                        (getattr(game,"pending_jail_turn",None), "jail")]:
            if flag:
                p = flag.get("player") if isinstance(flag, dict) else None
                if p is None: p = current
                model = ActionModel(game, p)
                # If there are non-NOOPs, let MCTS pick
                legal = model.legal_actions()
                if len(legal) > 1 or (legal and legal[0].kind != "NOOP"):
                    a = mcts_decide(game, p, iterations=600)
                    model.apply(a)
                    changed = True; break
        # Bankrupt notice
        if getattr(game, "pending_bankrupt_notice", None):
            game.pending_bankrupt_notice = None
            changed = True
    return

def play_one_game(seed, mode="selfplay"):
    random.seed(seed)
    if mode == "selfplay":
        names = ["AI 1","AI 2","AI 3","AI 4"]
        bots  = {n: MCTSMonopolyBot("AI") for n in names}
    else:
        names = ["AI 1","BuyAll","Cautious","Greedy"]
        bots  = {"AI 1": MCTSMonopolyBot("AI")}
    game = Game(player_names=names)
    # Rotate starting seat to reduce bias
    rot = seed % len(game.players)
    game.players = game.players[rot:] + game.players[:rot]
    for i,p in enumerate(game.players): p.color = [(0,0,255),(0,255,0),(255,0,0),(0,255,255)][i]

    turns = 0
    MAX_TURNS = 300

    while not game.game_over and turns < MAX_TURNS and len(game.players) > 1:
        cur = game.players[game.current_player_index % len(game.players)]
        resolve_all_modals(game, cur)

        # If the current player is in jail and has a pending jail-turn choice, resolve via AI model
        if getattr(game,"pending_jail_turn",None):
            resolve_all_modals(game, cur)

        # Decide to act/roll using the same action model (NOOP => roll)
        model = ActionModel(game, cur)
        legal = model.legal_actions()
        if len(legal) > 1 or (legal and legal[0].kind != "NOOP"):
            a = mcts_decide(game, cur, iterations=600)
            model.apply(a)
            resolve_all_modals(game, cur)
            continue

        # Roll phase (mirrors your Game/Dice/Player logic)
        s,is_double = game.dice.roll()
        cur.move(s, game.board)
        resolve_all_modals(game, cur)

        if cur.in_jail:
            # Just went/remaining in jail — advance turn
            game.current_player_index = (game.current_player_index + 1) % len(game.players)
            turns += 1
            continue

        if is_double:
            cur.doubles_rolled_consecutive += 1
            if cur.doubles_rolled_consecutive >= 3:
                game.pending_jail = {"player": cur}
                resolve_all_modals(game, cur)
                cur.doubles_rolled_consecutive = 0
                game.current_player_index = (game.current_player_index + 1) % len(game.players)
            # else: extra turn (don’t advance index)
        else:
            cur.doubles_rolled_consecutive = 0
            game.current_player_index = (game.current_player_index + 1) % len(game.players)

        # Winner check (some flows do this internally; be explicit)
        if len(game.players) == 1:
            game.game_over = True
            game.winner = game.players[0]
        turns += 1

    # Decide winner on turn cap by net worth
    if not game.game_over:
        def net_worth(p):
            cash = p.money
            prop_val = 0
            for sp in p.properties_owned:
                cost = getattr(sp, "cost", 0) or 0
                if getattr(sp,"type","")=="Railroad": prop_val += cost * 1.05
                elif getattr(sp,"type","")=="Utility": prop_val += cost * 0.35
                else: prop_val += cost
            return cash + prop_val
        winner = max(game.players, key=net_worth)
        game.winner = winner
        game.game_over = True

    # Collect summary
    winner_name = game.winner.name if game.winner else "None"
    return {
        "seed": seed,
        "mode": mode,
        "turns": turns,
        "winner": winner_name,
        "seat": [p.name for p in game.players].index(winner_name) if winner_name in [p.name for p in game.players] else -1,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--mode", choices=["selfplay","vs_proxies"], default="selfplay")
    ap.add_argument("--out", default=f"results_{int(time.time())}.csv")
    args = ap.parse_args()

    rows = []
    for i in range(args.games):
        rows.append(play_one_game(seed=i, mode=args.mode))

    # Write CSV
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["seed","mode","turns","winner","seat"])
        w.writeheader()
        w.writerows(rows)

    # Quick console summary
    winners = Counter(r["winner"] for r in rows)
    total = len(rows)
    print(f"\n=== Summary ({args.mode}, n={total}) ===")
    for k,v in sorted(winners.items()):
        print(f"{k:10s} : {v:5d}  ({v/total:.1%})")
    avg_turns = sum(r["turns"] for r in rows)/total
    print(f"Avg turns: {avg_turns:.1f}")

if __name__ == "__main__":
    main()
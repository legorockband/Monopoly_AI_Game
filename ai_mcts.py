"""
MCTS-based AI for the provided Monopoly codebase.

Plugs into the existing pending_* decision points exposed by Game/Board.
Focuses on core optimal strategies:
- Prioritize Orange/Red/Light Blue
- Build up to 3 houses before hotels
- Prefer railroads over utilities
- Jail strategy: get out early game; linger mid/late
- Aggressive house building when cash buffer allows

Usage (integration notes at bottom of file).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import random

# --- Lightweight feature extraction & heuristics ----------------------------

# Color weights approximate ROI/landing frequency (relative biases)
COLOR_WEIGHTS = {
    (255, 165, 0): 1.32,  # Orange
    (255, 0, 0): 1.22,    # Red
    (173, 216, 230): 1.18,# Light Blue
    (255, 255, 0): 1.00,  # Yellow
    (0, 255, 0): 0.95,    # Green
    (255, 0, 255): 0.90,  # Pink
    (150, 75, 0): 0.85,   # Brown
    (0, 0, 139): 0.75,    # Dark Blue (swingy, expensive)
    "RAIL": 1.15,
    "UTIL": 0.25,
}

# Rent escalation emphasis for houses up to 3
HOUSE_STEP_WEIGHT = [0.0, 1.0, 1.8, 2.6, 1.0, 0.5]  # [base,1,2,3,4,hotel]

# Safety cash buffer (prefer to keep at least this much liquid)
MIN_CASH_BUFFER = 150

try:
    from ai_manage import decide_and_apply_management
except ImportError:
    decide_and_apply_management = None

# --- Action representation --------------------------------------------------
@dataclass(frozen=True)
class Action:
    kind: str
    data: Tuple[Any, ...] = field(default_factory=tuple)

    def __repr__(self) -> str:
        if not self.data:
            return self.kind
        return f"{self.kind}{self.data!r}"


# --- Game adapter: read-only view of what matters to the AI -----------------
@dataclass
class Snapshot:
    """A minimal snapshot the AI can score without deep-copying the whole engine.
    We keep it cheap: values are derived live from the Game object each time.
    """
    game: Any
    me: Any

    def net_worth(self) -> int:
        cash = self.me.money
        prop_val = 0
        house_val = 0
        for sp in self.me.properties_owned:
            cost = getattr(sp, "cost", 0) or 0
            if getattr(sp, "type", "") == "Railroad":
                prop_val += cost * COLOR_WEIGHTS["RAIL"]
            elif getattr(sp, "type", "") == "Utility":
                prop_val += cost * COLOR_WEIGHTS["UTIL"]
            else:
                w = COLOR_WEIGHTS.get(getattr(sp, "color_group", None), 0.8)
                prop_val += cost * w
                # building value (not perfect but guides toward 3 houses)
                if getattr(sp, "has_hotel", False):
                    house_val += sp.house_cost * 4 * HOUSE_STEP_WEIGHT[5]
                else:
                    n = getattr(sp, "num_houses", 0)
                    for i in range(1, n + 1):
                        house_val += sp.house_cost * HOUSE_STEP_WEIGHT[i]
        # Slight bonus for monopolies
        mono_bonus = 0
        for sp in self.game.board.spaces:
            if getattr(sp, "type", "") == "Property" and getattr(sp, "owner", None) is self.me:
                mates = [q for q in self.game.board.spaces
                         if getattr(q, "type", "") == "Property" and getattr(q, "color_group", None) == sp.color_group]
                if all(getattr(q, "owner", None) is self.me for q in mates):
                    mono_bonus += 100  # small shaping reward per set
        return int(cash + prop_val + house_val + mono_bonus)


# --- MCTS core --------------------------------------------------------------
@dataclass
class Node:
    state: Snapshot
    parent: Optional['Node']
    action_from_parent: Optional[Action]
    untried_actions: List[Action]
    children: List['Node'] = field(default_factory=list)
    visits: int = 0
    total_value: float = 0.0

    def uct_select_child(self, c: float = 1.35) -> "Node":
        best, best_score = None, -1e9
        for ch in self.children:
            if ch.visits == 0:
                score = float("inf")
            else:
                exploit = ch.total_value / ch.visits
                explore = c * math.sqrt(math.log(self.visits + 1) / ch.visits)
                score = exploit + explore
            if score > best_score:
                best, best_score = ch, score
        return best

    def add_child(self, action: Action, state: Snapshot, actions: List[Action]) -> "Node":
        child = Node(state=state, parent=self, action_from_parent=action, untried_actions=actions)
        self.children.append(child)
        self.untried_actions.remove(action)
        return child

    def update(self, value: float) -> None:
        self.visits += 1
        self.total_value += value


# --- Action generators tied to the real Game APIs --------------------------
class ActionModel:
    def __init__(self, game: Any, me: Any):
        self.game = game
        self.me = me

    # Generate legal actions constrained to current pending modal/state
    def legal_actions(self) -> List[Action]:
        g = self.game
        me = self.me
        acts: List[Action] = []

        # Debt handling
        if g.pending_debt and g.pending_debt.get("player") is me:
            amt = g.pending_debt["amount"]
            if me.money >= amt:
                acts.append(Action("PAY_DEBT"))
            acts.append(Action("RAISE_CASH"))
            acts.append(Action("BANKRUPT"))
            return acts

        # Jail-turn option modal
        if g.pending_jail_turn and g.pending_jail_turn.get("player") is me:
            props = [s for s in g.board.spaces if getattr(s, "type", "") == "Property"]
            total_props = len(props) or 1
            owned_props = sum(1 for s in props if getattr(s, "owner", None) is not None)
            owned_ratio = owned_props / total_props
            EARLY = owned_ratio < 0.50
            forced_third = (me.jail_turns >= 2)

            acts: List[Action] = []
            if EARLY:
                if me.get_out_of_jail_free_cards > 0:
                    acts.append(Action("JAIL_USE_GOJF"))
                if me.money >= 50:
                    acts.append(Action("JAIL_PAY"))
                acts.append(Action("JAIL_ROLL"))
            else:
                if not forced_third:
                    acts.append(Action("JAIL_ROLL"))
                if me.get_out_of_jail_free_cards > 0:
                    acts.append(Action("JAIL_USE_GOJF"))
                if me.money >= 50:
                    acts.append(Action("JAIL_PAY"))
                if not acts:
                    acts.append(Action("JAIL_ROLL"))
            return acts

        # Immediate send-to-jail notice (ack only)
        if g.pending_jail and g.pending_jail.get("player") is me:
            acts.append(Action("ACK_GO_TO_JAIL"))
            return acts

        # Purchase decision
        if g.pending_purchase and g.pending_purchase.get("player") is me:
            prop = g.pending_purchase["property"]
            affordable = g.pending_purchase.get("affordable", True)
            if affordable:
                acts.append(Action("BUY", (prop,)))
            acts.append(Action("SKIP_PURCHASE", (prop,)))
            return acts

        # Rent & Tax
        if g.pending_rent and g.pending_rent.get("player") is me:
            acts.append(Action("PAY_RENT"))
            return acts
        if g.pending_tax and g.pending_tax.get("player") is me:
            acts.append(Action("PAY_TAX"))
            return acts

        # Build/manage popup (opened when landing on own property or from Manage UI)
        if g.pending_build and g.pending_build.get("player") is me:
            info = g.pending_build
            if info.get("can_house"):
                acts.append(Action("BUILD_HOUSE", (info["property"],)))
            if info.get("can_hotel"):
                acts.append(Action("BUILD_HOTEL", (info["property"],)))
            if info.get("can_sell_house"):
                acts.append(Action("SELL_HOUSE", (info["property"],)))
            if info.get("can_sell_hotel"):
                acts.append(Action("SELL_HOTEL", (info["property"],)))
            if info.get("can_mortgage"):
                acts.append(Action("MORTGAGE", (info["property"],)))
            if info.get("can_unmortgage"):
                acts.append(Action("UNMORTGAGE", (info["property"],)))
            acts.append(Action("SKIP_BUILD"))
            return acts

        # If none of the above, default to NOOP (driver will decide to roll/end)
        acts.append(Action("NOOP"))
        return acts

    # Apply an action to the real Game (one step); return a new Snapshot
    def apply(self, a: Action) -> Snapshot:
        g = self.game
        me = self.me
        kind = a.kind

        if kind == "PAY_DEBT":
            info = g.pending_debt
            if info and info.get("player") is me and me.money >= info["amount"]:
                amt = info["amount"]; cred = info.get("creditor")
                me.pay_money(amt)
                if cred: cred.collect_money(amt)
                g.clear_debt()
            return Snapshot(g, me)

        if kind == "RAISE_CASH":
            # Determine how much we need
            need = 0
            if g.pending_debt and g.pending_debt.get("player") is me:
                need = max(0, g.pending_debt["amount"] - me.money)

            # 1) Mortgage in strict order: Utilities → Railroads → Unimproved Properties
            from ai_manage import AIMonopolyPropertyManager
            from game import Property, Railroad, Utility
            mgr = AIMonopolyPropertyManager()
            while me.money < g.pending_debt["amount"]:
                mort_candidates = mgr._non_core_mortgage_candidates(g, me)
                if not mort_candidates:
                    break
                _, sp = mort_candidates[0]   # pick the first priority candidate
                if isinstance(sp, Property):
                    ok, _ = sp.can_mortgage(me, g.board)
                    if ok: sp.mortgage(me)
                elif isinstance(sp, (Railroad, Utility)):
                    ok, _ = sp.can_mortgage(me)
                    if ok: sp.mortgage(me)

                if me.money >= g.pending_debt["amount"]:
                    break

            # 2) As a last resort, sell houses/hotels to raise cash
            if me.money < g.pending_debt["amount"]:
                for sp in me.properties_owned:
                    if hasattr(sp, "can_sell_house") and sp.can_sell_house(me, g.board)[0]:
                        sp.sell_house(me)
                    elif hasattr(sp, "can_sell_hotel") and sp.can_sell_hotel(me, g.board)[0]:
                        sp.sell_hotel(me)
                    if me.money >= g.pending_debt["amount"]:
                        break

            return Snapshot(g, me)

        if kind == "BANKRUPT":
            info = g.pending_debt
            if info and info.get("player") is me:
                g.declare_bankruptcy(me, info.get("creditor"))
                g.clear_debt()
            return Snapshot(g, me)

        if kind == "JAIL_USE_GOJF":
            g.use_gojf_and_exit(me); return Snapshot(g, me)
        
        if kind == "JAIL_PAY":
            g.pay_fine_and_exit(me); return Snapshot(g, me)
        
        if kind == "JAIL_ROLL":
            g.roll_for_doubles_from_jail(me); return Snapshot(g, me)
        
        if kind == "ACK_GO_TO_JAIL":
            g.pending_jail = None
            me.in_jail = True
            me.position = g.board.jail_space_index
            me.jail_turns = 0
            return Snapshot(g, me)

        if kind == "BUY":
            g.confirm_purchase(True); return Snapshot(g, me)
       
        if kind == "SKIP_PURCHASE":
            g.confirm_purchase(False); return Snapshot(g, me)

        if kind == "PAY_RENT":
            g.settle_rent(); return Snapshot(g, me)
        
        if kind == "PAY_TAX":
            g.confirm_tax(); return Snapshot(g, me)

        if kind == "BUILD_HOUSE":
            g.confirm_build("house"); return Snapshot(g, me)
        
        if kind == "BUILD_HOTEL":
            g.confirm_build("hotel"); return Snapshot(g, me)
        
        if kind == "SELL_HOUSE":
            g.confirm_build("sell_house"); return Snapshot(g, me)
        
        if kind == "SELL_HOTEL":
            g.confirm_build("sell_hotel"); return Snapshot(g, me)
        
        if kind == "MORTGAGE":
            g.confirm_build("mortgage"); return Snapshot(g, me)
        
        if kind == "UNMORTGAGE":
            g.confirm_build("unmortgage"); return Snapshot(g, me)

        return Snapshot(g, me)


# --- Rollout policy ---------------------------------------------------------
def rollout_value(s: Snapshot) -> float:
    """Stochastic rollout: we don’t simulate future dice; instead, evaluate
    with a shaped heuristic and a small random jitter to break ties.
    """
    base = s.net_worth()
    # Encourage house count reaching 3 across strong colors
    three_house_push = 0
    for sp in s.me.properties_owned:
        if getattr(sp, "type", "") == "Property":
            n = getattr(sp, "num_houses", 0)
            if n == 3:
                w = COLOR_WEIGHTS.get(getattr(sp, "color_group", None), 1.0)
                three_house_push += 50 * w
    # Slight penalty for low cash (danger of rent)
    cash_pen = 0
    if s.me.money < MIN_CASH_BUFFER:
        cash_pen = (MIN_CASH_BUFFER - s.me.money) * 0.20
    return base + three_house_push - cash_pen + random.uniform(-5, 5)


# --- Search driver ----------------------------------------------------------
def mcts_decide(game: Any, me: Any, iterations: int = 400) -> Action:
    def _shadow_apply(model: ActionModel, action: Action) -> Snapshot:
        # Return a Snapshot without mutating the real game. A proper clone-based
        # simulator would go here; for safety we just no-op during search.
        return Snapshot(model.game, model.me)

    model = ActionModel(game, me)
    root_state = Snapshot(game, me)
    root = Node(state=root_state, parent=None, action_from_parent=None, untried_actions=model.legal_actions())

    if not root.untried_actions:
        return Action("NOOP")

    for _ in range(iterations):
        node = root
        state = Snapshot(game, me)
        local_model = ActionModel(game, me)

        # Selection
        while not node.untried_actions and node.children:
            node = node.uct_select_child()
            state = _shadow_apply(local_model, node.action_from_parent)
            local_model = ActionModel(game, me)

        # Expansion
        if node.untried_actions:
            a = random.choice(node.untried_actions)
            state = _shadow_apply(local_model, a)
            local_model = ActionModel(game, me)
            node = node.add_child(a, state, local_model.legal_actions())

        # Rollout (heuristic evaluation)
        value = rollout_value(state)

        # Backprop
        while node is not None:
            node.update(value)
            node = node.parent

    # Pick the most-visited child
    if not root.children:
        return random.choice(root.untried_actions)
    best = max(root.children, key=lambda c: c.visits)
    return best.action_from_parent or Action("NOOP")


# --- High-level bot ---------------------------------------------------------
class MCTSMonopolyBot:
    """A simple orchestration wrapper. Call step() repeatedly from the UI loop
    whenever it’s this player’s turn. The bot will:
      - auto-handle modals (rent/tax/purchase/build/jail/debt)
      - request rolls by returning the flag `want_roll`
      - request end-of-turn by returning `want_end`
    """
    def __init__(self, name_prefix: str = "AI"):
        self.name_prefix = name_prefix

    def is_ai(self, player: Any) -> bool:
        return isinstance(player.name, str) and player.name.strip().upper().startswith(self.name_prefix.upper())

    def step(self, game: Any, player: Any, iterations: int = 400) -> Dict[str, bool]:
        if not self.is_ai(player):
            return {"want_roll": False, "want_end": False}

        if getattr(game, "pending_jail", None) or getattr(game, "pending_jail_turn", None):
            return {"want_roll": False, "want_end": False}

        # If ANY modal is up, do nothing. Let the UI show it + handle timed auto-actions.
        if (getattr(game, "pending_purchase", None) and game.pending_purchase.get("player") is player) \
           or (getattr(game, "pending_rent", None) and game.pending_rent.get("player") is player) \
           or (getattr(game, "pending_tax", None) and game.pending_tax.get("player") is player) \
           or getattr(game, "pending_build", None) or getattr(game, "pending_debt", None) \
           or getattr(game, "pending_trade", None):
            return {"want_roll": False, "want_end": False}

        # Give AI a chance to manage (build/mortgage/unmortgage) when no modal is up
        if decide_and_apply_management:
            decide_and_apply_management(game, player)
            # If management opened a modal (e.g., build/debt), let UI handle it this frame
            if getattr(game, "pending_build", None) or getattr(game, "pending_debt", None):
                return {"want_roll": False, "want_end": False}

        # Try a smart trade first.
        if self._try_trade(game, player):
            return {"want_roll": False, "want_end": False}

        model = ActionModel(game, player)
        actions = model.legal_actions()
        if actions and (len(actions) > 1 or actions[0].kind != "NOOP"):
            a = mcts_decide(game, player, iterations=iterations)
            model.apply(a)

            # After an auto-action resolves, try one more management sweep
            if decide_and_apply_management:
                decide_and_apply_management(game, player)
                if getattr(game, "pending_build", None) or getattr(game, "pending_debt", None):
                    return {"want_roll": False, "want_end": False}

            return {"want_roll": False, "want_end": False}

        return {"want_roll": True, "want_end": False}

    # --- Trading heuristics ---
    def _priority_colors(self):
        # Orange first; then strong middle (pink/red/yellow), then light blue
        return [
            (255, 165, 0),   # Orange
            (173, 216, 230), # Light Blue
            (255, 0, 0),     # Red
            (255, 255, 0),   # Yellow
            (255, 0, 255),   # Pink
        ]

    @staticmethod
    def _weighted_title_value(sp) -> float:
        t = getattr(sp, "type", "")
        if t == "Railroad":
            return getattr(sp, "cost", 0) * COLOR_WEIGHTS["RAIL"]
        if t == "Utility":
            return getattr(sp, "cost", 0) * COLOR_WEIGHTS["UTIL"]
        if t == "Property":
            w = COLOR_WEIGHTS.get(getattr(sp, "color_group", None), 0.8)
            return getattr(sp, "cost", 0) * w
        return getattr(sp, "cost", 0) or 0

    @staticmethod
    def _ev_offer_value(offer: dict) -> float:
        v = float(int(offer.get("cash", 0))) + 100.0 * int(offer.get("gojf", 0))
        for sp in offer.get("props", []):
            v += MCTSMonopolyBot._weighted_title_value(sp)
        return v

    def _owns_any_in_band(self, game, me):
        # High-value band: indices 11..29 inclusive, exclude utilities
        for sp in game.board.spaces[11:30]:
            if getattr(sp, "type", "") == "Property" and getattr(sp, "owner", None) is me:
                return True
        # also count any Orange anywhere
        for sp in me.properties_owned:
            if getattr(sp, "type", "") == "Property" and getattr(sp, "color_group", None) == (255, 165, 0):
                return True
        return False

    def _missing_set_props(self, game, me, color):
        mine = [sp for sp in me.properties_owned
                if getattr(sp, "type","")=="Property" and getattr(sp, "color_group", None)==color]
        group = [sp for sp in game.board.spaces
                 if getattr(sp, "type","")=="Property" and getattr(sp, "color_group", None)==color]
        missing = [sp for sp in group if getattr(sp, "owner", None) is not me]
        return mine, group, missing

    def _find_owner(self, sp, players):
        for p in players:
            if getattr(sp, "owner", None) is p:
                return p
        return None

    def _cash_after(self, me, cash_offer):
        return getattr(me,"money",0) - int(cash_offer)

    def _try_trade(self, game, me):
        tried = getattr(game, "_trade_attempted_this_turn", None)
        if isinstance(tried, set) and (me in tried):
            return False
        
        # Only consider if no proposal pending and we have some cash buffer
        if getattr(game, "pending_trade", None):
            return False
        if not self._owns_any_in_band(game, me):
            return False

        budget = max(0, getattr(me, "money", 0) - MIN_CASH_BUFFER)
        if budget < 60:  # nothing meaningful to offer
            return False

        # Walk priority colors; try to buy a single missing title from its owner
        for color in self._priority_colors():
            mine, group, missing = self._missing_set_props(game, me, color)
            if not mine or not missing:
                continue

            # Try the cheapest missing first
            missing_sorted = sorted(missing, key=lambda s: getattr(s, "cost", 0))

            for target in missing_sorted:
                owner = self._find_owner(target, game.players)
                if owner is None or owner is me:
                    continue

                base = int(getattr(target, "cost", 0) or 0)
                completes = (len(mine) + 1 == len(group))
                premium = int(round(base * (0.40 if completes else 0.10)))  # +30% if completing, else +10%
                offer_cash = min(budget, base + premium)

                if self._cash_after(me, offer_cash) < MIN_CASH_BUFFER:
                    continue

                offer_left  = {"cash": offer_cash, "gojf": 0, "props": []}   # what I (me) give
                offer_right = {"cash": 0,        "gojf": 0, "props": [target]}  # what I get

                # --- Balance with cash so it’s fair but slightly in our favor (asks for money if we give more)
                me_get  = {"cash": 0, "gojf": 0, "props": offer_right.get("props", [])}  # what I receive in titles
                me_give = {"cash": 0, "gojf": 0, "props": offer_left.get("props", [])}   # what I give in titles

                v_get_titles  = MCTSMonopolyBot._ev_offer_value(me_get)
                v_give_titles = MCTSMonopolyBot._ev_offer_value(me_give)

                # Target a small edge for me (e.g., +8% when it completes a set, +3% otherwise)
                edge = 0.08 if completes else 0.03
                fair_cash_delta = (v_give_titles - v_get_titles) * (1 + edge)

                if fair_cash_delta > 0:
                    # I'm giving more value → ask THEM for money
                    ask = int(round(fair_cash_delta))
                    owner_cash = getattr(owner, "money", 0)
                    ask = max(0, min(ask, max(0, owner_cash - MIN_CASH_BUFFER)))
                    if ask > 0:
                        offer_right["cash"] = ask
                else:
                    # I’m getting more value → optionally sweeten with a small cash bump on my side
                    give = int(round(-fair_cash_delta * 0.5))  # split the surplus
                    give = min(give, budget)
                    if give > 0 and self._cash_after(me, offer_cash + give) >= MIN_CASH_BUFFER:
                        offer_left["cash"] = offer_cash + give

                # Rough fairness check using the engine's heuristic
                delta_ok = True
                try:
                    prev = getattr(game, "pending_trade", None)
                    game.start_trade_proposal(me, owner, offer_left, offer_right)
                    dl_me  = game.rough_trade_delta_for(me)
                    dl_own = game.rough_trade_delta_for(owner)
                    fair = abs(dl_me) <= base * 0.20 and abs(dl_own) <= base * 0.20
                    if completes:
                        fair = dl_own >= 0  # ensure the other side isn't losing value
                    delta_ok = fair
                finally:
                    game.pending_trade = prev  # restore

                if not delta_ok:
                    continue

                # --- Additional sanity checks using game heuristics ---
                me_get  = {"cash": offer_right["cash"], "gojf": offer_right["gojf"], "props": offer_right.get("props", [])}
                me_give = {"cash": offer_left["cash"], "gojf": offer_left["gojf"], "props": offer_left.get("props", [])}

                # 1. Don’t break pairs unless I gain a monopoly
                if game.would_break_pair_without_monopoly(me, me_get, me_give):
                    continue  # skip this trade entirely

                # 2. If the opponent would get a monopoly and I don’t, demand a premium
                if game.would_grant_monopoly(owner, me_give, me_get) and not game.would_grant_monopoly(me, me_get, me_give):
                    # increase required edge or just skip
                    continue

                # 3. Mortgaged properties should be worth less
                for sp in me_get["props"]:
                    if getattr(sp, "is_mortgaged", False):
                        # apply a discount to effective value
                        offer_right["cash"] = max(0, offer_right["cash"] - int(sp.mortgage_value * 0.5))

                # 4. Cancel if the fairness check shows the other side loses too much
                dl_me  = game.rough_trade_delta_for(me)
                dl_own = game.rough_trade_delta_for(owner)
                if dl_own < -base * 0.15:  # owner would lose more than ~15% of value
                    continue

                # Propose it!
                game.start_trade_proposal(me, owner, offer_left, offer_right)
                tried = getattr(game, "_trade_attempted_this_turn", None)
                if isinstance(tried, set):
                    tried.update({me, owner})

                return True

        return False


# --- Integration instructions ----------------------------------------------
INTEGRATION = r"""
1) Save this file as ai_mcts.py alongside your existing modules.

2) In main_display.py, import and instantiate once:
       from ai_mcts import MCTSMonopolyBot
       bot = MCTSMonopolyBot(name_prefix="AI")

3) Any player whose name starts with "AI" will be controlled by the bot.
"""

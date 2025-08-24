# ai_manage.py
from __future__ import annotations
from typing import List, Optional
from game import Property, Railroad, Utility, Player, Game

class AIMonopolyPropertyManager:
    MAX_DICE_SUM = 12
    EARLY_GAME_MIN_BUFFER = 200
    LATE_GAME_MIN_BUFFER  = 400

    def __init__(self):
        # Queue of (action, property)
        # action is one of: "house"
        self._build_queue: list[Property] = []

    def next_build_request(self, game: Game, me: Player) -> Optional[Property]:
        """
        Pop the next property we want to build *via the UI modal*.
        Validate it's still legal and preserves buffer.
        """
        while self._build_queue:
            prop = self._build_queue.pop(0)
            # Re-check legality/cash because state may have changed
            if not isinstance(prop, Property) or prop.owner is not me:
                continue
            can_house, _ = prop.can_build_house(me, game.board)
            if not can_house:
                continue
            buffer_needed = self._cash_buffer_needed(game, me)
            if me.money - prop.house_cost < buffer_needed:
                continue
            return prop
        return None

    def consider_management(self, game: Game, player: Player) -> None:
        if not player or player not in game.players:
            return
        if (game.pending_debt or game.pending_rent or game.pending_purchase or
            game.pending_tax or game.pending_build or game.pending_jail or
            game.pending_jail_turn or game.pending_bankrupt_notice or
            game.last_drawn_card or game.pending_trade):
            return

        buffer_needed = self._cash_buffer_needed(game, player)

        if player.money < buffer_needed:
            self._raise_cash_to_buffer(game, player, buffer_needed)

        if player.money < buffer_needed:
            return

        # Enqueue at most ONE build per call; UI will execute it via modal.
        self._enqueue_one_build_toward_three(game, player, buffer_needed)

    # ---------- internals ----------

    def _enqueue_one_build_toward_three(self, game: Game, me: Player, buffer_needed: int) -> None:
        monopolies = self._owned_monopolies(game, me)
        for group in monopolies:
            # skip sets already at 3 on all or with hotels
            if all((p.has_hotel or p.num_houses >= 3) for p in group):
                continue
            # even-build: pick the least-developed first, but cap at 3
            candidates = [p for p in group if not p.has_hotel and p.num_houses < 3]
            if not candidates:
                continue
            candidates.sort(key=lambda p: (p.num_houses, p.index))
            for prop in candidates:
                can_house, _ = prop.can_build_house(me, game.board)
                if not can_house:
                    continue
                if me.money - prop.house_cost < buffer_needed:
                    continue
                # enqueue and return (only one per consider_management call)
                self._build_queue.append(prop)
                return

    # (keep your existing _cash_buffer_needed, _owned_monopolies, _non_core_mortgage_candidates,
    #  and _raise_cash_to_buffer exactly as you have them)


    # -------------------- Policy helpers --------------------

    def _cash_buffer_needed(self, game: Game, me: Player) -> int:
        """
        Estimate the single worst rent I could be forced to pay right now,
        then choose a buffer = max(threat, floor_min) where floor depends on game saturation.
        """
        threat = 0
        board = game.board

        for sp in board.spaces:
            # Owned by someone else?
            owner = getattr(sp, "owner", None)
            if owner is None or owner is me:
                continue

            if isinstance(sp, Property):
                # Monopoly doubles base rent when unimproved
                owner_has_monopoly = owner.has_monopoly(sp.color_group, board)
                rent = sp.calculate_rent(owner_has_monopoly)
                threat = max(threat, rent)

            elif isinstance(sp, Railroad):
                count = owner.count_railroads()
                rent = sp.calculate_rent(count)
                threat = max(threat, rent)

            elif isinstance(sp, Utility):
                # Worst-case utility: dice 12 * 10 if owner has 2 utilities
                num_utils = owner.count_utilities()
                if num_utils == 2:
                    rent = self.MAX_DICE_SUM * 10
                elif num_utils == 1:
                    rent = self.MAX_DICE_SUM * 4
                else:
                    rent = 0
                threat = max(threat, rent)

        # Rough saturation → raise the floor late game
        props = [s for s in board.spaces if isinstance(s, Property)]
        owned = sum(1 for s in props if getattr(s, "owner", None) is not None)
        ratio = owned / (len(props) or 1)

        floor = self.EARLY_GAME_MIN_BUFFER if ratio < 0.6 else self.LATE_GAME_MIN_BUFFER
        return max(threat, floor)

    def _owned_monopolies(self, game: Game, me: Player):
        """Return list of lists: each is the properties in a monopoly set that 'me' owns."""
        monopolies = []
        seen_colors = set()
        for sp in game.board.spaces:
            if isinstance(sp, Property) and sp.owner is me:
                cg = sp.color_group
                if cg in seen_colors:
                    continue
                seen_colors.add(cg)
                group = [p for p in game.board.spaces
                         if isinstance(p, Property) and p.color_group == cg]
                # Own them all?
                if all(p.owner is me for p in group):
                    monopolies.append(sorted(group, key=lambda p: p.index))
        return monopolies

    def _non_core_mortgage_candidates(self, game: Game, me: Player):
        """
        Titles we prefer to mortgage first:
        1) Any unmortgaged Railroad/Utility (simple cash that doesn't block set building)
        2) Properties NOT in any monopoly
        3) Properties in a monopoly BUT (a) no houses/hotel and (b) not needed immediately
        (Mortgage checks enforce "no building on the set" rule anyway.)
        """
        board = game.board
        # Collect sets we fully own
        monopoly_sets = set(tuple(id(p) for p in s) for s in self._owned_monopolies(game, me))
        in_monopoly = set()
        for s in monopoly_sets:
            in_monopoly.update(s)

        rr_utils, loose_props, mono_props = [], [], []
        for sp in me.properties_owned:
            if isinstance(sp, Railroad) and not sp.is_mortgaged:
                ok, _ = sp.can_mortgage(me)
                if ok: rr_utils.append(("rail_util", sp))
            elif isinstance(sp, Utility) and not sp.is_mortgaged:
                ok, _ = sp.can_mortgage(me)
                if ok: rr_utils.append(("rail_util", sp))
            elif isinstance(sp, Property) and not sp.is_mortgaged:
                # In or out of a monopoly?
                if id(sp) not in in_monopoly:
                    ok, _ = sp.can_mortgage(me, board)
                    if ok: loose_props.append(("loose_prop", sp))
                else:
                    # If it's in a monopoly, mortgage only if *completely unimproved* (rule enforced by can_mortgage)
                    ok, _ = sp.can_mortgage(me, board)
                    if ok and sp.num_houses == 0 and not sp.has_hotel:
                        mono_props.append(("mono_unimproved", sp))

        # Priority order as described
        return rr_utils + loose_props + mono_props

    def _raise_cash_to_buffer(self, game: Game, me: Player, buffer_needed: int) -> None:
        """
        Mortgage assets (never sell houses) until we reach the buffer or run out of options.
        """
        # Keep picking from a prioritized list
        picked_any = True
        while me.money < buffer_needed and picked_any:
            picked_any = False
            for _, sp in self._non_core_mortgage_candidates(game, me):
                if me.money >= buffer_needed:
                    break
                if isinstance(sp, Property):
                    ok, _ = sp.can_mortgage(me, game.board)
                    if ok:
                        sp.mortgage(me)
                        picked_any = True
                elif isinstance(sp, Railroad):
                    ok, _ = sp.can_mortgage(me)
                    if ok:
                        sp.mortgage(me)
                        picked_any = True
                elif isinstance(sp, Utility):
                    ok, _ = sp.can_mortgage(me)
                    if ok:
                        sp.mortgage(me)
                        picked_any = True
            # If we couldn't pick anything new, stop
        # Do NOT sell houses/hotels here, by policy.
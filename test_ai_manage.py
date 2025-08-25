# test_ai_manage.py
from ai_manage import AIMonopolyPropertyManager
from game import Game, Property, Railroad, Utility

def find_props(game, names):
    name_to_space = {s.name: s for s in game.board.spaces}
    return [name_to_space[n] for n in names]

def reset_houses(*props):
    for p in props:
        if isinstance(p, Property):
            p.num_houses = 0
            p.has_hotel = False
            p.is_mortgaged = False

def mark_owner(player, *spaces):
    for s in spaces:
        s.owner = player
        if s not in player.properties_owned:
            player.properties_owned.append(s)

def clear_owners(*players):
    # helper if you rerun in same process
    for pl in players:
        pl.properties_owned.clear()

def test_1_build_even_to_three():
    print("\n=== Test 1: Build evenly to 3 houses (with buffer satisfied) ===")
    game = Game(["AI 1", "HUMAN"])
    ai = game.players[0]
    hu = game.players[1]

    # Give AI the full Light Blue set (Oriental/Vermont/Connecticut)
    orient, vermont, connect = find_props(game, ["Oriental Avenue", "Vermont Avenue", "Connecticut Avenue"])
    reset_houses(orient, vermont, connect)
    clear_owners(ai, hu)
    mark_owner(ai, orient, vermont, connect)

    # Give the human something small so buffer floor dominates
    rr = find_props(game, ["Reading Railroad"])[0]
    rr.is_mortgaged = False
    mark_owner(hu, rr)

    # Cash: enough to buy 9 houses while keeping buffer
    ai.money = 2000

    mgr = AIMonopolyPropertyManager()
    mgr.consider_management(game, ai)

    print(f"Money after building: ${ai.money}")
    for p in [orient, vermont, connect]:
        print(f"{p.name}: houses={p.num_houses}, hotel={p.has_hotel}")
    assert all(p.num_houses == 3 for p in [orient, vermont, connect]), "Should reach 3 houses each"
    assert not any(p.has_hotel for p in [orient, vermont, connect]), "No hotels"
    print("✅ Passed: even build to 3 houses.")

def test_2_respect_buffer_no_build():
    print("\n=== Test 2: Do NOT build if only have buffer ===")
    game = Game(["AI 1", "HUMAN"])
    ai = game.players[0]
    hu = game.players[1]

    # Human owns both utilities to spike worst-case rent to 120 (12 * 10)
    elec, water = find_props(game, ["Electric Company", "Water Works"])
    elec.is_mortgaged = water.is_mortgaged = False
    clear_owners(ai, hu)
    mark_owner(hu, elec, water)

    # AI owns magenta set (no houses yet)
    stc, states, virginia = find_props(game, ["St. Charles Place", "States Avenue", "Virginia Avenue"])
    reset_houses(stc, states, virginia)
    mark_owner(ai, stc, states, virginia)

    # Set AI money to exactly the computed buffer -> should refuse to spend
    mgr = AIMonopolyPropertyManager()
    needed = mgr._cash_buffer_needed(game, ai)
    ai.money = needed

    mgr.consider_management(game, ai)

    print(f"Needed buffer = {needed}, AI money after = {ai.money}")
    print(f"Houses: {[ (p.name, p.num_houses) for p in (stc, states, virginia) ]}")
    assert all(p.num_houses == 0 for p in (stc, states, virginia)), "Should not build when only buffer available"
    print("✅ Passed: respects buffer and does not build.")

def test_3_mortgage_non_core_first():
    print("\n=== Test 3: Mortgage non-core (RR/Utility/loose) first to reach buffer ===")
    game = Game(["AI 1", "HUMAN"])
    ai = game.players[0]
    hu = game.players[1]

    # Human: owns a strong rent (e.g., has 3 houses somewhere). We'll simulate by giving them a monopoly with 3 houses.
    kent, ind, ill = find_props(game, ["Kentucky Avenue", "Indiana Avenue", "Illinois Avenue"])
    reset_houses(kent, ind, ill)
    mark_owner(hu, kent, ind, ill)
    # Pretend human already built 3 houses on each (to increase threat)
    for p in (kent, ind, ill):
        p.num_houses = 3

    # AI: owns a Reading RR and a loose property (not part of monopoly)
    rr = find_props(game, ["Reading Railroad"])[0]
    atl = find_props(game, ["Atlantic Avenue"])[0]  # loose, no set completed
    rr.is_mortgaged = False
    atl.is_mortgaged = False
    reset_houses(atl)
    clear_owners(ai, hu)  # clear and re-mark everything
    mark_owner(hu, kent, ind, ill)
    mark_owner(ai, rr, atl)

    # AI money is low; needs to hit buffer by mortgaging RR before touching houses (policy: never sell houses)
    ai.money = 50

    mgr = AIMonopolyPropertyManager()
    needed = mgr._cash_buffer_needed(game, ai)
    print(f"Estimated buffer needed: {needed}")

    mgr.consider_management(game, ai)

    print(f"Money after management: ${ai.money}")
    print(f"RR mortgaged? {rr.is_mortgaged}, Atlantic mortgaged? {atl.is_mortgaged}")
    # At least one of RR/loose should be mortgaged to move toward buffer
    assert rr.is_mortgaged or atl.is_mortgaged, "Should mortgage a non-core title to raise cash"
    # No selling houses anywhere (we never call sell_* in manager)
    assert all(not getattr(sp, 'has_hotel', False) for sp in ai.properties_owned), "No hotels sold/modified"
    print("✅ Passed: mortgages non-core first; no selling of houses.")

def test_4_avoid_actions_when_modals_open():
    print("\n=== Test 4: No action taken while a modal/pending state is open ===")
    game = Game(["AI 1", "HUMAN"])
    ai = game.players[0]

    # Give AI a monopoly & cash that would normally trigger building
    orient, vermont, connect = find_props(game, ["Oriental Avenue", "Vermont Avenue", "Connecticut Avenue"])
    reset_houses(orient, vermont, connect)
    mark_owner(ai, orient, vermont, connect)
    ai.money = 2000

    # Simulate a pending state (e.g., rent modal)
    game.pending_rent = {"player": ai, "owner": game.players[1], "property": orient, "amount": 10}

    mgr = AIMonopolyPropertyManager()
    mgr.consider_management(game, ai)

    # Should NOT have built due to pending modal
    assert all(p.num_houses == 0 for p in (orient, vermont, connect)), "Should not act while modal is open"
    print("✅ Passed: manager does nothing while modals are open.")

if __name__ == "__main__":
    test_1_build_even_to_three()
    test_2_respect_buffer_no_build()
    test_3_mortgage_non_core_first()
    test_4_avoid_actions_when_modals_open()
    print("\nAll tests ran.\n")

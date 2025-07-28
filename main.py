import dice
import board_test
import game_test


def main():
    # You can now safely call their functions here
    board_test.create_board()  # Draw board (comment this out if not needed every run)

    game = game_test.Game(player_names=["Player 1", "Player 2"])
    game.start_game()

if __name__ == "__main__":
    main()
from random import shuffle
asked_split = False
wins = 0 
losses = 0
draws = 0

num_correct = 0
num_incorrect = 0

def generate_split_dict(rules, k_range=range(2, 12)):
    		return {k: rules(k) for k in k_range}

basic_phrases = {
    "pair_splitting": {
        4: "A pair of 2's splits against dealer 2 through 7, otherwise hit.",
        6: "A pair of 3's splits against dealer 2 through 7, otherwise hit.",
        8: "A pair of 4's splits against dealer 5 and 6, otherwise hit.",
        10: "A pair of 5's doubles against dealer 2 through 9, otherwise hit.",
        12: "A pair of 6's splits against dealer 2 through 6, otherwise hit.",
        14: "A pair of 7’s splits against dealer 2 through 7, otherwise hit.",
        16: "Always split 8’s.",
        18: "A pair of 9’s splits against dealer 2 through 9, except for 7, otherwise stand.",
        20: "Never split tens.",
        22: "Always split aces.",
    },
	
	"soft_totals": {
        13: "Soft 13 (A,2) doubles against dealer 5 through 6, otherwise hit.",
        14: "Soft 14 (A,3) doubles against dealer 5 through 6, otherwise hit.",
        15: "Soft 15 (A,4) doubles against dealer 4 through 6, otherwise hit.",
        16: "Soft 16 (A,5) doubles against dealer 4 through 6, otherwise hit.",
        17: "Soft 17 (A,6) doubles against dealer 3 through 6, otherwise hit.",
        18: "Soft 18 (A,7) doubles against dealer 2 through 6, and hits against 9 through Ace, otherwise stand.",
        19: "Soft 19 (A,8) doubles against dealer 6, otherwise stand.",
        20: "Soft 20 (A,9) always stands.",
    },
	
    "hard_totals": {
		4: "8 or lower always hits.",
        5: "8 or lower always hits.",
        6: "8 or lower always hits.",
        7: "8 or lower always hits.",
        8: "8 or lower always hits.",
        9: "9 doubles against dealer 3 through 6 otherwise hit.",
        10: "10 doubles against dealer 2 through 9 otherwise hit.",
        11: "11 always doubles.",
        12: "12 stands against dealer 4 through 6, otherwise hit.",
        13: "13 stands against dealer 2 through 6, otherwise hit.",
        14: "14 stands against dealer 2 through 6, otherwise hit.",
        15: "15 stands against dealer 2 through 6, otherwise hit.",
        16: "16 stands against dealer 2 through 6, otherwise hit.",
        17: "17 and up always stands.",
        18: "17 and up always stands.",
        19: "17 and up always stands.",
        20: "17 and up always stands.",
        21: "17 and up always stands.",
    },
}

basic_strategy = {
    # Pair Splitting (simplified)
		"pair_splitting": {
		    4: generate_split_dict(lambda k: "Y" if 1 < k < 8 else "N"),
		    6: generate_split_dict(lambda k: "Y" if 1 < k < 8 else "N"),
		    8: generate_split_dict(lambda k: "Y" if k in {5, 6} else "N"),
		    10: "N",
		    12: generate_split_dict(lambda k: "Y" if 1 < k < 7 else "N"),
		    14: generate_split_dict(lambda k: "Y" if 1 < k < 8 else "N"),
		    16: "Y",
		    18: generate_split_dict(lambda k: "N" if k in {7, 10, 11} else "Y"),
		    20: "N",
		    22: "Y",
		},
    # Soft Totals (simplified)
    "soft_totals": {
        13: generate_split_dict(lambda k: "D" if k in {5,6} else "H"),
        14: generate_split_dict(lambda k: "D" if k in {5,6} else "H"),
        15: generate_split_dict(lambda k: "D" if k in {4,5,6} else "H"),
        16: generate_split_dict(lambda k: "D" if k in {4,5,6} else "H"),
        17:generate_split_dict(lambda k: "D" if k in {3,4,5,6} else "H"),
        18:generate_split_dict(lambda k: "S" if k in {7,8} else "H" if k in {9,10,11} else "Ds"),
        19: generate_split_dict(lambda k: "Ds" if k == 6 else "S"),
        20: "S",
        21: "S",
    },

    # Hard Totals (simplified)
    "hard_totals": {
    		5: "H",
    		6: "H",
    		7: "H",
    		8: "H",
    		# Always Hit on hard 8 or less
    		9: generate_split_dict(lambda k: "D" if k in {3,4,5,6} else "H"),
    		10: generate_split_dict(lambda k: "H" if k in {10,11} else "D"),
    		11: "D",
    		12: generate_split_dict(lambda k: "S" if k in {4,5,6} else "H"),
    		13: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
    		14: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
    		15: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
    		16: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
        17: "S",  # Always Stand on hard 17
        18: "S",
        19: "S",
        20: "S",
        21: "S" 
    },
}

def print_blackjack_strategy_table(strategy_dict):
    def extract_upcard_keys(moves):
        """Extract unique dealer upcard values for the table header."""
        upcards = set()
        for strategy in moves.values():
            if isinstance(strategy, dict):
                upcards.update(strategy.keys())
        return sorted(upcards)

    print("Blackjack Strategy Table")
    print("=" * 70)
    
    for category, moves in strategy_dict.items():
        print(f"\nCategory: {category.replace('_', ' ').title()}")
        print("-" * 70)

        # Extract upcard keys for the header
        upcards = extract_upcard_keys(moves)
        print(f"{'Your Hand':<12} | " + " | ".join(f"{up:<3}" for up in upcards))
        print("-" * 70)

        # Print rows for each player's hand
        for hand, strategy in moves.items():
            row = f"{hand:<12} | "
            if isinstance(strategy, dict):
                row += " | ".join(f"{strategy.get(up, '-'):>3}" for up in upcards)
            else:
                row += f"{strategy:>3}"
            print(row)
        print("-" * 70)
        print("KEY: H = hit, S = stand, D = Double if available, else hit, Ds = Double if available, else stand, Y = yes, N = no")


def print_dash(num):
		for i in range(num):
				print('-', end="")
		print()

# Create deck and shuffle
def create_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = {rank: min(10, int(rank)) if rank.isdigit() else 10 for rank in ranks}
    values['Ace'] = 11
    return [{'rank': rank, 'suit': suit, 'value': values[rank]} for rank in ranks for suit in suits]
    
def get_num_aces(hand):
    total = sum(card['value'] for card in hand)
    # Adjust for Aces
    num_aces = sum(1 for card in hand if card['rank'] == 'Ace')
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return num_aces
    	
# Evaluate the player's move
def evaluate_move(player_hand, player_total, dealer_upcard, move):
    # Simplified basic strategy
    global basic_strategy
    global basic_phrases
    global asked_split, num_correct, num_incorrect
    key = (player_total, dealer_upcard)
    if (player_hand[0]['value'] == player_hand[1]['value'] and asked_split):
        #splits
        strategy = basic_strategy.get("pair_splitting", {}).get(player_total, "unknown")
        phrase = basic_phrases.get("pair_splitting", {}).get(player_total, "unknown")
        if len(player_hand) != 2:
            if strategy == 'D':
                strategy = 'H'
        asked_split = False
    elif ((player_hand[0]['value'] == 11 or player_hand[1]['value'] == 11) and get_num_aces(player_hand)==1):
        strategy = basic_strategy.get("soft_totals", {}).get(player_total, "unknown")
        phrase = basic_phrases.get("soft_totals", {}).get(player_total, "unknown")
        if len(player_hand) != 2:
            if strategy == 'D':
                strategy = 'H'
            elif strategy == 'Ds':
                strategy = 'S'
        else:
            if strategy == 'Ds':
                strategy = 'D'
    else:
    	#hard totals
        strategy = basic_strategy.get("hard_totals", {}).get(player_total, "unknown")
        phrase = basic_phrases.get("hard_totals", {}).get(player_total, "unknown")
        if len(player_hand) != 2:
            if strategy == 'D':
                strategy = 'H'
    	
   	# Handle cases where strategy is a dictionary (generated by generate_split_dict)
    if isinstance(strategy, dict):
        correct_move = strategy.get(dealer_upcard, "unknown")
    else:
        correct_move = strategy
        
    if correct_move == "unknown":
        return "No strategy available for this scenario."
    elif move == correct_move:
        num_correct += 1
        return f"Correct! The basic strategy is to {correct_move}."
    else:
        num_incorrect += 1
        return f"Incorrect. The correct move was to {correct_move}.\n{phrase}"

def calculate_total(hand):
    total = sum(card['value'] for card in hand)
    # Adjust for Aces
    num_aces = sum(1 for card in hand if card['rank'] == 'Ace')
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return total

def dealer_turn(deck, dealer_hand):
    while calculate_total(dealer_hand) < 17:  # Dealer hits until total is 17 or higher
        dealer_hand.append(deck.pop())
    return dealer_hand

def play_hand(deck, hand, dealer_upcard_value):
    global num_correct, num_incorrect
    """Plays a single hand for the player."""
    while True:
        player_total = calculate_total(hand)
        if player_total > 21:
            print(f"You busted with a total of {player_total}. Dealer wins!")
            return

        print(f"Your total is {player_total}.")
        print_dash(20)
        move = input("Hit, Stand, or Double? (h,s,d)").strip().upper()

        # Get feedback for move
        feedback = evaluate_move(hand, player_total, dealer_upcard_value, move)
        print(feedback)

        if move == "H":
            hand.append(deck.pop())
            print(f"You drew {hand[-1]['rank']} of {hand[-1]['suit']}.")
        elif move == "S":
            break
        elif move == "D":
            if len(hand) == 2:  # Allow doubling only on first move
                hand.append(deck.pop())
                print(f"You doubled and drew {hand[-1]['rank']} of {hand[-1]['suit']}.")
                break
            else:
                print("You can only double on your first move!")
        else:
            print("Invalid move. Please choose Hit, Stand, or Double.")

def play_blackjack():
    #Globals
    global wins, losses, draws, num_correct, num_incorrect
    # Setup
    deck = create_deck()
    shuffle(deck)

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop()]
    dealer_upcard_value = dealer_hand[0]['value']

    print(f"Your hand:\n    {player_hand[0]['rank']} of {player_hand[0]['suit']}\n    {player_hand[1]['rank']} of {player_hand[1]['suit']}")
    print(f"Dealer's upcard:\n    {dealer_hand[0]['rank']} of {dealer_hand[0]['suit']}")

    # Check for split
    split_hand = None
    global asked_split
    if player_hand[0]['value'] == player_hand[1]['value']:
        split = input("Would you like to split? (y/n) ").strip().upper()
        asked_split = True
        feedback = evaluate_move(player_hand, calculate_total(player_hand), dealer_upcard_value, split)
        print(feedback)
        if split == "Y":
            split_hand = [player_hand.pop()]  # Move second card to split hand
            player_hand.append(deck.pop())  # Add a new card to player_hand
            split_hand.append(deck.pop())  # Add a new card to split_hand
            print(f"Your first hand: {player_hand[0]['rank']} of {player_hand[0]['suit']} and {player_hand[1]['rank']} of {player_hand[1]['suit']}")

    # Play player_hand
    #print("\nPlaying your first hand...")
    play_hand(deck, player_hand, dealer_upcard_value)

    # Play split_hand if it exists
    if split_hand:
        #print("\nPlaying your second hand...")
        print(f"Your second hand: {split_hand[0]['rank']} of {split_hand[0]['suit']} and {split_hand[1]['rank']} of {split_hand[1]['suit']}")
        play_hand(deck, split_hand, dealer_upcard_value)

    # Dealer's turn
    dealer_hand.append(deck.pop())  # Reveal dealer's second card
    if calculate_total(player_hand) < 22:
        dealer_hand = dealer_turn(deck, dealer_hand)
    dealer_total = calculate_total(dealer_hand)

    # Print the dealer's hand
    if len(dealer_hand) == 2:
        print(f"Dealer's hand: {dealer_hand[0]['rank']} of {dealer_hand[0]['suit']} and {dealer_hand[1]['rank']} of {dealer_hand[1]['suit']}")
    else:
        print("Dealer's hand: ", end="")
        for card in dealer_hand:
            print(f"{card['rank']} of {card['suit']}", end=", ")
        print()
    print(f"Dealer's total: {dealer_total}")

    # Determine results for each hand
    for i, hand in enumerate([player_hand, split_hand] if split_hand else [player_hand], start=1):
        if hand:
            player_total = calculate_total(hand)
            print(f"\nResults for hand {i}:")
            if dealer_total > 21 or (player_total > dealer_total and player_total < 22):
                print(f"You win with a total of {player_total}!")
                wins += 1
            elif player_total < dealer_total or player_total > 21:
                print(f"Dealer wins with a total of {dealer_total}.")
                losses += 1
            else:
                print("Push...")
                draws += 1

# Play the game
while(True):
    play_blackjack()
    print()
    str = input('Type \'stop\' to end game.\nType \'chart\' to see book moves.\n Press anything else to continue.')
    if str == 'stop':
        print_dash(25)
        print('Training Session Finished')
        print_dash(25)
        print(f'Wins: {wins}\nLosses: {losses}\nDraws: {draws}\n\nCorrect moves: {num_correct}\nIncorrect moves: {num_incorrect}\n')
        print(f'Your accuracy: {num_correct/(num_correct+num_incorrect)}%')
        print_dash(25)				
        break
    elif str == 'chart':
        print_blackjack_strategy_table(basic_strategy)
    else:
        print("----- New Hand -----")
        print()
input("Press Enter to exit...")
'''
# Example game
deck = create_deck()
shuffle(deck)

player_hand = [deck.pop(), deck.pop()]
dealer_upcard = deck.pop()

player_total = sum(card['value'] for card in player_hand)
print(f"Your hand: {player_hand[0]['rank']} of {player_hand[0]['suit']} and {player_hand[1]['rank']} of {player_hand[1]['suit']}, total: {player_total}")
print(f"Dealer's upcard: {dealer_upcard['rank']}")

# Player makes a move
move = input("Hit, Stand, or Double? ")
feedback = evaluate_move(player_hand, player_total, int(dealer_upcard['value']), move)
print(feedback)'''

import pygame
import sys
import math
from random import shuffle, choices

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
CARD_WIDTH = 90
CARD_HEIGHT = 126
CARD_SPACING = 25
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 55
BUTTON_SPACING = 15
CARD_CORNER_RADIUS = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
DARK_GREEN = (0, 80, 0)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (138, 43, 226)
TEAL = (0, 128, 128)
BACKGROUND = (7, 99, 36)  # Casino green
CARD_BACK = (20, 50, 100)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Game state
asked_split = False
wins = 0
losses = 0
draws = 0
num_correct = 0
num_incorrect = 0

# Training system - tracks performance by hand type
training_stats = {
    "hard_totals": {},  # {hand_value: {"correct": 0, "incorrect": 0}}
    "soft_totals": {},
    "pair_splitting": {},
}

# Game variables
deck = []
player_hand = []
dealer_hand = []
split_hand = None
dealer_upcard_value = 0
game_state = "waiting"
current_hand = "main"
main_hand_done = False
split_hand_done = False
feedback_message = ""
feedback_color = BLACK
can_double = True
can_split = False
training_mode = True  # Enable adaptive training

def generate_split_dict(rules, k_range=range(2, 12)):
    return {k: rules(k) for k in k_range}

basic_phrases = {
    "pair_splitting": {
        4: "A pair of 2's splits against dealer 2 through 7, otherwise hit.",
        6: "A pair of 3's splits against dealer 2 through 7, otherwise hit.",
        8: "A pair of 4's splits against dealer 5 and 6, otherwise hit.",
        10: "A pair of 5's doubles against dealer 2 through 9, otherwise hit.",
        12: "A pair of 6's splits against dealer 2 through 6, otherwise hit.",
        14: "A pair of 7's splits against dealer 2 through 7, otherwise hit.",
        16: "Always split 8's.",
        18: "A pair of 9's splits against dealer 2 through 9, except for 7, otherwise stand.",
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
    "soft_totals": {
        13: generate_split_dict(lambda k: "D" if k in {5,6} else "H"),
        14: generate_split_dict(lambda k: "D" if k in {5,6} else "H"),
        15: generate_split_dict(lambda k: "D" if k in {4,5,6} else "H"),
        16: generate_split_dict(lambda k: "D" if k in {4,5,6} else "H"),
        17: generate_split_dict(lambda k: "D" if k in {3,4,5,6} else "H"),
        18: generate_split_dict(lambda k: "S" if k in {7,8} else "H" if k in {9,10,11} else "Ds"),
        19: generate_split_dict(lambda k: "Ds" if k == 6 else "S"),
        20: "S",
        21: "S",
    },
    "hard_totals": {
        5: "H",
        6: "H",
        7: "H",
        8: "H",
        9: generate_split_dict(lambda k: "D" if k in {3,4,5,6} else "H"),
        10: generate_split_dict(lambda k: "H" if k in {10,11} else "D"),
        11: "D",
        12: generate_split_dict(lambda k: "S" if k in {4,5,6} else "H"),
        13: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
        14: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
        15: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
        16: generate_split_dict(lambda k: "S" if k in {2,3,4,5,6} else "H"),
        17: "S",
        18: "S",
        19: "S",
        20: "S",
        21: "S" 
    },
}

def create_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = {rank: min(10, int(rank)) if rank.isdigit() else 10 for rank in ranks}
    values['Ace'] = 11
    return [{'rank': rank, 'suit': suit, 'value': values[rank]} for rank in ranks for suit in suits]

def get_weak_hands():
    """Identify hands the player struggles with"""
    weak_hands = []
    
    for category, stats in training_stats.items():
        for hand_value, performance in stats.items():
            total = performance.get("correct", 0) + performance.get("incorrect", 0)
            if total >= 3:  # Need at least 3 attempts
                accuracy = performance.get("correct", 0) / total
                if accuracy < 0.7:  # Less than 70% accuracy
                    weak_hands.append((category, hand_value, accuracy))
    
    # Sort by worst performance
    weak_hands.sort(key=lambda x: x[2])
    return weak_hands

def create_weighted_deck():
    """Create a deck that prioritizes weak hands"""
    deck = create_deck()
    
    if not training_mode:
        shuffle(deck)
        return deck
    
    weak_hands = get_weak_hands()
    if not weak_hands:
        shuffle(deck)
        return deck
    
    # Create a weighted deck - prioritize cards that create weak hands
    # This is simplified - in practice, we'd need more sophisticated logic
    # For now, we'll just shuffle normally but track which hands appear
    shuffle(deck)
    return deck

def get_num_aces(hand):
    total = sum(card['value'] for card in hand)
    num_aces = sum(1 for card in hand if card['rank'] == 'Ace')
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return num_aces

def calculate_total(hand):
    total = sum(card['value'] for card in hand)
    num_aces = sum(1 for card in hand if card['rank'] == 'Ace')
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return total

def get_hand_category(player_hand, player_total):
    """Determine the category of hand for training"""
    if len(player_hand) >= 2 and player_hand[0]['value'] == player_hand[1]['value']:
        return "pair_splitting", player_total
    elif len(player_hand) >= 2 and (player_hand[0]['value'] == 11 or player_hand[1]['value'] == 11) and get_num_aces(player_hand) == 1:
        return "soft_totals", player_total
    else:
        return "hard_totals", player_total

def update_training_stats(player_hand, player_total, is_correct):
    """Update training statistics"""
    category, hand_value = get_hand_category(player_hand, player_total)
    
    if category not in training_stats:
        training_stats[category] = {}
    if hand_value not in training_stats[category]:
        training_stats[category][hand_value] = {"correct": 0, "incorrect": 0}
    
    if is_correct:
        training_stats[category][hand_value]["correct"] += 1
    else:
        training_stats[category][hand_value]["incorrect"] += 1

def evaluate_move(player_hand, player_total, dealer_upcard, move):
    global basic_strategy, basic_phrases, asked_split, num_correct, num_incorrect
    
    if (len(player_hand) >= 2 and player_hand[0]['value'] == player_hand[1]['value'] and asked_split):
        strategy = basic_strategy.get("pair_splitting", {}).get(player_total, "unknown")
        phrase = basic_phrases.get("pair_splitting", {}).get(player_total, "unknown")
        if len(player_hand) != 2:
            if strategy == 'D':
                strategy = 'H'
        asked_split = False
    elif (len(player_hand) >= 2 and (player_hand[0]['value'] == 11 or player_hand[1]['value'] == 11) and get_num_aces(player_hand)==1):
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
        strategy = basic_strategy.get("hard_totals", {}).get(player_total, "unknown")
        phrase = basic_phrases.get("hard_totals", {}).get(player_total, "unknown")
        if len(player_hand) != 2:
            if strategy == 'D':
                strategy = 'H'
    
    if isinstance(strategy, dict):
        correct_move = strategy.get(dealer_upcard, "unknown")
    else:
        correct_move = strategy
        
    if correct_move == "unknown":
        return ("No strategy available for this scenario.", GRAY)
    
    is_correct = (move == correct_move)
    update_training_stats(player_hand, player_total, is_correct)
    
    if is_correct:
        num_correct += 1
        return (f"✓ Correct! The basic strategy is to {correct_move}.", GREEN)
    else:
        num_incorrect += 1
        return (f"✗ Incorrect. The correct move was {correct_move}. {phrase}", RED)

def dealer_turn(deck, dealer_hand):
    while calculate_total(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
    return dealer_hand

def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rounded rectangle"""
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
    pygame.draw.rect(surface, BLACK, (x + radius, y, w - 2*radius, h), 2)
    pygame.draw.rect(surface, BLACK, (x, y + radius, w, h - 2*radius), 2)

def draw_card(screen, card, x, y, face_up=True):
    """Draw a card with rounded corners and shadow"""
    # Shadow (simple dark rectangle behind)
    shadow_offset = 3
    shadow_rect = (x + shadow_offset, y + shadow_offset, CARD_WIDTH, CARD_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=CARD_CORNER_RADIUS)
    
    # Card background
    card_rect = (x, y, CARD_WIDTH, CARD_HEIGHT)
    draw_rounded_rect(screen, WHITE, card_rect, CARD_CORNER_RADIUS)
    
    if not face_up:
        # Card back pattern
        inner_rect = (x + 8, y + 8, CARD_WIDTH - 16, CARD_HEIGHT - 16)
        draw_rounded_rect(screen, CARD_BACK, inner_rect, CARD_CORNER_RADIUS - 2)
        # Pattern on back
        for i in range(3):
            for j in range(4):
                pygame.draw.circle(screen, (40, 70, 120), 
                                 (x + 20 + j * 20, y + 20 + i * 30), 5)
        return
    
    # Card content
    font_small = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 32)
    font_large = pygame.font.Font(None, 42)
    
    # Suit color
    suit_color = RED if card['suit'] in ['Hearts', 'Diamonds'] else BLACK
    
    # Rank
    rank_text = card['rank'][0] if card['rank'] != '10' else '10'
    rank_surface = font_large.render(rank_text, True, suit_color)
    screen.blit(rank_surface, (x + 8, y + 8))
    
    # Suit symbol
    suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
    suit_text = suit_symbols[card['suit']]
    suit_surface = font_large.render(suit_text, True, suit_color)
    screen.blit(suit_surface, (x + CARD_WIDTH - 32, y + 8))
    
    # Center suit (larger)
    center_suit = font_medium.render(suit_text, True, suit_color)
    screen.blit(center_suit, (x + CARD_WIDTH // 2 - 12, y + CARD_HEIGHT // 2 - 12))
    
    # Bottom rank and suit (upside down)
    screen.blit(rank_surface, (x + CARD_WIDTH - 32, y + CARD_HEIGHT - 42))
    screen.blit(suit_surface, (x + 8, y + CARD_HEIGHT - 42))

def draw_button(screen, text, x, y, width, height, color, hover=False, enabled=True):
    """Draw a button with rounded corners"""
    if not enabled:
        color = GRAY
    elif hover:
        color = tuple(min(255, c + 25) for c in color)
    
    button_rect = (x, y, width, height)
    draw_rounded_rect(screen, color, button_rect, 8)
    
    font = pygame.font.Font(None, 32)
    text_surface = font.render(text, True, WHITE if enabled else LIGHT_GRAY)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

def start_new_game():
    """Initialize a new game"""
    global deck, player_hand, dealer_hand, split_hand, dealer_upcard_value
    global game_state, current_hand, main_hand_done, split_hand_done
    global feedback_message, can_double, can_split, asked_split
    
    deck = create_weighted_deck()
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop()]
    dealer_upcard_value = dealer_hand[0]['value']
    split_hand = None
    current_hand = "main"
    main_hand_done = False
    split_hand_done = False
    feedback_message = ""
    can_double = True
    can_split = (len(player_hand) == 2 and player_hand[0]['value'] == player_hand[1]['value'])
    asked_split = False
    
    if can_split:
        game_state = "split_choice"
    else:
        game_state = "playing"

def advance_to_next_hand():
    """Mark the current hand complete and move to next hand/dealer."""
    global game_state, current_hand, can_double, main_hand_done, split_hand_done
    global player_hand, split_hand

    if current_hand == "main":
        main_hand_done = True
        if split_hand and not split_hand_done and calculate_total(split_hand) <= 21:
            current_hand = "split"
            can_double = (len(split_hand) == 2)
        else:
            game_state = "dealer_turn"
    else:
        split_hand_done = True
        if not main_hand_done and calculate_total(player_hand) <= 21:
            current_hand = "main"
            can_double = (len(player_hand) == 2)
        else:
            game_state = "dealer_turn"

def handle_hit():
    """Handle hit action"""
    global player_hand, split_hand, current_hand, deck, game_state, feedback_message, feedback_color, can_double, dealer_upcard_value
    
    hand = split_hand if current_hand == "split" else player_hand
    if not hand:
        return

    move_result = evaluate_move(hand, calculate_total(hand), dealer_upcard_value, "H")
    feedback_message, feedback_color = move_result

    hand.append(deck.pop())
    can_double = False
    total = calculate_total(hand)
    
    if total > 21:
        feedback_message = f"Bust! Total: {total}"
        feedback_color = RED
        advance_to_next_hand()

def handle_stand():
    """Handle stand action"""
    global game_state, current_hand, player_hand, split_hand, feedback_message, feedback_color, dealer_upcard_value, can_double
    
    hand = split_hand if current_hand == "split" else player_hand
    if not hand:
        return
    
    total = calculate_total(hand)
    move_result = evaluate_move(hand, total, dealer_upcard_value, "S")
    feedback_message, feedback_color = move_result
    can_double = False
    advance_to_next_hand()

def handle_double():
    """Handle double action"""
    global player_hand, split_hand, current_hand, deck, game_state, feedback_message, feedback_color, can_double, dealer_upcard_value
    
    if not can_double:
        return
    
    hand = split_hand if current_hand == "split" else player_hand
    if not hand or len(hand) != 2:
        return

    move_result = evaluate_move(hand, calculate_total(hand), dealer_upcard_value, "D")
    feedback_message, feedback_color = move_result

    hand.append(deck.pop())
    can_double = False
    
    total = calculate_total(hand)
    
    if total > 21:
        feedback_message = f"Bust! Total: {total}"
        feedback_color = RED

    advance_to_next_hand()

def handle_split():
    """Handle split action"""
    global player_hand, split_hand, deck, game_state, current_hand
    global can_split, can_double, asked_split, dealer_upcard_value
    global feedback_message, feedback_color, main_hand_done, split_hand_done
    
    if not can_split or len(player_hand) != 2:
        return
    
    asked_split = True
    total = calculate_total(player_hand)
    move_result = evaluate_move(player_hand, total, dealer_upcard_value, "Y")
    feedback_message, feedback_color = move_result
    
    split_hand = [player_hand.pop()]
    player_hand.append(deck.pop())
    split_hand.append(deck.pop())
    
    main_hand_done = False
    split_hand_done = False
    can_split = False
    can_double = True
    current_hand = "main"
    game_state = "playing"

def handle_no_split():
    """Handle no split action"""
    global game_state, can_split, asked_split, dealer_upcard_value, feedback_message, feedback_color, player_hand
    
    asked_split = True
    total = calculate_total(player_hand)
    move_result = evaluate_move(player_hand, total, dealer_upcard_value, "N")
    feedback_message, feedback_color = move_result
    
    can_split = False
    game_state = "playing"

def finish_dealer_turn():
    """Complete dealer's turn and determine winner"""
    global dealer_hand, deck, game_state, player_hand, split_hand, wins, losses, draws, feedback_message, feedback_color
    
    dealer_hand.append(deck.pop())
    
    player_busted = calculate_total(player_hand) > 21
    split_busted = split_hand and calculate_total(split_hand) > 21
    
    if not (player_busted and (not split_hand or split_busted)):
        dealer_hand = dealer_turn(deck, dealer_hand)
    
    dealer_total = calculate_total(dealer_hand)
    
    results = []
    for i, hand in enumerate([player_hand, split_hand] if split_hand else [player_hand], start=1):
        if hand:
            player_total = calculate_total(hand)
            if dealer_total > 21 or (player_total > dealer_total and player_total < 22):
                results.append(f"Hand {i}: Win! ({player_total} vs {dealer_total})")
                wins += 1
            elif player_total < dealer_total or player_total > 21:
                results.append(f"Hand {i}: Lose ({player_total} vs {dealer_total})")
                losses += 1
            else:
                results.append(f"Hand {i}: Push ({player_total} vs {dealer_total})")
                draws += 1
    
    feedback_message = " | ".join(results)
    feedback_color = BLUE
    game_state = "game_over"

def main():
    global game_state, feedback_message, feedback_color
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack Trainer - Adaptive Learning")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)
    
    start_new_game()
    
    running = True
    button_hover = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if game_state == "split_choice":
                    if 450 <= mouse_x <= 590 and 700 <= mouse_y <= 755:
                        handle_split()
                    elif 610 <= mouse_x <= 750 and 700 <= mouse_y <= 755:
                        handle_no_split()
                
                elif game_state == "playing":
                    button_y = 700
                    if 450 <= mouse_x <= 590 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT:
                        handle_hit()
                    elif 610 <= mouse_x <= 750 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT:
                        handle_stand()
                    elif 770 <= mouse_x <= 910 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT and can_double:
                        handle_double()
                
                elif game_state == "game_over":
                    if 550 <= mouse_x <= 750 and 750 <= mouse_y <= 805:
                        start_new_game()
                    elif 770 <= mouse_x <= 870 and 750 <= mouse_y <= 805:
                        running = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button_hover = None
                
                if game_state == "split_choice":
                    if 450 <= mouse_x <= 590 and 700 <= mouse_y <= 755:
                        button_hover = "split_yes"
                    elif 610 <= mouse_x <= 750 and 700 <= mouse_y <= 755:
                        button_hover = "split_no"
                
                elif game_state == "playing":
                    button_y = 700
                    if 450 <= mouse_x <= 590 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT:
                        button_hover = "hit"
                    elif 610 <= mouse_x <= 750 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT:
                        button_hover = "stand"
                    elif 770 <= mouse_x <= 910 and button_y <= mouse_y <= button_y + BUTTON_HEIGHT and can_double:
                        button_hover = "double"
                
                elif game_state == "game_over":
                    if 550 <= mouse_x <= 750 and 750 <= mouse_y <= 805:
                        button_hover = "new_game"
                    elif 770 <= mouse_x <= 870 and 750 <= mouse_y <= 805:
                        button_hover = "quit"
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw dealer area
        dealer_y = 80
        dealer_label = font.render("Dealer", True, GOLD)
        screen.blit(dealer_label, (80, dealer_y - 40))
        
        dealer_total = calculate_total(dealer_hand)
        if game_state in ["dealer_turn", "game_over"]:
            for i, card in enumerate(dealer_hand):
                x = 80 + i * (CARD_WIDTH + CARD_SPACING)
                draw_card(screen, card, x, dealer_y, face_up=True)
            total_text = font_small.render(f"Total: {dealer_total}", True, WHITE)
            screen.blit(total_text, (80, dealer_y + CARD_HEIGHT + 15))
        else:
            draw_card(screen, dealer_hand[0], 80, dealer_y, face_up=True)
            draw_card(screen, {'rank': '?', 'suit': '?', 'value': 0}, 80 + CARD_WIDTH + CARD_SPACING, dealer_y, face_up=False)
        
        # Draw player area - always show main hand
        player_y = 280
        hand_label = font.render("Your Hand (Main)" if split_hand else "Your Hand", True, GOLD)
        screen.blit(hand_label, (80, player_y - 40))
        
        if player_hand:
            for i, card in enumerate(player_hand):
                x = 80 + i * (CARD_WIDTH + CARD_SPACING)
                draw_card(screen, card, x, player_y, face_up=True)
            
            player_total = calculate_total(player_hand)
            # Debug: show individual card values
            card_values = [str(card['value']) for card in player_hand]
            debug_text = font_tiny.render(f"Cards: {', '.join(card_values)}", True, LIGHT_GRAY)
            screen.blit(debug_text, (80, player_y + CARD_HEIGHT + 35))
            total_text = font_small.render(f"Total: {player_total}", True, WHITE)
            screen.blit(total_text, (80, player_y + CARD_HEIGHT + 15))
        
        # Draw split hand if exists - always show it
        if split_hand:
            split_y = 450
            split_label = font.render("Split Hand", True, GOLD)
            screen.blit(split_label, (80, split_y - 40))
            for i, card in enumerate(split_hand):
                x = 80 + i * (CARD_WIDTH + CARD_SPACING)
                draw_card(screen, card, x, split_y, face_up=True)
            split_total = calculate_total(split_hand)
            # Debug: show individual card values
            card_values = [str(card['value']) for card in split_hand]
            debug_text = font_tiny.render(f"Cards: {', '.join(card_values)}", True, LIGHT_GRAY)
            screen.blit(debug_text, (80, split_y + CARD_HEIGHT + 35))
            total_text = font_small.render(f"Total: {split_total}", True, WHITE)
            screen.blit(total_text, (80, split_y + CARD_HEIGHT + 15))
            
            # Highlight which hand is currently active
            if current_hand == "split":
                highlight_text = font_tiny.render("← Currently Playing", True, YELLOW)
                screen.blit(highlight_text, (80 + len(split_hand) * (CARD_WIDTH + CARD_SPACING) + 10, split_y + CARD_HEIGHT // 2))
            else:
                highlight_text = font_tiny.render("← Currently Playing", True, YELLOW)
                screen.blit(highlight_text, (80 + len(player_hand) * (CARD_WIDTH + CARD_SPACING) + 10, player_y + CARD_HEIGHT // 2))
        
        # Draw feedback
        if feedback_message:
            # Background for feedback
            feedback_bg = pygame.Surface((SCREEN_WIDTH - 160, 60))
            feedback_bg.set_alpha(200)
            feedback_bg.fill((0, 0, 0))
            screen.blit(feedback_bg, (80, 640))
            
            feedback_surface = font_small.render(feedback_message, True, feedback_color)
            screen.blit(feedback_surface, (100, 655))
        
        # Draw buttons
        button_y = 700
        if game_state == "split_choice":
            draw_button(screen, "Split", 450, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                       GREEN if button_hover == "split_yes" else DARK_GREEN, 
                       button_hover == "split_yes")
            draw_button(screen, "No Split", 610, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                       RED if button_hover == "split_no" else (150, 0, 0), 
                       button_hover == "split_no")
        
        elif game_state == "playing":
            draw_button(screen, "Hit", 450, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                       BLUE if button_hover == "hit" else (0, 100, 200), 
                       button_hover == "hit")
            draw_button(screen, "Stand", 610, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                       ORANGE if button_hover == "stand" else (200, 120, 0), 
                       button_hover == "stand")
            draw_button(screen, "Double", 770, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                       YELLOW if button_hover == "double" else (200, 180, 0), 
                       button_hover == "double", enabled=can_double)
        
        elif game_state == "game_over":
            draw_button(screen, "New Game", 550, 750, 200, BUTTON_HEIGHT, 
                       GREEN if button_hover == "new_game" else DARK_GREEN, 
                       button_hover == "new_game")
            draw_button(screen, "Quit", 770, 750, 100, BUTTON_HEIGHT, 
                       RED if button_hover == "quit" else (150, 0, 0), 
                       button_hover == "quit")
        
        # Draw statistics panel
        stats_x = SCREEN_WIDTH - 320
        stats_y = 80
        
        # Panel background
        panel_bg = pygame.Surface((300, 500))
        panel_bg.set_alpha(220)
        panel_bg.fill((0, 0, 0))
        screen.blit(panel_bg, (stats_x - 10, stats_y - 10))
        
        title = font_small.render("Statistics", True, GOLD)
        screen.blit(title, (stats_x, stats_y))
        
        stats_text = [
            f"Wins: {wins}",
            f"Losses: {losses}",
            f"Draws: {draws}",
            "",
            f"Correct: {num_correct}",
            f"Incorrect: {num_incorrect}",
        ]
        if num_correct + num_incorrect > 0:
            accuracy = num_correct / (num_correct + num_incorrect) * 100
            stats_text.append(f"Accuracy: {accuracy:.1f}%")
        
        for i, text in enumerate(stats_text):
            stat_surface = font_tiny.render(text, True, WHITE)
            screen.blit(stat_surface, (stats_x, stats_y + 40 + i * 30))
        
        # Draw training focus
        weak_hands = get_weak_hands()
        if weak_hands and training_mode:
            focus_y = stats_y + 280
            focus_title = font_small.render("Training Focus", True, YELLOW)
            screen.blit(focus_title, (stats_x, focus_y))
            
            category_names = {
                "hard_totals": "Hard",
                "soft_totals": "Soft",
                "pair_splitting": "Pairs"
            }
            
            for i, (category, hand_value, accuracy) in enumerate(weak_hands[:5]):  # Top 5 weak hands
                category_name = category_names.get(category, category)
                text = f"{category_name} {hand_value}: {accuracy*100:.0f}%"
                color = RED if accuracy < 0.5 else ORANGE
                focus_surface = font_tiny.render(text, True, color)
                screen.blit(focus_surface, (stats_x, focus_y + 30 + i * 25))
        
        # Auto-advance dealer turn
        if game_state == "dealer_turn":
            pygame.time.wait(500)
            finish_dealer_turn()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

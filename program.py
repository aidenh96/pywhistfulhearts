################################################################################
#
#   Project 3: Whistful Hearts FINAL
#   Aiden H
#   Date: 29/05/2015
#

################################################################################
#
#   INDEX
#   ----------
#
#   1. Constants and imports
#   2. Main Functions
#       A. is_broken_hearts
#       B. is_valid_play
#       C. score_game
#       D. play
#       E. predict_score
#   3. Helper Functions
#       A. check_hearts
#       B. winner
#       C. trick_points
#       D. card_sort
#       E. play_duck
#       F. play_void
#       G. void_data
#       H. suit_count
#       I. get_cards
#       J.get_winner_score
#

################################################################################
#
#   1. Constants and imports
#
from operator import itemgetter
RANK = {"A": 14, "K": 13, "Q": 12, "J":11, "0": 10, "9":9, "8":8, "7":7, \
"6":6, "5":5, "4":4, "3":3, "2":2, "1": 1}
# This assigns each card ranking an integer value that can be used to order cards based on this rank.
# NOTE: 1 is defined to prevent index/key errors

################################################################################
#
#   2. Main Functions
#

def is_broken_hearts(prev_tricks, curr_trick = ()):
    '''
    This function will determine if hearts has been broken in the given tricks.
    '''

    if curr_trick: # Checks for broken hearts in the current trick if defined
        if check_hearts(curr_trick):
            return(True)

    if check_hearts(prev_tricks[3:]): # Checks for broken hearts in all rounds after the third
        return(True)

    return(False)

################################################################################

def is_valid_play(play, curr_trick, hand, prev_tricks, broken=is_broken_hearts):
    '''
    This function determines if a selected card is a valid card that can be
    played in the current trick, based on data from the previous trick, the
    players hand and from the 'is_broken_hearts' function.
    '''

    suitsInHand = set([i[1] for i in hand]) # Finds which suits are in players hand

    if len(hand) == 1: # If there is only 1 card left in had, it must be valid
        return(True)

    if play in hand:  # Card has to be in the players hand for them to use it

        if curr_trick: # Checks if the trick has already started

            leadSuit = curr_trick[0][1] # Finds the leading suit for the trick being played

            if leadSuit in "".join(hand): # Checks if player has any cards in the leading suit (must play it)
                if leadSuit in play: # Checks if their card is in the leading suit
                    return(True)
                else:
                    return(False)

        # Conditions for if a player doesn't have a card in the leading suit
        # or if the player must start the trick
        if len(prev_tricks) < 3: # In the first three rounds, any card my be played
            return(True)

        if not broken(prev_tricks, curr_trick): # In main rounds, heart cannot be played until broken

            if suitsInHand == {'H'}: # If player only has hearts, they can break hearts
                return(True)
            elif 'H' in play: # If player has suits other than hearts, they cannot play hearts
                return(False)
            else:
                return(True)
        else: # If heart is broken, any card can be played
            return(True)

    return(False)

################################################################################

def score_game(tricks, deck_top):
    trumps = deck_top[0][1] # Determines the trumps for the preliminary rounds
    playerScore = {0:0, 1:0, 2:0, 3:0} # Stores each players score
    nextTrickOrd = [0,1,2,3] # Used to determine the order of the next trick
    currWinner = 0
    win = ""

    for trick in tricks:

        if trick in tricks[:3]: # Finds the winning play for a trick in the preliminary rounds
            win = winner(trick, trumps, True)
            mainRounds = False
        else:
            win = winner(trick) # Finds the winning play for a trick in the main rounds
            mainRounds = True

        currWinner = nextTrickOrd[trick.index(win)] #Determins the index of the current winner
        nextTrickOrd = []
        nextPlayer = currWinner

        if mainRounds: # Only calculates score if the game is in the main rounds
            playerScore[currWinner] += trick_points(trick) # Use 'trick_points' function to determine score

        while len(nextTrickOrd) < 4:
            # Updates the play order for each trick so it can be used to
            # determine which player plays which card

            nextTrickOrd.append(nextPlayer)

            if nextPlayer == 3:
                # Restarts the play count at 0 if it reaches 3 (the last player)
                nextPlayer = 0
            else:
                nextPlayer = nextPlayer + 1

    # SHOOTING THE MOON
    pointCount = 0
    maxPoints = 26 # Max number of points a play can get

    for trick in tricks[:3]:
        # Determines the number of points left after the first three rounds have been played
        for card in trick:
            # 'maxPoints' value is reduced as each point bearing card is found
            if 'H' in card:
                maxPoints -= 1
            elif 'QS' == card:
                maxPoints -= 13

    for trick in tricks[4:]:
        # Determines the amount of points a player could have gotten within the given tricks
        for card in trick:
            # 'pointCount' value is increased as each point bearing card is found
            if 'H' in card:
                pointCount += 1
            elif card == 'QS':
                pointCount += 13

    # For moon to be shot, the max available points must equal the number of
    # point accumulated in the given tricks and this value must be in the scores
    # dictionary indicting that a player actually has that score
    if pointCount == maxPoints and pointCount in playerScore.values():

        for player, score in playerScore.items():
            if score != 0:
                # Finds which player it was that shot the moon
                playerScore[player] = -(playerScore[player]) # Negates that players score

    return((playerScore[0], playerScore[1], playerScore[2], playerScore[3]))

################################################################################

def play(curr_trick, hand, prev_tricks, deck_top, is_valid=is_valid_play, \
score=score_game, player_data=None, suppress_player_data=False):
    '''
    This function determines what card to play, choosing out of multiple
    strategies. Note that the strategies are in order for weakest to strongest
    so that the strongest valid strategy will be played.
    '''

    # These cards are either high valued-point bearing cards or high valued cards
    badCards = ['QS', 'KS', 'AH', 'KH', 'QH', 'AS', 'AD', 'AC', 'KD', 'KC', 'QD', 'QC']
    haveQueen = False
    checkVoid = False
    validCards = []
    winCount = 0

    # Determines if in first round
    if not prev_tricks:
        checkVoid =  True # Allows voiding strategy to be attempted

    for card in hand:
        if card == 'QS': # Checks to see if hand contains Queen of Spades
            haveQueen = True
        if is_valid(card, curr_trick, hand, prev_tricks): # Adds cards that can be played to a list
            validCards.append(card)

    playCard = validCards[0] # Temporarily set the 'playCard' to the first valid card

    # Checks voiding a suit strategy can be used
    if not suppress_player_data:
        # Generates 'player_data' needed to void a suit
        player_data = void_data(hand, prev_tricks, haveQueen, checkVoid, player_data)

    if len(prev_tricks) < 3: # All plays for preliminary rounds

        # Play high valued heart cards to get rid of them
        if get_cards(validCards, 'H'):
            playCard = get_cards(validCards, 'H')[0]
        else:
            # Play highest valued card to get rid of it
            playCard = card_sort(validCards, ("C", "D", "S", "H"))[0]

        # Get rid of bad cards in the first round first if possible
        for card in badCards:
            if card in validCards:
                playCard = card
                break

        if not suppress_player_data:
            # Attempt to void a suit if possible
            # Makes sure there is a void suit and voiding hasn't finished
            if player_data['playVoid'] and not player_data['compVoid']:
                # Tries to not win the trick if deck top has a suit that is trying to be voided
                if deck_top[-1][1] == player_data['voidSuit']:
                    if play_void(validCards, player_data['voidSuit'], False):
                        playCard = play_void(validCards, player_data['voidSuit'], False)

                elif play_void(validCards, player_data['voidSuit'], force_return=True):
                    playCard = play_void(validCards, player_data['voidSuit'], force_return=True)


    if len(prev_tricks) > 3: # All plays for main rounds

        # If no strategy can be used, the lowest ranked card will be played
        playCard = card_sort(validCards, ('H', 'S', 'C', 'D'), False)[0]

        if not curr_trick:
            # Play a middle ranged card in attempt to not win trick
            for card in card_sort(validCards, ('D', 'C', 'S', 'H')):
                for val in [7,6,5]: # Designated middle range values
                    if card[0] == val:
                        playCard = card
                    break

        if len(curr_trick) == 3:
            # Plays for if the player is the last to put down card in a trick

            for card in validCards:
                curr_trick = list(curr_trick)
                if winner((curr_trick + [card])) == card:
                    winCount += 1 # Counts how many valid plays lead to a win

            # Plays highest valued card because going to win anyway
            if winCount == len(validCards) and len(validCards) > 2:
                    playCard = card_sort(validCards, ('H', 'S', 'C', 'D'))[0]

        if curr_trick:
            leadSuit = curr_trick[0][1] # Determines leading suit for 'curr_trick'

            # If the game is in the main rounds and the trick has begun, the
            # 'ducking' strategy will be used if possible
            if play_duck(curr_trick, validCards):
                playCard = play_duck(curr_trick, validCards)

            # If player doesn't have a card in a leading suit, play the highest
            # point cards first, and if that is not possible, play highest value card
            if not get_cards(hand, leadSuit):
                if 'QS' in validCards:
                    playCard = 'QS'
                elif get_cards(validCards, 'H'):
                    playCard = get_cards(validCards, 'H')[0]
                else:
                    playCard = card_sort(validCards, ('H', 'S', 'C', 'D'))[0]

        # Attempt to void a suit if possible
        if not suppress_player_data:
            if player_data['playVoid'] and not player_data['compVoid']:
                if play_void(validCards, player_data['voidSuit'], force_return=True):
                    playCard = play_void(validCards, player_data['voidSuit'], force_return=True)

    # Determines what to return based on if 'player_data' is being used
    if suppress_player_data:
        return(playCard)
    else:
        return((playCard, player_data))

################################################################################

def predict_score(hand):
    '''
    Predicts a score for a player based on the cards in their initial hand.
    '''
    highCards = '90JQKA'
    lowCards = '234567'
    heartCount = 0
    score = 0
    highCardCount = 0
    lowCardCount = 0

    for card in hand:
        if 'H' in card:
            if card[0] in highCards: # Adds 1 for high heart cards
                score += 1
            heartCount += 1

    heartCount = 13 - heartCount # Calculates hearts distributed among other players
    score += heartCount % 4 # Shares heart cards between players, adds 1 point for each heart

    for card in hand:
        # Determines the number of high and low cards in the hand
        if card[0] in highCards:
            highCardCount += 1
        elif card[0] in lowCards:
            lowCardCount += 1

    score += (highCardCount % 2) # Assumes half the high cards in hand will attract points

    if 'QS' not in hand:
        if highCardCount > 6:
            score += 13

    # This slightly adjusts scores manually
    if score >= 5 and score < 10:
        score += 1
    elif score > 15:
        score = 0

    # Makes sure score is bigger than zero before returning as shooting the moon
    # is NOT taken into account in this function
    if int(score) > 0:
        return(int(score))
    else:
        return(0)

################################################################################
#
#   3. Helper Functions
#

def check_hearts(tricks):
    '''
    This function iterates through a list of tricks, checking if there is a
    heart present within that trick.
    '''
    for trick in tricks:
        for card in trick:
            if "H" in card:
                return(True) # 'True' is immediately returned if a heart is found

    return(False) #If no hearts are found, 'False' is returned

################################################################################

def winner(trick, trumps="", prelim=False):
    '''
    This function determines the winning play in a trick. If the trick is part
    of the preliminary three rounds, 'trumps' needs to be defined and the
    'prelim' argument must be 'True'
    '''

    win = "1"  # '1' defined as default to prevent index/key errors
    trickSuits = set([i[1] for i in trick]) # Determines all played suits in a trick

    if prelim and trumps in trickSuits:
        # If the game is in the preliminary rounds and a trumps has been played, it will win
        for card in trick:

            if trumps in card:
                # This determines the highest ranking card played and assigns it to 'win'
                if RANK[card[0]] > RANK[win[0]]:
                    win = card

    # If the game is in preliminary round and no trumps played or if the game
    # is in the main rounds the following checks will occur
    else:
        win = trick[0] # wining card temporarily set to fist card in trick
        leadSuit = trick[0][1] # Determines leading suit for the trick

        for card in trick:
            if leadSuit in card:
                # The highest played card in the leading suit will win
                if RANK[card[0]] > RANK[win[0]]:
                    win = card

    return(win)

################################################################################

def trick_points(trick):
    '''
    This function determines the number of points that a trick is worth.
    '''
    points = 0 # Initialize a point counter

    for card in trick:
        # Iterates through cards and adds points for each heart found, and for QS
        if 'H' in card:
            points += 1
        elif 'QS' == card:
            points += 13

    return(points)

################################################################################

def card_sort(cards, suitOrd=("C", "H", "S", "D"), descend=True):
    '''
    This function sorts card based on value and suit. The suit ranking is
    customizable to suit various needs of other function and the order
    (ascending or descending) can also be set, with descending as default.
    '''
    cards = list(cards)
    cardTup = []

    if len(cards) < 1:
        # If there is only one card, this cannot be ordered, so it is returned
        return(cards)
    else:
        card = cards[0] # Otherwise, the fist card in the 'cards' list is set as the temporary output

    # This creates a dictionary for the ranking of suits based on the defined suit order
    rank = 0
    suitRank = {}
    for suit in suitOrd:
        suitRank[suit] = rank
        rank += 1

    # Converts each card into a 3-tuple: (value rank, suit rank, card)
    for card in cards:
        cardTup.append((RANK[card[0]], suitRank[card[1]], card))

    # The sorted function is used to order the tuples based on their first and
    # second elements the last element of the ordered tuples is returned as a
    # list either ascending or descending as defined
    if descend:
        return([i[2] for i in sorted(cardTup, reverse=True)])
    else:
        return([i[2] for i in sorted(cardTup)])

################################################################################

def play_duck(trick, cards):
    '''
    This function selects a card to play using the strategy of 'ducking.'
    Ducking is always playing the highest card under the card that was played
    by others in the current trick.
    '''
    leadSuit = trick[0][1] # Determines the leading suit for the current trick
    validCards = []

    for card in trick:
        # Card that can be ducked MUST be in the leading suit
        if leadSuit in card:
            validCards.append(card)

    maxValue = RANK[card_sort(validCards)[0][0]] # Get the highest ranked card in the leading suit
    validCards = [] # Reset 'validCards' list

    for card in cards:
        # Finds all the cards with a rank lower than the highest ranked card of the leading suit
        if RANK[card[0]] < maxValue:
            validCards.append(card)

    if validCards:
        # Get the highest card that is under the highest ranked card in the trick
        return(card_sort(validCards)[0])
    else:
        return(False) # If there isn't any cards lower than the 'maxValue', ducking cannot be used

################################################################################

def play_void(cards, voidSuit, playHigh = True, force_return=False):
    '''
    This function will return a card that can be played when attempting to void
    a suit. Optionally determinable is if a high to low card is needed to be, or
    to force a return if a valid move is possible.
    '''
    vaildVoidCards = []
    playCard = ""

    for card in cards:
        # Finds all the possible cards that can be played to void a suit
        if voidSuit in card:
            vaildVoidCards.append(card)

    if vaildVoidCards and force_return:
        # Forces a return if one is possible
        return(card_sort(vaildVoidCards)[0])

    if vaildVoidCards and playHigh:
        # Plays a high card that can be played to void a suit
        playCard = card_sort(vaildVoidCards)[0]
        if RANK[playCard[0]] > 8: # Uses global card rank to determine value
            return(playCard)

    if vaildVoidCards and not playHigh:
        # Plays a low card that can be played to void a suit
        playCard = card_sort(vaildVoidCards, descend=False)[0]
        if RANK[playCard[0]] < 7: # Uses global card rank to determine value
            return(playCard)

    return(False)

################################################################################

def void_data(hand, prev_tricks, haveQueen, checkVoid, player_data):
    '''
    This function updates 'player_data' that is used for voiding. It also
    determines if which suit to void, and if voiding has been completed.
    '''

    if len(prev_tricks) > 3:
        # Stops trying to void hearts after the first three rounds
        if player_data['voidSuit'] == 'H':
            player_data['compVoid'] == True
            player_data['voidHearts'] == False # Prevents reattempt to void hearts

    if prev_tricks:
        # Allows new void to be attempted if initial one has finished
        if player_data['compVoid']:
            checkVoid = True

    if checkVoid: # Checks if a suit can be voided
        player_data = {'playVoid': False, 'voidSuit':"",'compVoid': False, 'voidHearts': True}

        #Check to see if a void suit can be made
        if not player_data['voidSuit']:
            if suit_count(hand, haveQueen, player_data['voidHearts']):
                player_data['voidSuit'] = suit_count(hand, haveQueen, player_data['voidHearts'])
                player_data['playVoid'] = True

    # Determines if voiding a suit had been completed
    if player_data['playVoid']:
        if player_data['voidSuit'] not in [i[1] for i in hand]:
            player_data['compVoid'] = True

    return(player_data)

################################################################################

def suit_count(hand, haveQueen=False, voidHearts=True):
    '''
    This function count the number of cards in a suit for a hand of cards and
    returns the suits with the least amount of cards in it, if that value is < 3.
    It also doesn't count specific suits as defined in the arguments.
    '''
    suitCount = {'C':0,'H':0,'D':0,'S':0} # Dictionary to store count

    for card in hand:
        suitCount[card[1]] += 1

    if haveQueen: # Removes spades count of the Queen of Spades is present
        suitCount.pop('S')
    if not voidHearts: # Removes hearts if necessary
        suitCount.pop('H')

    suitCount = sorted(suitCount.items(), key=itemgetter(1, 0)) # Sorts based on count then suit

    for tup in suitCount:
        if tup[1] == 0: # Removes all suits that don't have any cards in them
            suitCount.remove(tup)
        if tup[1] >= 4: # Removes any suits that have more that three cards in them
            suitCount.remove(tup)

    if suitCount:
        return(suitCount[0][0]) # Returns the suit with lowest count
    else:
        return(False)

################################################################################
def get_cards(cards, suit):
    '''
    This function iterates over a list of cards and returns a sorted list of
    cards that are all from a defined suit.
    '''
    output = []

    for card in cards:
        if suit in card:
            output.append(card)

    if output:
        return(card_sort(output)) # Using card_sort function to sort cards
    else:
        return(False)

################################################################################

def get_winner_score(trick, round_id, deck_top):
    '''
    This function determines the index of the winner in a trick and how many
    points they receive.
    '''
    if round_id <= 3:
        # Gets the winner for a trick within the first three rounds
        win = winner(trick, deck_top[0][1], True)
    else:
        # Gets the winner for a trick after the first three rounds
        win = winner(trick)

    # Returns the index of th winner relative to the current trick, and their points
    return((trick.index(win) , trick_points(trick)))

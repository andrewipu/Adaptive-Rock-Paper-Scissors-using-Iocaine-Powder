# filepath: c:\VS Code\Rock-Paper-Scissors using Iocaine Powder\Iocaine_RPS.py
import random
import time
import sys
import cProfile # For profiling the code
import pstats # For saving profiling results
from iocaine_cython_parts import match_single, match_both, StatsCython, do_history, do_predict, PredictCython, scan_predict 

# ------------------------------------------------------------------------------
# Utility functions for rock-paper-scissors moves.
# In our mapping, 0 = Rock, 1 = Paper, 2 = Scissors.
# The arrays below tell you which move beats or loses to a given move.
# For example, will_beat[0] == 1 means that Paper (1) beats Rock (0).
# Similarly, will_lose_to[0] == 2 means that Scissors (2) lose to Rock (0).
will_beat = [1, 2, 0]
will_lose_to = [2, 0, 1]


# ------------------------------------------------------------------------------
# match_single: Given a candidate starting index "i" in a history (a list of moves)
# and the current number of moves, this function compares the subsequence starting
# at index i with the ending sequence of the history. It returns how many moves
# match consecutively, comparing backwards from the end.
#
# In the C version, pointer arithmetic is used; here we work with list indices.

# def match_single(i, history):
#     num = len(history)
#     # high_index points to the last move in the history.
#     high_index = num - 1
#     # low_index starts at candidate position i.
#     low_index = i
#     # Compare moves while we can go backwards and the moves match.
#     while low_index > 0 and history[low_index] == history[high_index]:
#         low_index -= 1
#         high_index -= 1
#     # The number of matching moves is the distance moved from the end.
#     return (num - 1) - high_index


# ------------------------------------------------------------------------------
# match_both: For a given candidate index "i" (in the history arrays for both players),
# this function checks how many moves match backwards from the end when comparing both
# the opponent’s and your own histories.
#
# Note: In the original C code the histories are 1-indexed (with element 0 being the count).
# Here our histories are plain Python lists (0-indexed), so we adjust the indexing accordingly.

# def match_both(i, my_history, opp_history):
#     num = len(my_history)  # Both histories have the same length.
#     j = 0
#     # Compare backwards from the end: compare the j-th last move with the move at candidate i.
#     while j < i and opp_history[num - 1 - j] == opp_history[i - 1 - j] and \
#           my_history[num - 1 - j] == my_history[i - 1 - j]:
#         j += 1
#     return j


# ------------------------------------------------------------------------------
# do_history: Given a time window "age" and the two histories (your moves and opponent's moves),
# this function searches for the longest matching subsequences in three cases:
#
# 1. Matching in your own history.
# 2. Matching in the opponent's history.
# 3. Matching in both histories simultaneously.
#
# It returns a list "best" of three indices (one for each case) that provided the best match.
# def do_history(age, my_history, opp_history):
#     num = len(my_history)
#     # Initialize best indices and best match lengths for each of the three cases.
#     best = [0, 0, 0]         # 0: my history, 1: opponent history, 2: both histories
#     best_length = [0, 0, 0]
    
#     # Look for best match in your own history.
#     for i in range(num - 1, max(num - age, best_length[0]), -1):
#         j = match_single(i, my_history)
#         if j > best_length[0]:
#             best_length[0] = j
#             best[0] = i
#             if j > num // 2:
#                 break

#     # Look for best match in opponent's history.
#     for i in range(num - 1, max(num - age, best_length[1]), -1):
#         j = match_single(i, opp_history)
#         if j > best_length[1]:
#             best_length[1] = j
#             best[1] = i
#             if j > num // 2:
#                 break

#     # Look for best match in both histories simultaneously.
#     for i in range(num - 1, max(num - age, best_length[2]), -1):
#         j = match_both(i, my_history, opp_history)
#         if j > best_length[2]:
#             best_length[2] = j
#             best[2] = i
#             if j > num // 2:
#                 break

#     return best


# ------------------------------------------------------------------------------
# Stats class:
# This class implements what in C was a struct "stats" holding a 2D array "sum" and an "age".
# "trials" determines how many rows we keep. The sum array tracks a running difference
# for each move (0, 1, 2) over time.
# class Stats:
#     def __init__(self, trials):
#         self.trials = trials
#         self.age = 0
#         # Create a (trials+1) x 3 list initialized to zeros.
#         self.sum = [[0, 0, 0] for _ in range(trials + 1)]
    
#     # reset_stats: resets the age to 0 and clears the first row.
#     def reset(self):
#         self.age = 0
#         self.sum[0] = [0, 0, 0]
    
#     # add_stats: update the current row by adding delta to the given move index.
#     def add(self, move, delta):
#         self.sum[self.age][move] += delta
    
#     # next_stats: increment the age (up to trials) and copy over the previous row.
#     def next(self):
#         if self.age < self.trials:
#             self.age += 1
#             self.sum[self.age] = self.sum[self.age - 1].copy()
    
#     # max_stats: given a window "age", compute the difference in statistics over that window.
#     # It returns the index (move) with the highest difference (score) and a flag indicating validity.
#     def max_stats(self, age):
#         which = -1
#         score = -10**9  # Start with a very low score.
#         for i in range(3):
#             # If the window is longer than the stats recorded, use the entire history.
#             if age > self.age:
#                 diff = self.sum[self.age][i]
#             else:
#                 diff = self.sum[self.age][i] - self.sum[self.age - age][i]
#             if diff > score:
#                 score = diff
#                 which = i
#         return which, score, (which != -1)


# ------------------------------------------------------------------------------
# Predict class:
# This corresponds to the C struct "predict". Each Predict holds a Stats object
# and the last move prediction ("last").
# class Predict:
#     def __init__(self, trials):
#         self.st = StatsCython(trials)
#         self.last = -1  # -1 indicates no previous prediction.
    
#     def reset(self):
#         self.st.reset()
#         self.last = -1


# ------------------------------------------------------------------------------
# do_predict: This function updates a Predict structure.
#
# Parameters:
#   pred  - a Predict object
#   last  - the opponent's last move (or -1 if none)
#   guess - the algorithm's current guess for the opponent's move
#
# If a previous move exists (pred.last != -1), the function calculates a "difference"
# between the opponent's last move and the previous guess. It then updates the stats:
# it adds one to the move that would beat that difference and subtracts one from the move
# that would lose to that difference. Finally, it advances the stats (like moving to the next row)
# and sets the new prediction.
# def do_predict(pred, last, guess):
#     if last != -1:
#         diff = (3 + last - pred.last) % 3
#         pred.st.add(will_beat[diff], 1)
#         pred.st.add(will_lose_to[diff], -1)
#         pred.st.next()
#     pred.last = guess


# ------------------------------------------------------------------------------
# scan_predict: This function looks at a Predict structure’s stats over a given window "age"
# and returns the move that best fits (by adding the stored "which" to the last prediction).
# It returns a tuple (move, score). If no valid move is found, move will be None.
# def scan_predict(pred, age):
#     which, score, valid = pred.st.max_stats(age)
#     if valid:
#         move = (pred.last + which) % 3
#         return move, score
#     else:
#         return None, score


# ------------------------------------------------------------------------------
# Now we set up the main Iocaine bot class.
#
# The C struct "iocaine" contains many predictors arranged in multi-dimensional arrays.
# In our Python version we mimic this using lists-of-lists.
class IocaineBot:
    def __init__(self, trials=50):
        self.trials = trials
        # The ages array defines different time windows used in the prediction.
        self.ages = [1000, 100, 10, 5, 2, 1]
        self.num_ages = len(self.ages)
        
        # Histories for the bot's moves and the opponent's moves.
        self.my_history = []   # Bot's moves (each move is 0, 1, or 2)
        self.opp_history = []  # Opponent's moves
        
        # pr_history: for each age, for each of 3 matching cases, and 2 predictions each.
        self.pr_history = [[[PredictCython(trials) for _ in range(2)]
                            for _ in range(3)]
                           for _ in range(self.num_ages)]
        # pr_freq: for each age, two predictors.
        self.pr_freq = [[PredictCython(trials) for _ in range(2)]
                        for _ in range(self.num_ages)]
        # pr_fixed and pr_random: two single predictors.
        self.pr_fixed = PredictCython(trials)
        self.pr_random = PredictCython(trials)
        # pr_meta: one predictor per age.
        self.pr_meta = [PredictCython(trials) for _ in range(self.num_ages)]
        # Stats for our moves and the opponent's moves.
        self.stats = [StatsCython(trials), StatsCython(trials)]
    
    # A simple version of biased_roshambo: returns a random move (can be replaced with a more sophisticated bias).
    def biased_roshambo(self):
        return random.choice([0, 1, 2])
    
    # The main function that calculates the bot's move.
    # It follows the same steps as the C function "iocaine".
    def get_move(self):
        num = len(self.my_history)
        # Determine the opponent's last move (if any).
        last = self.opp_history[-1] if num > 0 else -1
        # Use a random guess as a baseline.
        guess = self.biased_roshambo()
        
        # Initialization: if no moves have been played yet, reset all predictors and stats.
        if num == 0:
            for a in range(self.num_ages):
                self.pr_meta[a].reset()
                for p in range(2):
                    for w in range(3):
                        self.pr_history[a][w][p].reset()
                    self.pr_freq[a][p].reset()
            for p in range(2):
                self.stats[p].reset()
            self.pr_random.reset()
            self.pr_fixed.reset()
        else:
            # Update the stats based on the most recent moves.
            # In the original C code the moves are stored in the array at index "num".
            # Here we simply use the last move in the history lists.
            self.stats[0].add(self.my_history[-1], 1)
            self.stats[1].add(self.opp_history[-1], 1)
        
        # For each time window (age), update predictions.
        for a in range(self.num_ages):
            # Find best matching indices for this age.
            best = do_history(self.ages[a], self.my_history, self.opp_history)
            for w in range(3):
                b = best[w]
                if b == 0:
                    # No history found – use the baseline guess.
                    do_predict(self.pr_history[a][w][0], last, guess)
                    do_predict(self.pr_history[a][w][1], last, guess)
                else:
                    # If a match is found, use the move following the matching sequence.
                    # (In the original C code, b+1 is used to index the next move.)
                    my_next = self.my_history[b+1] if (b+1) < len(self.my_history) else guess
                    opp_next = self.opp_history[b+1] if (b+1) < len(self.opp_history) else guess
                    do_predict(self.pr_history[a][w][0], last, my_next)
                    do_predict(self.pr_history[a][w][1], last, opp_next)
            # Also update frequency predictors using overall stats.
            for p in range(2):
                best_stat, _, valid = self.stats[p].max_stats(self.ages[a])
                if valid:
                    do_predict(self.pr_freq[a][p], last, best_stat)
                else:
                    do_predict(self.pr_freq[a][p], last, guess)
        
        # Update fixed and random predictors.
        do_predict(self.pr_random, last, guess)
        do_predict(self.pr_fixed, last, 0)
        
        # Combine predictions from the various predictors.
        move = -1
        score = -10**9
        for a in range(self.num_ages):
            for aa in range(self.num_ages):
                for p in range(2):
                    for w in range(3):
                        pred_move, pred_score = scan_predict(self.pr_history[aa][w][p], self.ages[a])
                        if pred_move is not None and pred_score > score:
                            score = pred_score
                            move = pred_move
                    pred_move, pred_score = scan_predict(self.pr_freq[aa][p], self.ages[a])
                    if pred_move is not None and pred_score > score:
                        score = pred_score
                        move = pred_move
            pred_move, pred_score = scan_predict(self.pr_random, self.ages[a])
            if pred_move is not None and pred_score > score:
                score = pred_score
                move = pred_move
            pred_move, pred_score = scan_predict(self.pr_fixed, self.ages[a])
            if pred_move is not None and pred_score > score:
                score = pred_score
                move = pred_move
            do_predict(self.pr_meta[a], last, move)
        
        final_move = -1
        score = -10**9
        for a in range(self.num_ages):
            pred_move, pred_score = scan_predict(self.pr_meta[a], self.trials)
            if pred_move is not None and pred_score > score:
                score = pred_score
                final_move = pred_move
        
        # Return the chosen move.
        return final_move

    # A helper method to update the histories after a round.
    # It expects your move and the opponent's move (each should be 0, 1, or 2).
    def update_history(self, my_move, opp_move):
        self.my_history.append(my_move)
        self.opp_history.append(opp_move)


# Simulation Function
def run_simulation(bot, num_rounds):
    print(f"Starting simulation for {num_rounds} rounds...")
    simulation_start_time = time.perf_counter()

    total_get_move_wall_time_sec = 0.0
    total_get_move_cpu_time_sec = 0.0

    # Initialize bot if it has an init method (already done in __main__ but good practice if used elsewhere)
    if hasattr(bot, '_iocaine_init') and callable(getattr(bot, '_iocaine_init')):
        bot._iocaine_init()
    elif hasattr(bot, 'iocaine_init') and callable(getattr(bot, 'iocaine_init')):
        bot.iocaine_init()

    for i in range(num_rounds):
        # --- Measure bot.get_move() ---
        wall_start_time = time.perf_counter()
        cpu_start_time = time.process_time()

        # Bot determines its move
        my_move = bot.get_move()

        cpu_end_time = time.process_time()
        wall_end_time = time.perf_counter()
        # --- End Measurement ---

        wall_time_taken = wall_end_time - wall_start_time
        cpu_time_taken = cpu_end_time - cpu_start_time

        total_get_move_wall_time_sec += wall_time_taken
        total_get_move_cpu_time_sec += cpu_time_taken

        # Simulate an opponent's move (e.g., using the bot's biased random choice)
        # In a real profiling scenario for the bot's learning, you might use another bot
        # or a more complex opponent. For now, this is fine for profiling get_move.
        opponent_move = bot.biased_roshambo() # Or random.choice([0,1,2])

        # Update bot's history
        bot.update_history(my_move, opponent_move)

        if (i + 1) % (num_rounds // 10 if num_rounds >= 10 else 1) == 0:
            print(f"Simulation round {i + 1}/{num_rounds} completed.")


    simulation_end_time = time.perf_counter()
    print(f"Simulation finished in {simulation_end_time - simulation_start_time:.2f} seconds.")

    if num_rounds > 0:
        print("\n--- Simulation Performance Summary ---")
        print(f"Total bot.get_move() calls: {num_rounds}")
        print(f"Average bot.get_move() Wall-clock time: {total_get_move_wall_time_sec / num_rounds:.6f} seconds")
        print(f"Average bot.get_move() CPU time: {total_get_move_cpu_time_sec / num_rounds:.6f} seconds")
        print(f"Total Wall-clock time for all get_move() calls: {total_get_move_wall_time_sec:.6f} seconds")
        print(f"Total CPU time for all get_move() calls: {total_get_move_cpu_time_sec:.6f} seconds")


# Simulation main function
if __name__ == "__main__":
    bot = IocaineBot(trials=50) # You might want to adjust trials for simulation

    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        # Simulation Mode
        num_simulation_rounds = 1000 # Number of rounds for simulation
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            num_simulation_rounds = int(sys.argv[2])

        profiler = cProfile.Profile()
        profiler.disable()
        # profiler.enable()

        run_simulation(bot, num_simulation_rounds)

        profiler.disable()

        # Save the profiling data
        profile_file = "iocaine_rps_profile.prof"
        profiler.dump_stats(profile_file)
        # Replaced with a dump so snakeviz can read it
        # with open(profile_file, "w") as f:
        #     ps = pstats.Stats(profiler, stream=f)
        #     ps.sort_stats(pstats.SortKey.CUMULATIVE) # Sort by cumulative time
        #     ps.print_stats()
        
        print(f"\nProfiling data saved to {profile_file}")
        print(f"To visualize, install snakeviz (pip install snakeviz) and run:")
        print(f"snakeviz {profile_file}")

    else:
        # Interactive Mode (your existing code)
        print("Welcome to Rock-Paper-Scissors using IocaineBot!")
        print("Enter your move: r (rock), p (paper), s (scissors). Ctrl+C to quit.")
        print("To run simulation: python Iocaine_RPS.py simulate [num_rounds]")
        move_map = {'r': 0, 'p': 1, 's': 2}
        rev_move_map = {0: 'rock', 1: 'paper', 2: 'scissors'}

        user_score = 0
        bot_score = 0

        total_wall_time_sec = 0.0
        total_cpu_time_sec = 0.0
        num_bot_calls = 0

        if hasattr(bot, '_iocaine_init') and callable(getattr(bot, '_iocaine_init')):
            bot._iocaine_init()
        elif hasattr(bot, 'iocaine_init') and callable(getattr(bot, 'iocaine_init')):
            bot.iocaine_init()

        try:
            while True:
                print(f"\n--- Round {num_bot_calls + 1} ---")
                user_input = input("Your move (r/p/s): ").strip().lower()

                if user_input not in move_map:
                    print("Invalid move. Please enter r, p, or s")
                    continue

                user_move = move_map[user_input]

                wall_start_time = time.perf_counter()
                cpu_start_time = time.process_time()

                bot_move_val = bot.get_move()

                cpu_end_time = time.process_time()
                wall_end_time = time.perf_counter()

                wall_time_taken = wall_end_time - wall_start_time
                cpu_time_taken = cpu_end_time - cpu_start_time

                total_wall_time_sec += wall_time_taken
                total_cpu_time_sec += cpu_time_taken
                num_bot_calls += 1

                # ... (rest of your interactive mode print statements and logic) ...
                print(f"Bot move Wall-clock time: {wall_time_taken:.6f} seconds")
                print(f"Bot move CPU time: {cpu_time_taken:.6f} seconds")
                if num_bot_calls > 0:
                    print(f"Average Wall-clock time: {total_wall_time_sec / num_bot_calls:.6f} seconds")
                    print(f"Average CPU time: {total_cpu_time_sec / num_bot_calls:.6f} seconds")

                print(f"You played: {rev_move_map.get(user_move, 'unknown')}")
                print(f"Bot played: {rev_move_map.get(bot_move_val, 'unknown')}")

                result = (user_move - bot_move_val + 3) % 3
                if result == 0:
                    print("It's a Tie!")
                elif result == 1:
                    print("You Win!")
                    user_score += 1
                else: 
                    print("Bot Wins!")
                    bot_score += 1
                
                if hasattr(bot, 'update_history') and callable(getattr(bot, 'update_history')):
                    bot.update_history(bot_move_val, user_move)
                else:
                    pass

        except KeyboardInterrupt:
            print("\nExiting game (Ctrl+C detected).")
        finally:
            if num_bot_calls > 0:
                print("\n--- Final Performance Summary (Python) ---")
                print(f"Total rounds played: {num_bot_calls}")
                print(f"Average bot.get_move() Wall-clock time: {total_wall_time_sec / num_bot_calls:.6f} seconds")
                print(f"Average bot.get_move() CPU time: {total_cpu_time_sec / num_bot_calls:.6f} seconds")
                
                print("\n--- Overall Game Results ---")
                print(f"Total rounds played: {num_bot_calls}")
                print(f"Rounds won by You: {user_score}")
                print(f"Rounds won by Bot: {bot_score}")
                if user_score > bot_score:
                    print("You won the game!")
                elif bot_score > user_score:
                    print("Bot won the game!")
                else:
                    print("The game is a tie!")
            else:
                print("\nNo rounds were played.")
    


# ------------------------------------------------------------------------------
# Example usage in a command-line game:
#
# This code demonstrates how you might play against the IocaineBot.
# Run this module and enter your move as "r" for rock, "p" for paper, or "s" for scissors.
# if __name__ == "__main__":
#     bot = IocaineBot(trials=50)
#     print("Welcome to Rock-Paper-Scissors using IocaineBot!")
#     print("Enter your move: r (rock), p (paper), s (scissors). Ctrl+C to quit.")
#     move_map = {'r': 0, 'p': 1, 's': 2}
#     rev_move_map = {0: 'rock', 1: 'paper', 2: 'scissors'}

#     user_score = 0  # Initialize user's score
#     bot_score = 0   # Initialize bot's score

#     total_wall_time_sec = 0.0
#     total_cpu_time_sec = 0.0
#     num_bot_calls = 0

#     # Call bot's initialization if it has one
#     if hasattr(bot, '_iocaine_init') and callable(getattr(bot, '_iocaine_init')):
#         bot._iocaine_init()
#     elif hasattr(bot, 'iocaine_init') and callable(getattr(bot, 'iocaine_init')):
#         bot.iocaine_init()

#     try:
#         while True:
#             # Display current round
#             print(f"\n--- Round {num_bot_calls + 1} ---")
#             user_input = input("Your move (r/p/s): ").strip().lower()

#             # if user_input == 'q':
#             #     print("Quitting game.")
#             #     break

#             if user_input not in move_map:
#                 print("Invalid move. Please enter r, p, or s")
#                 continue

#             user_move = move_map[user_input]

#             # --- Measure bot.get_move() ---
#             wall_start_time = time.perf_counter()
#             cpu_start_time = time.process_time() # Start CPU timer

#             bot_move_val = bot.get_move()

#             cpu_end_time = time.process_time() # End CPU timer
#             wall_end_time = time.perf_counter()
#             # --- End Measurement ---

#             wall_time_taken = wall_end_time - wall_start_time
#             cpu_time_taken = cpu_end_time - cpu_start_time # Calculate CPU time taken

#             total_wall_time_sec += wall_time_taken
#             total_cpu_time_sec += cpu_time_taken # Accumulate CPU time
#             num_bot_calls += 1

#             print(f"Bot move Wall-clock time: {wall_time_taken:.6f} seconds")
#             print(f"Bot move CPU time: {cpu_time_taken:.6f} seconds") # Print current CPU time
#             if num_bot_calls > 0:
#                 print(f"Average Wall-clock time: {total_wall_time_sec / num_bot_calls:.6f} seconds")
#                 print(f"Average CPU time: {total_cpu_time_sec / num_bot_calls:.6f} seconds") # Print average CPU time

#             print(f"You played: {rev_move_map.get(user_move, 'unknown')}")
#             print(f"Bot played: {rev_move_map.get(bot_move_val, 'unknown')}")

#             # Determine winner
#             result = (user_move - bot_move_val + 3) % 3
#             if result == 0:
#                 print("It's a Tie!")
#             elif result == 1:
#                 print("You Win!")
#             else: # result == 2
#                 print("Bot Wins!")

#             # Update history for the bot
#             if hasattr(bot, 'update_history') and callable(getattr(bot, 'update_history')):
#                 bot.update_history(bot_move_val, user_move) # Corrected order: bot's move, then opponent's (user's) move
#             else:
#                 pass

#     except KeyboardInterrupt:
#         print("\nExiting game (Ctrl+C detected).")
#     finally:
#         if num_bot_calls > 0:
#             print("\n--- Final Performance Summary (Cython) ---")
#             print(f"Total rounds played: {num_bot_calls}")
#             print(f"Average bot.get_move() Wall-clock time: {total_wall_time_sec / num_bot_calls:.6f} seconds")
#             print(f"Average bot.get_move() CPU time: {total_cpu_time_sec / num_bot_calls:.6f} seconds") # Add CPU time to summary

#             # Display final scores and overall winner
#             print("\n--- Overall Game Results ---")
#             print(f"Total rounds played: {num_bot_calls}") # Add total rounds here
#             print(f"Rounds won by You: {user_score}")
#             print(f"Rounds won by Bot: {bot_score}")
#             if user_score > bot_score:
#                 print("You won the game!")
#             elif bot_score > user_score:
#                 print("Bot won the game!")
#             else:
#                 print("The game is a tie!")
#         else:
#             print("\nNo rounds were played.")
#filepath: iocaine_cython_parts.pyx
#cimport cython # Not strictly needed for this example but good to know

# Potentially faster access from Cython
cdef list will_beat_cy = [1, 2, 0]
cdef list will_lose_to_cy = [2, 0, 1]

cdef class StatsCython:
    cdef public int trials
    cdef public int age
    cdef public list sum # Python list of lists of ints

    def __init__(self, int trials_param):
        self.trials = trials_param
        self.age = 0
        self.sum = [[0, 0, 0] for _ in range(self.trials + 1)]
    
    # reset_stats: resets the age to 0 and clears the first row.
    def reset(self):
        self.age = 0
        self.sum[0] = [0, 0, 0]
    
    # add_stats: update the current row by adding delta to the given move index.
    def add(self, int move, int delta):
        self.sum[self.age][move] += delta
    
    # next_stats: increment the age (up to trials) and copy over the previous row.
    def next(self):
        if self.age < self.trials:
            self.age += 1
            self.sum[self.age] = self.sum[self.age - 1].copy()
    
    # max_stats: given a window "age", compute the difference in statistics over that window.
    # It returns the index (move) with the highest difference (score) and a flag indicating validity.
    cpdef max_stats(self, int age_window): # Renamed 'age' param to avoid clash with self.age
        cdef int which = -1
        cdef int score = -10**9  # Or a more specific int minimum
        cdef int i
        cdef int diff

        for i in range(3):
            if age_window > self.age:
                diff = self.sum[self.age][i]
            else:
                diff = self.sum[self.age][i] - self.sum[self.age - age_window][i]
            
            if diff > score:
                score = diff
                which = i
        return which, score, (which != -1)

cdef class PredictCython:
    cdef public StatsCython st  # Declare type of st
    cdef public int last        # Declare type of last

    def __init__(self, int trials):
        self.st = StatsCython(trials)
        self.last = -1  # -1 indicates no previous prediction.
    
    def reset(self):
        self.st.reset()
        self.last = -1

cpdef do_predict(PredictCython pred, int last, int guess):
    cdef int diff
    if last != -1:
        diff = (3 + last - pred.last) % 3
        # Use the Cython-defined lists for potentially faster access
        pred.st.add(will_beat_cy[diff], 1)    # Accessing StatsCython.add
        pred.st.add(will_lose_to_cy[diff], -1) # Accessing StatsCython.add
        pred.st.next()                        # Accessing StatsCython.next
    pred.last = guess # pred.last access will be fast

cpdef match_single(int i, list history):
    cdef int num = len(history)
    # high_index points to the last move in the history.
    cdef int high_index = num - 1
    # low_index starts at candidate position i.
    cdef int low_index = i
    # Compare moves while we can go backwards and the moves match.
    while low_index > 0 and history[low_index] == history[high_index]:
        low_index -= 1
        high_index -= 1
    # The number of matching moves is the distance moved from the end.
    return (num - 1) - high_index

cpdef match_both(int i, list my_history, list opp_history):
    cdef int num = len(my_history)  # Both histories have the same length.
    cdef int j = 0
    # Compare backwards from the end: compare the j-th last move with the move at candidate i.
    while j < i and opp_history[num - 1 - j] == opp_history[i - 1 - j] and \
          my_history[num - 1 - j] == my_history[i - 1 - j]:
        j += 1
    return j

cpdef do_history(int age, list my_history, list opp_history):
    cdef int num = len(my_history)
    # Initialize best indices and best match lengths for each of the three cases.
    cdef list best = [0, 0, 0]         # 0: my history, 1: opponent history, 2: both histories
    cdef list best_length = [0, 0, 0]
    cdef int i, j
    
    # Look for best match in your own history.
    for i in range(num - 1, max(num - age, best_length[0]), -1):
        j = match_single(i, my_history)
        if j > best_length[0]:
            best_length[0] = j
            best[0] = i
            if j > num // 2:
                break

    # Look for best match in opponent's history.
    for i in range(num - 1, max(num - age, best_length[1]), -1):
        j = match_single(i, opp_history)
        if j > best_length[1]:
            best_length[1] = j
            best[1] = i
            if j > num // 2:
                break

    # Look for best match in both histories simultaneously.
    for i in range(num - 1, max(num - age, best_length[2]), -1):
        j = match_both(i, my_history, opp_history)
        if j > best_length[2]:
            best_length[2] = j
            best[2] = i
            if j > num // 2:
                break

    return best

cpdef scan_predict(PredictCython pred, int age):
    # Type declarations for local variables
    cdef int predicted_opponent_move_from_stats # This is 'which' from max_stats
    cdef int current_score
    cdef bint is_valid
    cdef int move_to_return # This is the 'move' calculated as (pred.last + which) % 3

    # Call the max_stats method from the StatsCython object within pred
    predicted_opponent_move_from_stats, current_score, is_valid = pred.st.max_stats(age)

    if not is_valid:
        # Original Python returned (None, score).
        # Return a tuple (None, current_score). Cython can return Python's None.
        return None, current_score

    # If valid, calculate the move to return based on the original Python logic.
    # pred.last is the previous prediction this predictor (pred) made for the opponent's move.
    # predicted_opponent_move_from_stats is the current prediction from this predictor's stats
    # for what the opponent might do.
    move_to_return = (pred.last + predicted_opponent_move_from_stats) % 3
    
    return move_to_return, current_score # Return a tuple (move, score)



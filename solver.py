def load_board(board):
    '''
    Input: list[list[str]] or list[str]
    Output: list[list[set]], list[tuple(int))]
    This function loads in and does pre-processing for a 9 x 9 sudoku board.
    
    '''
    if type(board) != list:
        raise TypeError("Unexpected input! Please input a list of strings or list of lists")
    if len(board) != 9:
        raise Exception("Expected a 9x9 Sudoku board!")
    matrix = [[set() for i in range(9)] for j in range(9)]
    cancellation_queue = []
    for rownum in range(9):
        if len(board[rownum]) != 9:
            raise Exception("Expected a 9x9 Sudoku board, at least one row has a length of %s" %len(board[rownum]))
        for colnum in range(9):
            if board[rownum][colnum] not in '.123456789':
                raise Exception("Input not in .123456789")
            if board[rownum][colnum] == '.':
                matrix[rownum][colnum] = set([i for i in range(1, 10)])
            else:
                matrix[rownum][colnum] = set([int(board[rownum][colnum])])
                cancellation_queue.append((rownum, colnum))
    return matrix, cancellation_queue

def change_line(matrix, line, pos, number):
    line.remove(pos)
    update = set()
    for position in line:
        if number in matrix[position[0]][position[1]]:
            matrix[position[0]][position[1]].remove(number)
            if len(matrix[position[0]][position[1]]) == 1:
                update.add(position)
    return update 

def update_horizontal(matrix, pos):
    line = [(pos[0], i) for i in range(9)]
    number = next(iter(matrix[pos[0]][pos[1]]))
    updates = change_line(matrix, line, pos, number)
    return updates 

def update_vertical(matrix, pos):
    line = [(i, pos[1]) for i in range(9)]
    number = next(iter(matrix[pos[0]][pos[1]]))
    updates = change_line(matrix, line, pos, number)
    return updates
    
def update_square(matrix, pos):
    start_row = pos[0] // 3 * 3 
    start_col = pos[1] // 3 * 3
    square = []
    for i in range(3):
        for j in range(3):
            square.append((start_row + i, start_col + j))
    number = next(iter(matrix[pos[0]][pos[1]]))
    updates = change_line(matrix, square, pos, number)
    return updates

def update_matrix(matrix, pos):
    updates = set()
    for fun in [update_horizontal, update_vertical, update_square]:
        updates = updates.union(fun(matrix, pos))
    return updates


def canceller(matrix, cancellation_queue):
    while len(cancellation_queue) != 0:
        pos = cancellation_queue.pop()
        updates = update_matrix(matrix, pos)
        for update in updates:
            cancellation_queue.append(update)
    return matrix, cancellation_queue
    
def count_line(matrix, line):
    update = set()
    for number in range(1, 10):
        count = 0 
        for position in line: 
            if number in matrix[position[0]][position[1]]:
                if len(matrix[position[0]][position[1]]) == 1:
                    break
                count += 1
                if count > 1:
                    break 
                saved = position 
        else:
            matrix[saved[0]][saved[1]] = set([number])
            update.add(saved)
    return update
    
def count_horizontal(matrix):
    updates = set()
    for i in range(9):
        line = [(i, j) for j in range(9)]
        updates = updates.union(count_line(matrix, line))
    return updates
    
def count_vertical(matrix):
    updates = set()
    for j in range(9):
        line = [(i, j) for i in range(9)]
        updates = updates.union(count_line(matrix, line))
    return updates

def count_squares(matrix):
    updates = set()
    starts = [(x,y) for x in [0, 3, 6] for y in [0, 3, 6]]
    for start in starts:
        line = []
        for i in range(3):
            for j in range(3):
                line.append((start[0] + i, start[1] + j))
        updates = updates.union(count_line(matrix, line))
    return updates
    
def full_counter(matrix):
    updates = set()
    for counter in [count_squares, count_vertical, count_horizontal]:
        updates = updates.union(counter(matrix))
    return matrix, updates

def output_board(matrix):
    board = [['.' for i in range(9)] for j in range(9)]
    for i in range(9):
        for j in range(9):
            if len(matrix[i][j]) == 1:
                number = next(iter(matrix[i][j]))
                board[i][j] = str(number)
    return board    

def sudoku_solver(board):
    matrix, cancellation_queue = load_board(board)
    while len(cancellation_queue) != 0:
        matrix, cancellation_queue = canceller(matrix, cancellation_queue)
        matrix, updates = full_counter(matrix)
        cancellation_queue = list(updates)
    board = output_board(matrix)
    return board


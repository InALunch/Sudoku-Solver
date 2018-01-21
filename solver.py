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
    '''The simplest Sudoku strategy. If a position in a row row, column or 3x3 square already has a number n, then we know that no other position in that row, column or square can be n. So we remove n from the set of possiblities for every other position in that row, column, or square.'''
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
    '''If a position is definitely a certain number, we update possible options along its row, column and square to reflect this.'''
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
    return matrix
  
def generate_lines(horizontal = True):
    lines = []
    for i in range(9):
        if horizontal:
             line = [(i, j) for j in range(9)]
        else:
            line = [(j, i) for j in range(9)]
        lines.append(line)
    return lines 

def generate_squares():
    starts = [(x,y) for x in [0, 3, 6] for y in [0, 3, 6]]
    squares = []
    for start in starts:
        square = []
        for i in range(3):
            for j in range(3):
                square.append((start[0] + i, start[1] + j))
        squares.append(square)
    return squares
    
def generate_all():
    '''
    generates a list of all the "blocks", that is, positions that are intricately tied to each other because they're the same row, column or 3x3 block where no two positions can be the same number. 
    '''
    blocks = []
    for line in generate_lines(True):
        blocks.append(line)
    for line in generate_lines(False):
        blocks.append(line)
    for line in generate_squares():
        blocks.append(line)
    return blocks

def count_line(matrix, line):
    '''
    For every line, if there is only one position along the line where a possiblity remains that it is n, then  
    that position MUST necessarily be n. We update the matrix accordingly, and then returns the changed positions.
    '''
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

def full_counter(blocks, matrix):
    '''Invokes count_line on all blocks in the first argument.'''
    updates = set()
    for block in blocks:
        for new_pos in count_line(matrix, block):
            updates.add(new_pos)
    return matrix, updates

def extracttuple(n):
    '''
    Overly clever code tbh, but I almost never get to make a function that generates functions
    '''
    def findtuples(lst, matrix):
        new_lst = []
        for elem in lst:
            if len(matrix[elem[0]][elem[1]]) == n:
                new_lst.append(elem)
        return new_lst
    return findtuples
    
def find_twins(line, matrix):
    '''
    Given a list of positions in the same 'block' (line/square) where the matrix stores sets of length 2, identify "open twins", ie points where the stored set at those positions are identical.
     Basically just a variant algorithm of the optimal solution to TwoSum, see https://leetcode.com/problems/two-sum/description/ 
    '''
    unmatched = dict()
    twins = []
    for elem in line:
        value = tuple(matrix[elem[0]][elem[1]])
        if value in unmatched:
            twins.append([elem, unmatched[value]])
        else:
            unmatched[value] = elem
    return twins 

def find_triplets(tripleslist, matrix):
    '''Identifies and returns the first set of triplets in a block, akin to "find_twins".
    We stop searching after the first set of triplets is found, since it seems exceedingly unlikely that the same block will have two triplets'''
    unmatched = dict()
    triplets = []
    for elem in tripleslist:
        value = tuple(matrix[elem[0]][elem[1]])
        if value in unmatched:
            if len(unmatched[value]) == 2:
                triplets.append(unmatched[value][0])
                triplets.append(unmatched[value][1])
                triplets.append(elem)
                return triplets
            else:
                unmatched[value].append(elem)
        else:
            unmatched[value] = [elem]
    return []
    

def tuple_ellimination(block, matrix, tups):
    values = matrix[tups[0][0]][tups[0][1]]
    updates = set()
    for tup in block:
        if tup not in tups and len(tup) > 1:
            for value in values:
                if value in matrix[tup[0]][tup[1]]:
                    matrix[tup[0]][tup[1]].discard(value)
                    if len(matrix[tup[0]][tup[1]]) == 1:
                        updates.add(tup)
    return updates 
        
def open_twins(blocks, matrix):
    '''
    1. For each block, find 'open twins', that is, positions in the same block where the underlying possibilities are identical sets of length two.
    eg, (0,5) and (0,7) are in the same row. Suppose that matrix[0][5] and matrix[0][7] both point to set(2,6), then (0,5) and (0,7) are open twins.
    2. If a,b are stored in the open twins, delete a,b from the matrix in every other element in the same block.
    eg, in this case, any element along row 0 except (0,5) and (0,7) can no longer store 2 or 6.
    
    Why does this work? Suppose A,B are two positions in the same block, and each of them can be a or b. Then we know it's either Aa and Bb or Ab and Ba. In either case, neither a nor b can fit into one of the other positions along the same block.
    '''
    find_doubles = extracttuple(2)
    updates = set()
    for block in blocks:
        doubles = find_doubles(block, matrix)
        twins = []
        if len(doubles) >= 2:
            twins = find_twins(doubles, matrix)
        if len(twins) > 0:
            for pair in twins:
                ups = tuple_ellimination(block, matrix, pair)
                for u in ups:
                    updates.add(u)
    return updates

def open_triplets(blocks, matrix):
    '''as with open_twins, but for positions with 3 possibilities instead of 2.'''
    find_3tuples = extracttuple(3) #originally find_triples, but looked too much like "find_triplets"
    updates = set()
    for block in blocks:
        triples = find_3tuples(block, matrix)
        if len(triples)>=3:
            triplets = find_triplets(triples, matrix)
            if triplets:
                ups = tuple_ellimination(block, matrix, triplets)
                for u in ups:
                    updates.add(u)
    return updates
            
def output_board(matrix):
    '''returns the updated board in a hopefully easy to read format.'''
    board = [['.' for i in range(9)] for j in range(9)]
    for i in range(9):
        for j in range(9):
            if len(matrix[i][j]) == 1:
                number = next(iter(matrix[i][j]))
                board[i][j] = str(number)
    return '\n'.join('|'.join(row) for row in board)    

def sudoku_solver(board):
    matrix, cancellation_queue = load_board(board)
    blocks = generate_all()
    while len(cancellation_queue) != 0:
        matrix = canceller(matrix, cancellation_queue)
        matrix, updates = full_counter(blocks, matrix)
        updates = updates.union(open_twins(blocks, matrix))
        updates = updates.union(open_triplets(blocks, matrix))
        cancellation_queue = list(updates)
        
    board = output_board(matrix)
    return board
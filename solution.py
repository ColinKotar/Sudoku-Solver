from utils import *

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
unitlist = row_units + column_units + square_units

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention.
    """
    from collections import Counter

    # val = {"B1": "5", "I5": "35678", "H5": "35678", "C1": "4678", "H6": "23568", "C5": "2", "G2": "123568", "H1": "2346789",
    #     "E4": "234678", "G5": "35678", "E2": "123568", "C4": "9", "C7": "13456", "D6": "23568", "A4": "5", "H2": "23568",
    #     "D5": "1356789", "I3": "25678", "C6": "368", "D3": "25689", "A1": "2468", "E6": "23568", "B2": "2", "A5": "3468",
    #     "E5": "13456789", "F2": "7", "I7": "9", "B5": "46", "F4": "23468", "E3": "25689", "H7": "234568", "H8": "234567",
    #     "F6": "23568", "A6": "7", "D9": "1235678", "F7": "1234568", "I8": "123567", "I6": "4", "A8": "2346", "F5": "1345689",
    #     "B7": "7", "G3": "245678", "I1": "123678", "G6": "9", "H4": "1", "I4": "23678", "F8": "1234569", "B8": "8",
    #     "A3": "1", "E1": "123689", "C3": "4678", "G9": "12345678", "I9": "1235678", "B9": "9", "F9": "1234568", "E8": "12345679",
    #     "F1": "123689", "D2": "4", "D4": "23678", "B6": "1", "I2": "123568", "B4": "46", "G7": "1234568", "H3": "2456789",
    #     "D8": "1235679", "E7": "1234568", "A2": "9", "D7": "123568", "C9": "13456", "B3": "3", "G8": "1234567", "C8": "13456",
    #     "D1": "123689", "A7": "2346", "F3": "25689", "H9": "2345678", "E9": "12345678", "A9": "2346", "G1": "1234678", "C2": "68", "G4": "23678"}

    for unit in unitlist:
        # find the naked twins in each unit
        unit_keys_values = {k:values[k] for k in unit}
        count = Counter(unit_keys_values.values())
        possible_twins = []
        # find twin value
        for pt, c in count.items():
            if c == 2 and len(pt) == 2:
                possible_twins.append(pt)
        # if there is a twin in current unit
        if possible_twins:
            # find locations of the twins
            twin_key = {}
            for key_box, value in unit_keys_values.items():
                for pt in possible_twins:
                    if value == pt and value not in twin_key.values():
                        twin_key[key_box] = pt
            # using locations, remove twin values from it's peers
            for k, v in twin_key.items():
                for p in peers[k]:
                    if v != values[p]:
                        for n in v:
                            values[p] = values[p].replace(n, '')

    return values




def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for k in values:
        if len(values[k]) == 1:
            num = values[k]
            for p in peers[k]:
                values[p] = values[p].replace(num, '')
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False
    """
    # Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if not values:
        return False

    if all(len(values[n]) == 1 for n in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    _, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

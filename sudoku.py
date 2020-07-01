import math
import random

class Cell(object):
    def __init__(self, val, row, col, row_w=0, col_w=0, box_w=0, wt=0):
        self.val = val
        self.row = row
        self.col = col
        self.row_w = row_w
        self.col_w = col_w
        self.box_w = box_w
        self.wt = wt
        self.possible_moves = []
        self.label = None
        self.moves_label = None


class Sudoku(object):
    EMPTY_CELL_VALUE = -1

    def __init__(self, gui=None, **kwargs):

        print(kwargs)
        matrix = kwargs.get('matrix', [])
        size = kwargs.get('size', 9)

        is_empty = False

        if not matrix:
            is_empty = True

        self.const = int(math.sqrt(size))
        self.moves = []
        self.required_moves = 0

        self.matrix = []
        self.same_column_cells = dict()
        self.same_box_cells = dict()

        self.gui = gui
        self.total_moves = 0

        for row in range(0, (self.const ** 2)):
            self.matrix.append([])
            for col in range(0, (self.const ** 2)):
                if is_empty:
                    val = -1
                else:
                    val = matrix[row][col]

                cell = Cell(val, row, col)

                self.matrix[row].append(cell)

    def initialize(self):
        for row, row_cells in enumerate(self.matrix):
            for column, cell in enumerate(row_cells):
                if cell.val == -1:
                    self.required_moves += 1

                if column not in self.same_column_cells:
                    self.same_column_cells[column] = []
                self.same_column_cells[column].append(cell)

                box_no = self.get_box_no(row, column)

                if box_no not in self.same_box_cells:
                    self.same_box_cells[box_no] = []

                self.same_box_cells[box_no].append(cell)

    def get_box_no(self, row, col):
        row_index = row - row % self.const
        col_index = col - col % self.const

        box_no = row_index + int(col_index / self.const)

        return box_no

    def get_cells_in_same_box(self, cell):

        box_no = self.get_box_no(cell.row, cell.col)
        cells = self.same_box_cells[box_no]

        return cells

    def get_cells_in_same_column(self, column):
        return self.same_column_cells[column]

    def print_matrix(self):
        for row_elements in self.matrix:
            for cell in row_elements:
                print("{}:[{},{},{},{}],  ".format(cell.val, cell.row_w, cell.col_w, cell.box_w, cell.wt), end='')
            print()

    def validate_and_init(self):
        column_cells = dict()
        box_cells = dict()
        for row, row_cells_objs in enumerate(self.matrix):
            row_cells = dict()
            for column, cell in enumerate(row_cells_objs):
                if cell.val == -1:
                    self.required_moves += 1

                # duplicate check on row
                if cell.val != Sudoku.EMPTY_CELL_VALUE:
                    if cell.col not in row_cells:
                        row_cells[cell.col] = set()

                    if cell.val in row_cells[cell.col]:
                        return False

                    row_cells[cell.col].add(cell.val)

                # duplicate check on column
                if cell.val != Sudoku.EMPTY_CELL_VALUE:
                    if cell.col not in column_cells:
                        column_cells[cell.col] = set()
                    if cell.val in column_cells[cell.col]:
                        return False

                    column_cells[cell.col].add(cell.val)

                box_no = self.get_box_no(row, column)

                # duplicate check on box
                if cell.val != Sudoku.EMPTY_CELL_VALUE:
                    if box_no not in box_cells:
                        box_cells[box_no] = set()

                    if cell.val in box_cells[box_no]:
                        return False

                    box_cells[box_no].add(cell.val)

                # Initialize
                if column not in self.same_column_cells:
                    self.same_column_cells[column] = []
                self.same_column_cells[column].append(cell)

                box_no = self.get_box_no(row, column)

                if box_no not in self.same_box_cells:
                    self.same_box_cells[box_no] = []

                self.same_box_cells[box_no].append(cell)

        return True

    @staticmethod
    def get_random_sudoku():
        matrix = [[-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, 1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, -1, -1, -1, -1, -1, 1, -1, -1]]

    considered_box = []
    considered_row = []

    pass

    @staticmethod
    def get_sample_sudoku():
        sample_matrixs = [[[-1, -1, -1, 6, -1, -1, 4, -1, -1],
                           [7, -1, -1, -1, -1, 3, 6, -1, -1],
                           [-1, -1, -1, -1, 9, 1, -1, 8, -1],
                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                           [-1, 5, -1, 1, 8, -1, -1, -1, 3],
                           [-1, -1, -1, 3, -1, 6, -1, 4, 5],
                           [-1, 4, -1, 2, -1, -1, -1, 6, -1],
                           [9, -1, 3, -1, -1, -1, -1, -1, -1],
                           [-1, 2, -1, -1, -1, -1, 1, -1, -1]],
                          [[-1, -1, -1, 6, -1, -1, 4, -1, -1],
                           [-1, -1, -1, -1, -1, 3, 6, -1, -1],
                           [-1, -1, -1, -1, 9, 1, -1, 8, -1],
                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                           [-1, 5, -1, 1, 8, -1, -1, -1, 3],
                           [-1, -1, -1, 3, -1, 6, -1, 4, 5],
                           [-1, 4, -1, 2, -1, -1, -1, 6, -1],
                           [9, -1, 3, -1, -1, -1, -1, -1, -1],
                           [-1, 2, -1, -1, -1, -1, 1, -1, -1]],
                          [[8, -1, -1, -1, 1, -1, -1, 2, -1],
                           [2, -1, -1, -1, -1, -1, -1, -1, 1],
                           [-1, 1, -1, -1, 9, -1, -1, 5, -1],
                           [5, -1, -1, -1, -1, 4, 7, -1, -1],
                           [-1, 2, -1, -1, -1, -1, 5, 4, -1],
                           [7, -1, -1, 5, -1, -1, -1, 6, -1],
                           [-1, 5, 2, -1, -1, -1, -1, -1, 4],
                           [-1, -1, -1, -1, 4, -1, -1, -1, -1],
                           [-1, -1, -1, -1, 6, 2, 8, -1, 5]]

                          ]
        return sample_matrixs[random.randint(0, 99) % 3]

#              [[8, 3, 5, 4, 1, 6, 9, 2, 7],
#              [2, 9, 6, 8, 5, 7, 4, 3, 1],
#              [4, 1, 7, 2, 9, 3, 6, 5, 8],
#              [5, 6, 9, 1, 3, 4, 7, 8, 2],
#              [1, 2, 3, 6, 7, 8, 5, 4, 9],
#              [7, 4, 8, 5, 2, 9, 1, 6, 3],
#              [6, 5, 2, 7, 8, 1, 3, 9, 4],
#              [9, 8, 1, 3, 4, 5, 2, 7, 6],
#              [3, 7, 4, 9, 6, 2, 8, 1, 5]]

# [[-1, -1, -1, 6, -1, -1, 4, -1, -1],
#  [7, -1, -1, -1, -1, 3, 6, -1, -1],
#  [-1, -1, -1, -1, 9, 1, -1, 8, -1],
#  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#  [-1, 5, -1, 1, 8, -1, -1, -1, 3],
#  [-1, -1, -1, 3, -1, 6, -1, 4, 5],
#  [-1, 4, -1, 2, -1, -1, -1, 6, -1],
#  [9, -1, 3, -1, -1, -1, -1, -1, -1],
#  [-1, 2, -1, -1, -1, -1, 1, -1, -1]]

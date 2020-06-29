import copy

from SudokuSolver.sudoku import Sudoku

EMPTY_CELL_VALUE = -1


class SudokuSolver(Sudoku):
    def compute_weights(self, cell=None, revert=False):
        if cell:
            original_cell = cell

            same_row_cells = self.matrix[cell.row]
            same_col_cells = self.get_cells_in_same_column(cell.col)
            same_box_cells = self.get_cells_in_same_box(cell)

            row_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, same_row_cells)))
            col_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, same_col_cells)))
            box_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, same_box_cells)))

            if revert:
                original_cell.row_w = row_wt
                original_cell.col_w = col_wt
                original_cell.box_w = box_wt
                original_cell.wt = row_wt + col_wt + box_wt
            else:
                original_cell.row_w += 1
                original_cell.col_w += 1
                original_cell.box_w += 1
                original_cell.wt = 0

            for cell in same_row_cells:
                if cell.val != EMPTY_CELL_VALUE:
                    continue
                cell.wt = cell.wt - cell.row_w + row_wt
                cell.row_w = row_wt

            for cell in same_col_cells:
                if cell.val != EMPTY_CELL_VALUE:
                    continue
                cell.wt = cell.wt - cell.col_w + col_wt
                cell.col_w = col_wt

            for cell in same_box_cells:
                if cell.val != EMPTY_CELL_VALUE:
                    continue
                cell.wt = cell.wt - cell.box_w + box_wt
                cell.box_w = box_wt

        else:
            box_considered = []

            for row_index, matrix_row in enumerate(self.matrix):
                row_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, matrix_row)))

                for cell in matrix_row:
                    if cell.val != EMPTY_CELL_VALUE:
                        continue
                    cell.row_w = row_wt
                    cell.wt += cell.row_w

                    same_box_cells = self.get_cells_in_same_box(cell)
                    box_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, same_box_cells)))

                    same_box_cells = filter(lambda x: x.val == -1, same_box_cells)

                    for cell in same_box_cells:
                        if cell in box_considered:
                            continue
                        box_considered.append(cell)

                        cell.box_w = box_wt
                        cell.wt += box_wt

            for col in range(0, len(self.matrix)):
                same_col_cells = self.get_cells_in_same_column(col)
                col_wt = len(list(filter(lambda x: x.val != EMPTY_CELL_VALUE, same_col_cells)))

                for cell in same_col_cells:
                    if cell.val != EMPTY_CELL_VALUE:
                        continue
                    cell.col_w = col_wt
                    cell.wt += cell.col_w

    def get_max_weighted_cell(self):
        max_wt = -1
        max_wt_cell = None

        for matrix_row in self.matrix:
            for cell in matrix_row:
                if cell.wt > max_wt:
                    max_wt = cell.wt
                    max_wt_cell = cell

        return max_wt_cell

    def find_possible_values(self, cell):
        same_box_cells = self.get_cells_in_same_box(cell)
        same_col_cells = self.get_cells_in_same_column(cell.col)
        same_row_cells = self.matrix[cell.row]

        total_possible_values = [i + 1 for i in range(0, self.const ** 2)]

        valid_values = set(total_possible_values) - set(map(lambda x: x.val, same_box_cells)) - set(
            map(lambda x: x.val, same_col_cells)) - set(map(lambda x: x.val, same_row_cells))

        return list(valid_values) if valid_values else []

    def fill_cell(self, cell, value):
        cell.val = value
        self.total_moves += 1
        print("MOVES: {}".format(self.total_moves))

        if self.gui:
            self.gui.update_cell_at_runtime(cell.label, cell.val, cell.moves_label, cell.possible_moves)

    def is_solved(self):
        return len(self.moves) == self.required_moves

    def verify(self):
        solution = [[8, 3, 5, 4, 1, 6, 9, 2, 7],
                    [2, 9, 6, 8, 5, 7, 4, 3, 1],
                    [4, 1, 7, 2, 9, 3, 6, 5, 8],
                    [5, 6, 9, 1, 3, 4, 7, 8, 2],
                    [1, 2, 3, 6, 7, 8, 5, 4, 9],
                    [7, 4, 8, 5, 2, 9, 1, 6, 3],
                    [6, 5, 2, 7, 8, 1, 3, 9, 4],
                    [9, 8, 1, 3, 4, 5, 2, 7, 6],
                    [3, 7, 4, 9, 6, 2, 8, 1, 5]]

        for row, row_elements in enumerate(self.matrix):
            for column, cell in enumerate(row_elements):
                if cell.val != solution[row][column]:
                    return False

        return True

    def solve_recursively(self):

        if self.is_solved():
            print("SODOKU SOLVED")
            return True

        cell = self.get_max_weighted_cell()

        possible_values = self.find_possible_values(cell)
        print("New max weighted cell [{},{}] with possible moves {}".format(cell.row, cell.col, possible_values))

        if not possible_values:
            print("Wrong move picked: [{},{}]> {}".format(cell.row, cell.col, cell.val))
            return False

        cell.possible_moves = copy.copy(possible_values)
        self.moves.append(cell)

        for move in possible_values:
            self.fill_cell(cell, move)

            self.compute_weights(cell)

            print("Chose move [{},{}]->{} ".format(cell.row, cell.col, move))
            print()
            status = self.solve_recursively()

            print("Status of move [{},{}]->{} = {}".format(cell.row, cell.col, move, status))

            if status:
                return True

            cell.possible_moves.remove(move)

        else:
            print("All possible moves on [{},{}] failed. Need to backtrack now".format(cell.row, cell.col))
            print()

            cell.possible_moves = []

            self.fill_cell(cell, -1)
            self.compute_weights(cell, revert=True)
            self.moves.pop()

            return False

    def solve(self):
        self.total_moves = 0
        self.initialize()
        self.compute_weights()

        status = self.solve_recursively()

        print("Status of solving sudoku: {}".format(status))

        return status


if __name__ == '__main__':
    pass
    #
    # sudoku = SudokuSolver(**{'matrix': Sudoku.get_sample_sudoku()})
    # sudoku.solve()

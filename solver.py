import tkinter as tk

UPDATE_RATE = 100

import math
import time

EMPTY_CELL_VALUE = -1


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
        self.tried_moves = []
        self.label = None


class Sudoku(object):
    def __init__(self, matrix, gui):

        self.const = int(math.sqrt(len(matrix)))
        self.moves = []
        self.required_moves = 0

        self.matrix = []
        self.same_column_cells = dict()
        self.same_box_cells = dict()

        self.gui = gui

        for row in range(0, len(matrix)):
            self.matrix.append([])
            for col in range(0, len(matrix)):
                val = matrix[row][col]

                cell = Cell(val, row, col)

                self.matrix[row].append(cell)

                if matrix[row][col] == -1:
                    self.required_moves += 1

                if col not in self.same_column_cells:
                    self.same_column_cells[col] = []
                self.same_column_cells[col].append(cell)

                box_no = self.get_box_no(row, col)

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
        cell.label['text'] = value
        cell.moves_label['text'] = "{}".format(cell.possible_moves)
        if value != -1:
            cell.label['bg'] = 'green'
        else:
            cell.label['bg'] = 'red'
        # time.sleep(0.05)
        self.gui.update_idletasks()

    def is_solved(self):
        return len(self.moves) == self.required_moves

    def print_matrix(self):
        for row_elements in self.matrix:
            for cell in row_elements:
                print("{}:[{},{},{},{}],  ".format(cell.val, cell.row_w, cell.col_w, cell.box_w, cell.wt), end='')
            print()

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

        cell.possible_moves = possible_values
        self.moves.append(cell)

        for move in possible_values:

            cell.tried_moves.append(move)
            self.fill_cell(cell, move)

            self.compute_weights(cell)

            print("Chose move [{},{}]->{} ".format(cell.row, cell.col, move))
            print()
            status = self.solve_recursively()

            print("Status of move [{},{}]->{} = {}".format(cell.row, cell.col, move, status))

            if status:
                return True

            cell.tried_moves.pop()

        else:
            print("All possible moves on [{},{}] failed. Need to backtrack now".format(cell.row, cell.col))
            print()

            cell.tried_moves = []
            cell.possible_moves = []

            self.fill_cell(cell, -1)
            self.compute_weights(cell, revert=True)
            self.moves.pop()

            return False

    def solve(self):
        self.compute_weights()

        self.solve_recursively()


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


class Application(tk.Frame):
    def __init__(self, master=None, matrix=[]):
        super().__init__(master)

        self.master = master
        self.sudoku = Sudoku(matrix, self.master)
        self.create_widgets()
        # self.updater()

    def hit(self):
        cell = self.sudoku.matrix[0][0]
        cell.textvariable.set("!@")
        time.sleep(1)
        cell.textvariable.set("1")
        time.sleep(1)
        cell.textvariable.set("3")

    def create_widgets(self):

        container = tk.Frame(self.master, width=200, height=200)
        container.pack(side=tk.BOTTOM, fill="both")

        f2 = tk.Frame(self.master, bg="black", height=100, width=100)
        f2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        bt = tk.Button(container, bg="white", text="SOLVE", command=self.sudoku.solve)
        bt.pack(side=tk.BOTTOM)

        f3 = tk.Frame(f2, bg="white", height=600, width=600)
        f3.pack(side=tk.TOP, fill="both", pady=10, padx=10)

        sudoku_cells = self.sudoku.matrix

        for row, row_cells in enumerate(sudoku_cells):
            for column, cell in enumerate(row_cells):

                # label = tk.Label(f3, height=2, width=4,bg="pink",fg='black', activeforeground="pink",font = "Times 20")
                # label['text'] = cell.val
                #
                # if (cell.val != -1):
                #     label['fg'] = "blue"
                #     label['font'] = 'Times 20 bold'
                #
                # label.grid(row=row, column=column, padx=3, pady=3, ipadx=5,ipady=5)
                #
                # moves_label = tk.Label(f3, height=2, width=4,bg="pink",fg='black', activeforeground="pink",font = "Times 20")
                # moves_label['text'] = "[3]"
                # moves_label.grid(row=row+1, column=column, padx=3, pady=3, ipadx=5,ipady=5)
                #
                # cell.label = label
                # cell.moves_label = moves_label
                # # label['textvariable'] = cell.val
                # # label.pack()

                cell_frame = tk.Frame(f3, bg="white", height=70, width=70)
                cell_frame.grid(row=row, column=column, padx=3, pady=3)

                label = tk.Label(cell_frame, height=3, width=5, bg="pink", fg='black', activeforeground="pink",
                                 font="Times 20")
                label['text'] = cell.val

                if (cell.val != -1):
                    label['fg'] = "blue"
                    label['font'] = 'Times 20 bold'

                label.pack()

                moves_label = tk.Label(cell_frame, height=1, width=5, bg="pink", fg='black', activeforeground="pink",
                                       font="Times 10")
                moves_label.pack()

                cell.label = label
                cell.moves_label = moves_label

        pass

    def updater(self):
        print('updated')
        self.after(UPDATE_RATE, self.updater)


if __name__ == '__main__':
    matrix = [[-1, -1, -1, 6, -1, -1, 4, -1, -1],
              [7, -1, -1, -1, -1, 3, 6, -1, -1],
              [-1, -1, -1, -1, 9, 1, -1, 8, -1],
              [-1, -1, -1, -1, -1, -1, -1, -1, -1],
              [-1, 5, -1, 1, 8, -1, -1, -1, 3],
              [-1, -1, -1, 3, -1, 6, -1, 4, 5],
              [-1, 4, -1, 2, -1, -1, -1, 6, -1],
              [9, -1, 3, -1, -1, -1, -1, -1, -1],
              [-1, 2, -1, -1, -1, -1, 1, -1, -1]]

    root = tk.Tk()
    app = Application(master=root, matrix=matrix)

    app.master.title("Sudoku Solver")
    app.master.geometry("900x900")

    start_time = time.time()

    # for i in range(0, 9):
    #     for j in range(0, 9):
    #         matrix[i][j] = -1

    app.mainloop()

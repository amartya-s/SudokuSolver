import tkinter as tk

UPDATE_RATE = 100

import math
import time
import copy

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
        self.label = None


class Sudoku(object):
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
        self.delay = 0


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

                if val == -1:
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
        self.total_moves += 1
        print("MOVES: {}".format(self.total_moves))
        cell.label.delete("1.0", tk.END)
        if value == -1:
            cell.label.insert('')
            cell.label['bg'] = 'rosybrown1'
            # cell.label['relief'] = 'groove'
        else:
            cell.label.insert(value)
            cell.label['bg'] = 'rosybrown2'
            # cell.label['relief'] = 'groove'

        cell.moves_label['text'] = "{}".format(cell.possible_moves)

        self.gui.update_idletasks()
        time.sleep(self.delay)


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

    def solve(self, delay_in_moves=0):
        self.delay = delay_in_moves
        self.total_moves = 0
        self.compute_weights()

        status = self.solve_recursively()

        print("Status of solving sudoku: {}".format(status))

        return status

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
        matrix = [[-1, -1, -1, 6, -1, -1, 4, -1, -1],
                  [7, -1, -1, -1, -1, 3, 6, -1, -1],
                  [-1, -1, -1, -1, 9, 1, -1, 8, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, 5, -1, 1, 8, -1, -1, -1, 3],
                  [-1, -1, -1, 3, -1, 6, -1, 4, 5],
                  [-1, 4, -1, 2, -1, -1, -1, 6, -1],
                  [9, -1, 3, -1, -1, -1, -1, -1, -1],
                  [-1, 2, -1, -1, -1, -1, 1, -1, -1]]
        matrix = [[-1, -1, -1, 6, -1, -1, 4, -1, -1],
                  [7, -1, -1, -1, -1, 3, 6, -1, -1],
                  [-1, -1, -1, -1, 9, 1, -1, 8, -1],
                  [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                  [-1, 5, -1, 1, 8, -1, -1, -1, 3],
                  [-1, -1, -1, 3, -1, 6, -1, 4, 5],
                  [-1, 4, -1, 2, -1, -1, -1, 6, -1],
                  [9, -1, 3, -1, -1, -1, -1, -1, -1],
                  [-1, 2, -1, -1, -1, -1, 1, -1, -1]]
        # matrix =   [[-1, 1, -1, -1, 8, -1, -1, 9, -1],
        #              [7, -1, -1, 4, -1, -1, 1, -1, -1],
        #              [7, -1, -1, 4, -1, -1, 1, -1, -1],
        #              [4, -1, -1, 3, -1, -1, 5, -1, -1],
        #              [-1, 9, -1, -1, 4, -1, -1, 5, -1],
        #              [5, -1, -1, -1, -1, -1, 7, -1, -1],
        #              [6, -1, -1, 2, -1, -1, 4, -1, -1],
        #              [-1, 2, -1, -1, 3, -1, -1, 1, -1],
        #              [3, -1, -1, 5, -1, -1, 8, -1, -1],
        #              [1, -1, -1, 8, -1, -1, 9, -1, -1]]
        return matrix

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
class CustomText(tk.Text):
    def __init__(self, cell, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self.cell = cell
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def insert(self, text=''):
        self.delete("1.0", tk.END)
        super().insert("1.0", text, "center")

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "replace"):
            self.event_generate("<<TextModified>>")

        if command == 'delete':
            self.event_generate("<<TextDeleted>>")

        return result

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master = master
        self.slider = None
        self.status_label = None

        self.create_widgets()
        self.sudoku_cell_gui_objs = []

    def load_sample_sudoku(self, frame):
        sample_sudoku = Sudoku.get_sample_sudoku()
        self.sudoku = Sudoku(gui=frame, **{'matrix': sample_sudoku, 'size': len(sample_sudoku)})
        self.create_sudoku_layout(frame)

    def create_empty_sudoku(self, frame, size=9):
        self.sudoku = Sudoku(gui=frame, **{'matrix': [], 'size': size})
        self.create_sudoku_layout(frame)

    def retrieve_input(self, frame):
        childrens = frame.winfo_children()
        for ch in childrens:
            childs = ch.winfo_children()

            print([type(child) for child in childs])

    def solve_sudoku(self, frame):

        self.retrieve_input(frame)

        children = frame.winfo_children()

        text_labels = []

        for child in children:
            for sub_child in child.winfo_children():
                sub_child.unbind("<<TextModified>>")
                sub_child.unbind("<<TextDeleted>>")
                text_labels.append(sub_child)
        print(self.sudoku.print_matrix())

        status = self.sudoku.solve(int(self.slider.get()) / 1000)
        if status:
            self.status_label['text'] = 'Soduko Solved !'
        else:
            self.status_label['text'] = 'Invalid input. Unable to solve the sudoku'

        for label in text_labels:
            label.bind("<<TextModified>>", self.onModification)
            label.bind("<<TextDeleted>>", self.onDeletion)

        print("Total moves: {}".format(self.sudoku.total_moves))

    def updated_timer(self, *args):
        timer_val = int(args[0])
        timer_val = timer_val / 10

    def onDeletion(self, event):
        print("delete called")
        text = event.widget

        val = event.widget.get("1.0", "end-1c")

        # check if still it's valid
        try:
            val = int(val)
            text.cell.val = val
            text['fg'] = "white"
            text['bg'] = 'rosybrown3'
            text['relief'] = 'sunken'
            return
        except:
            print("Invalid literal")
            text['bg'] = 'rosybrown1'
            text['fg'] = 'black'
            text['relief'] = "groove"
            text.cell.val = -1

    def onModification(self, event, delete=True):
        print('insert called')
        text = event.widget
        val = event.widget.get("1.0", "end-1c")

        try:
            val = int(val)
        except:
            print("Invalid literal")
            text.delete("1.0", tk.END)
            return

        text['fg'] = "white"
        text['bg'] = 'rosybrown3'
        text['relief'] = 'sunken'
        text.cell.val = val

    def vcmd(self, action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):

        if value_if_allowed:
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    def create_sudoku_layout(self, frame):

        for row, row_cells in enumerate(self.sudoku.matrix):
            self.sudoku_cell_gui_objs.append([])
            for column, cell in enumerate(row_cells):
                cell_frame = tk.Frame(frame, bg="white", height=70, width=70)

                cell_frame.grid(row=row, column=column, padx=5, pady=5)

                text = CustomText(cell, cell_frame, bg='rosybrown1', fg='black', height=2, width=4,
                                  font="Times 20 bold", borderwidth=4, relief="groove")
                text.tag_configure("center", justify='center')
                text.tag_add("center", 1.0, "end")

                if (cell.val != -1):
                    text['fg'] = "white"
                    text['bg'] = 'rosybrown3'
                    text['relief'] = 'sunken'
                    text.insert(cell.val)
                    text['state'] = tk.DISABLED
                else:
                    text.insert('')
                    pass
                text.pack(ipadx=5, ipady=5)
                text.bind("<<TextModified>>", self.onModification)
                text.bind("<<TextDeleted>>", self.onDeletion)

                self.sudoku_cell_gui_objs[row].append(text)

                moves_label = tk.Label(cell_frame, height=1, width=5, bg='rosybrown2',
                                       font="Times 10 italic")
                moves_label.pack(fill="both", expand=True)

                cell.label = text
                cell.moves_label = moves_label

    def create_widgets(self):

        button_frame = tk.Frame(self.master)
        button_frame.pack(side=tk.LEFT, padx=20)
        # button_frame.grid(row=0,rowspan=100, column=0,columnspan=10)

        sudoku_frame = tk.Frame(self.master, borderwidth=2, relief="solid")
        sudoku_frame.pack(side=tk.RIGHT, fill=tk.NONE, ipadx=50, expand=True)
        # sudoku_frame.grid(row=0, column=11, rowspan=100)

        load_sample_sudoku_bt = tk.Button(button_frame, bg="thistle2", text="LOAD SAMPLE", height=2, width=20,
                                          borderwidth=2, relief="raised",
                                          command=lambda: self.load_sample_sudoku(sudoku_frame))
        load_sample_sudoku_bt.pack(pady=10)

        create_empty_sudoku_bt = tk.Button(button_frame, bg="thistle2", text="NEW SUDOKU", height=2, width=20,
                                           borderwidth=2, relief="raised",
                                           command=lambda: self.create_empty_sudoku(sudoku_frame))
        create_empty_sudoku_bt.pack(pady=10)

        solve_bt = tk.Button(button_frame, bg="thistle2", text="SOLVE", borderwidth=2, height=2, width=20,
                             relief="raised", command=lambda: self.solve_sudoku(sudoku_frame))
        solve_bt.pack(pady=10)

        slider = tk.Scale(button_frame, label="delay (ms)", length=150, bg="thistle2", from_=0, to=1000,
                          tickinterval=200, borderwidth=2, relief="raised", command=self.updated_timer,
                          orient=tk.HORIZONTAL, sliderlength=20)
        self.slider = slider
        slider.pack(pady=10)

        tk.Label(button_frame, text="(delay between moves in ms)").pack()

        self.status_label = tk.Label(button_frame, font='Times 15 bold')
        self.status_label.pack()


    def updater(self):
        print('updated')
        self.after(UPDATE_RATE, self.updater)


if __name__ == '__main__':


    root = tk.Tk()
    app = Application(master=root)

    app.master.title("Sudoku Solver")
    app.master.geometry("1000x900")

    start_time = time.time()


    app.mainloop()

    sudoku = Sudoku(**{'matrix': Sudoku.get_sample_sudoku()})
    sudoku.solve()

    print(sudoku.total_moves)

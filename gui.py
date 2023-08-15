import time
import tkinter as tk

from SudokuSolver.solver import Solver


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

        self.solver = None
        self.master = master
        self.slider = None
        self.status_label = None
        self.show_possible_moves = None

        self.create_widgets()
        self.sudoku_cell_gui_objs = []

    def load_sample_sudoku(self, frame):
        sample_sudoku = Solver.get_sample_sudoku()
        self.solver = Solver(gui=self, **{'matrix': sample_sudoku, 'size': len(sample_sudoku)})
        self.create_sudoku_layout(frame)

    def create_empty_sudoku(self, frame, size=9):
        self.solver = Solver(gui=self, **{'matrix': [], 'size': size})
        self.create_sudoku_layout(frame)

    def retrieve_input(self, frame):
        childrens = frame.winfo_children()
        for ch in childrens:
            childs = ch.winfo_children()

            print([type(child) for child in childs])

    def on_deletion(self, event):

        text = event.widget
        val = event.widget.get("1.0", "end-1c")
        print('delete called %s' % val)

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

    def on_modification(self, event, delete=True):
        text = event.widget
        val = event.widget.get("1.0", "end-1c")
        try:
            val = int(val)
            if val > 9:
                val = val % 10
            print('insert called %s' % val)
        except:
            print("Invalid literal")
            text.delete("1.0", tk.END)
            return

        text['fg'] = "white"
        text['bg'] = 'rosybrown3'
        text['relief'] = 'sunken'
        text.cell.val = val

    def update_cell_at_runtime(self, cell_gui_obj, value, moves_label_gui_obl, moves_val):
        cell_gui_obj.delete("1.0", tk.END)
        if value == -1:
            cell_gui_obj.insert('')
            cell_gui_obj['bg'] = 'rosybrown2'
            # cell.label['relief'] = 'groove'
        else:
            cell_gui_obj.insert(value)
            cell_gui_obj['bg'] = 'rosybrown2'
            # cell.label['relief'] = 'groove'

        if moves_label_gui_obl:
            moves_label_gui_obl['text'] = "{}".format(moves_val)
        self.update_idletasks()

        time.sleep(int(self.slider.get()) / 1000)

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

    def solve_sudoku(self, frame):

        self.retrieve_input(frame)

        children = frame.winfo_children()

        text_labels = []

        # un-binding events so that solver does not interfere
        for child in children:
            for sub_child in child.winfo_children():
                sub_child.unbind("<<TextModified>>")
                sub_child.unbind("<<TextDeleted>>")
                text_labels.append(sub_child)

        self.status_label['text'] = ''

        validation_status, solver_status = self.solver.solve()

        if not validation_status:
            self.status_label['text'] = 'Invalid input. \nUnable to solve the sudoku'
            self.status_label['fg'] = 'red'

        if solver_status:
            self.status_label['text'] = 'Soduko Solved ! \nTotal moves {}'.format(self.solver.total_moves)
            self.status_label['fg'] = 'green'
        else:
            self.status_label['text'] = 'Invalid input. \nUnable to solve the sudoku'
            self.status_label['fg'] = 'red'

        # rebinding events
        for label in text_labels:
            label.bind("<<TextModified>>", self.on_modification)
            label.bind("<<TextDeleted>>", self.on_deletion)

        print("Total moves: {}".format(self.solver.total_moves))

    def create_sudoku_layout(self, frame):

        for row, row_cells in enumerate(self.solver.matrix):
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
                text.bind("<<TextModified>>", self.on_modification)
                text.bind("<<TextDeleted>>", self.on_deletion)

                self.sudoku_cell_gui_objs[row].append(text)
                cell.label = text

                if self.show_possible_moves.get():
                    moves_label = tk.Label(cell_frame, height=1, width=5, bg='rosybrown2',
                                           font="Times 10 italic")
                    moves_label.pack(fill="both", expand=True)

                    cell.moves_label = moves_label

    def update_sudoku_layout(self):
        show_moves = self.show_possible_moves.get()
        print(show_moves)
        for row, row_cells in enumerate(self.solver.matrix):
            for column, cell in enumerate(row_cells):
                if show_moves:
                    moves_label = tk.Label(cell.label.master, height=1, width=5, bg='rosybrown2',
                                           font="Times 10 italic")
                    moves_label.pack(fill="both", expand=True)

                    cell.moves_label = moves_label
                else:
                    cell.moves_label.destroy()
                    cell.moves_label = None

    def create_widgets(self):

        side_frame = tk.Frame(self.master)
        side_frame.pack(side=tk.LEFT, padx=20)

        sudoku_frame = tk.Frame(self.master, borderwidth=2, relief="solid")
        sudoku_frame.pack(side=tk.RIGHT, fill=tk.NONE, ipadx=50, expand=True)

        self.status_label = tk.Label(side_frame, font='Times 18 bold')
        self.status_label.pack(side=tk.TOP, pady=50)

        load_sample_sudoku_bt = tk.Button(side_frame, bg="thistle2", text="LOAD SAMPLE", height=2, width=20,
                                          borderwidth=2, relief="raised",
                                          command=lambda: self.load_sample_sudoku(sudoku_frame))
        load_sample_sudoku_bt.pack(pady=10)

        create_empty_sudoku_bt = tk.Button(side_frame, bg="thistle2", text="NEW SUDOKU", height=2, width=20,
                                           borderwidth=2, relief="raised",
                                           command=lambda: self.create_empty_sudoku(sudoku_frame))
        create_empty_sudoku_bt.pack(pady=10)

        solve_bt = tk.Button(side_frame, bg="thistle2", text="SOLVE", borderwidth=2, height=2, width=20,
                             relief="raised", command=lambda: self.solve_sudoku(sudoku_frame))
        solve_bt.pack(pady=10)

        slider = tk.Scale(side_frame, label="delay (ms)", length=150, bg="thistle2", from_=0, to=1000,
                          tickinterval=200, borderwidth=2, relief="raised",
                          orient=tk.HORIZONTAL, sliderlength=20)
        self.slider = slider
        slider.pack(pady=10)

        tk.Label(side_frame, text="(delay between moves in ms)").pack()

        self.show_possible_moves = tk.IntVar()
        check_bt = tk.Checkbutton(side_frame, text='show possible moves per cell', variable=self.show_possible_moves,
                                  onvalue=1, offvalue=0,
                                  command=lambda: print(self.update_sudoku_layout()))
        check_bt.pack(pady=10, padx=0)


if __name__ == '__main__':
    s_time = time.time()

    root = tk.Tk()
    #
    # img = tk.PhotoImage('demo/sudoku.ico')
    # root.iconbitmap(img)

    app = Application(master=root)

    app.master.title("Sudoku Solver")
    app.master.geometry("1100x900")

    app.mainloop()

import tkinter as tk
import itertools as it
import client
from aux import *

# global variable
# imported conn from client

class App(tk.Tk):
    NUM_ROWS = 6
    NUM_COLS = 8

    def __init__(self):
        super().__init__()

        # display canvas
        self.canvas = tk.Canvas(self, width=720, height=640)
        self.canvas.pack()

        # instance variables
        self.letter_grid = ... # 6x8 2d array of letter displays
        self.visibile_word_rows = [0, 2, 4] # array of row indices from [0, 6)
        self.row_length = [5, 0, 7, 0, 8, 0] # array of row lengths from [0, 8]
        self.select_row, self.select_col = 0, 0 # int, int
        self.selecting = False # bool
        # binding inputs
        self.bind('<Motion>', self.mouse_move)
        self.bind('<Button-1>', self.left_click)
        self.bind('<Key>', self.key_pressed)
        self.bind('<Return>', self.return_key)

        # debug
        self.xy = self.canvas.create_text(40, 10, text="(0, 0)")
    
    def over_visible_row(self, row, col):
        """ returns a boolean whether the given r, c coordinate is over a visible letter """
        return col < self.row_length[row]
    
    def x_to_col(self, x):
        return (x - 50) // 80
    
    def col_to_x(self, r):
        return 80 * r + 50 + LetterDisplay.WIDTH // 2 

    def y_to_row(self, y):
        return (y - 50) // 120
    
    def row_to_y(self, c):
        return 120 * c + 50 + LetterDisplay.HEIGHT // 2

    def left_click(self, event):
        x, y = event.x, event.y
        col, row = self.x_to_col(x), self.y_to_row(y)

        # check if in the bounds of a visible row
        if self.over_visible_row(row, col):
            self.select(row, col)
            return

        # check if over the arrrow key
        # toggle expansion

    def key_pressed(self, event):
        if not self.selecting:
            return

        key = event.keycode
        # esc --> clear selection
        if key == 27: # esc
            self.deselect()
            # also minimize everything
        # arrow keys --> move selection
        elif key == 37: # left
            col = max(0, self.select_col - 1)
            self.select(self.select_row, col)
            self.select_col = col
        elif key == 38: # up
            # go to previous visible row
            row = self.select_row - 1
            while row >= 0:
                if self.row_length[row]:
                    self.select(row, min(self.select_col, self.row_length[row] - 1))
                    break
                row -= 1
        elif key == 39: # right
            col = min(self.row_length[self.select_row] - 1, self.select_col + 1)
            self.select(self.select_row, col)
            self.select_col = col
        elif key == 40: # down
            # go to next visible row
            row = self.select_row + 1
            while row < self.NUM_ROWS:
                if self.row_length[row]:
                    self.select(row, min(self.select_col, self.row_length[row] - 1))
                    break
                row += 1
        # a-z --> enter on select
        elif ord('A') <= key <= ord('Z'):
            self.letter_grid[self.select_row][self.select_col].update_letter(self.canvas, chr(key))
        # delete
        elif key == 8: # backspace
            self.letter_grid[self.select_row][self.select_col].update_letter(self.canvas, "")

    def return_key(self, event):
        # enter --> submit guess (only if word is full)
        pass

    def select(self, row, col):
        self.selecting = True
        # deselect current selection
        self.letter_grid[self.select_row][self.select_col].deselect(self.canvas)
        # select the word row and put cursor at the letter index
        self.letter_grid[row][col].select(self.canvas)
        # update instance vars
        self.select_row, self.select_col = row, col
    
    def deselect(self):
        self.selecting = False
        self.letter_grid[self.select_row][self.select_col].deselect(self.canvas)

    def mouse_move(self, event):
        x, y = event.x, event.y
        self.canvas.itemconfig(self.xy, text=f"({x},{y})")

    def display(self):
        """ Create the start screen"""
        
        # each square is a 100x100
        # y: 0-50 margin, 50-150 word 1, 170-270 word 2,
        # 290-390 word 3, 410-510 word 4, 530-630 word 5, 650-750 word 6, 750-800 margin
        # x: 0-50 margin, 50-150 letter 1, ... 750-850 letter 8, 850-900 margin
        # start screen only uses words 1, 3, 5
        # ABOVE IS NOW SCALED BY 0.8
        # create the 6x8 grid of letters
        xs = range(self.NUM_ROWS)
        ys = range(self.NUM_COLS)
        centers = it.product(xs, ys)
        self.letter_grid = [
            [LetterDisplay(self.col_to_x(c), self.row_to_y(r)) 
            for c in range(self.NUM_COLS)]
            for r in range(self.NUM_ROWS)]
        # set the visibilty of the start screen
        letter_iter = it.chain(*self.letter_grid)
        visibility_iter = it.chain.from_iterable([True] * l + [False] * (self.NUM_COLS-l) for l in self.row_length)
        for letter, visibility in zip(letter_iter, visibility_iter):
            if visibility:
                letter.toggle_display(self.canvas)

        # add the arrow buttons

    def run(self):
        self.display()
        try:
            while self.state():
                self.update()
                self.update_idletasks()
        except tk.TclError:
            pass

class LetterDisplay:
    WIDTH = 80  # px
    HEIGHT = 80 # px
    
    def __init__(self, x, y, *, visibility = False, letter = ""):
        self.visibility = visibility # bool
        self.letter = letter # str
        self.center = (x, y) # tuple[int, int]
        self.selected = False # bool

        self.widget_ids = []
    
    def corners(self):
        """ Returns list[tuple[int, int]] """
        cx, cy = self.center # center x, y
        x0, x1 = cx - self.WIDTH / 2, cx + self.WIDTH / 2
        y0, y1 = cy - self.HEIGHT / 2, cy + self.HEIGHT / 2
        return [
            (x0, y0), 
            (x1, y0), 
            (x1, y1), 
            (x0, y1)
        ]

    def show_display(self, canvas):
        # create the grid
        corners = self.corners()
        square_id = canvas.create_line(*it.chain(*corners), *corners[0])

        # create the letter textbox
        letter_id = canvas.create_text(*self.center, text=self.letter, font=("Helvetica", "25"))

        # append to widget_ids
        self.widget_ids.append(square_id)
        self.widget_ids.append(letter_id)
    
    def hide_display(self, canvas):
        for id in self.widget_ids:
            canvas.delete(id)

    def toggle_display(self, canvas):
        self.visibility = not self.visibility
        if self.visibility:
            self.show_display(canvas)
        else:
            self.hide_display(canvas)

    def select(self, canvas):
        self.selected = True
        if not self.visibility:
            return
        # move border to front
        canvas.tag_raise(self.widget_ids[0], 'all')
        # highlight border
        canvas.itemconfig(self.widget_ids[0], fill="orange")

    def deselect(self, canvas):
        canvas.itemconfig(self.widget_ids[0], fill="black")
        self.selected = False

    def update_letter(self, canvas, letter):
        self.letter = letter
        canvas.itemconfig(self.widget_ids[1], text=letter)

if __name__ == "__main__":
    App().start()

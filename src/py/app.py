import tkinter as tk
import itertools as it
import functools as ft
import operator
import animations
import client
from color import Color
from letter import Letter

"""
TODO:
    - fix selection in expanded mode
    - completed words should not be editable
    - return back to homescreen after complete
    - letter flipping
    - emphasis on letter inputs
    - UX --> delete should delete the last letter if not selected and is the most right
    -    --> maybe start with selecting the (0, 0) (expanded mode)
    - UI --> update to IRIS
"""
class App(tk.Tk):
    # class variables
    NUM_ROWS = 6
    NUM_COLS = 8
    NUM_KEYS = 3
    WIDTH = 720
    HEIGHT = 640
    UNSET_INDEX = -1
    LETTER_HOR_MARGIN = 20
    LETTER_VER_MARGIN = 24
    SIDE_MARGIN = 50
    DEFAULT_ROW_LENGTHS = [5, 0, 7, 0, 8, 0]

    def __init__(self):
        super().__init__()

        # create canvas
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()
        
        # instantiate variables
        self.letter_grid = [[None] * self.NUM_COLS for _ in range(self.NUM_ROWS)]
        self.row_lengths = self.DEFAULT_ROW_LENGTHS
        self.selectable_rows = [bool(length) for length in self.row_lengths]
        self.selected_row, self.selected_col, self.key_index = [self.UNSET_INDEX] * 3
        self.selecting = False
        self.expanded = False
        self.history = [[] for _ in range(self.NUM_KEYS)]

        # binding inputs
        self.bind('<Button-1>', self.left_click)
        self.bind('<Key>', self.key_pressed)
        self.bind('<Return>', self.return_key)
        
        # debug
        self.bind('<Motion>', self.mouse_move)
        self.xy = self.canvas.create_text(40, 10, text="(0, 0)")

    def mouse_move(self, event):
        x, y = event.x_root - self.winfo_rootx(), event.y_root - self.winfo_rooty()
        row, col = self.y_to_row(y), self.x_to_col(x)
        self.canvas.itemconfig(self.xy, text=f"({x},{y}) ({row},{col})")

    def left_click(self, event):
        x, y = event.x_root - self.winfo_rootx(), event.y_root - self.winfo_rooty()
        col, row = self.x_to_col(x), self.y_to_row(y)
        if self.is_selectable(row, col):
            self.select(row, col) # this sets the key_index
            self.expand()
        
        # check if over arrow

    def key_pressed(self, event):
        if not self.selecting:
            return
        key = event.keycode

        # define the methods
        def esc():
            self.deselect()
            self.minimize()
        def left():
            if self.selected_col == 0:
                return
            self.select(self.selected_row, self.selected_col - 1)
        def right():
            if self.selected_col == self.row_lengths[self.selected_row] - 1:
                return
            self.select(self.selected_row, self.selected_col + 1)
        def alphabet():
            char = chr(key)
            self.letter_grid[self.selected_row][self.selected_col].set_color(Color.GRAY, update=False)
            self.letter_grid[self.selected_row][self.selected_col].set_letter(char)
            right()
        def backspace():
            self.letter_grid[self.selected_row][self.selected_col].set_color(Color.WHITE, update=False)
            self.letter_grid[self.selected_row][self.selected_col].set_letter(" ")
            left()
        
        # map methods to keycode
        if   key == 27: esc()
        elif key == 37: left()
        elif key == 39: right()
        elif key == 8: backspace()
        elif ord('A') <= key <= ord('Z'):
            alphabet()
    
    def valid_word(self, word, key_index):
        row = self.key_index_to_row(key_index)
        return len(word) == self.DEFAULT_ROW_LENGTHS[row] \
                and client.valid_word(word)

    def return_key(self, _):
        if not self.selecting:
            return
        
        word = self.get_word(self.selected_row)
        if not self.valid_word(word, self.key_index):
            return
        
        # if word is correct
        # skip the moving history
        if self.correct_guess(word):
            self.history[self.key_index].append(word)
            self.propagate_history(N=1, offset=-1) # slow
            return
        
        # update display
        self.set_history_row_lengths(add=1)
        self.update_display()
        # move everything down
        self.propagate_history(offset=1) # fast
        # update history
        self.history[self.key_index].append(word)
        self.propagate_history(N=1) # slow
        # delete row 0
        word_length = len(word)
        self.set_row(0, " " * word_length, [Color.WHITE] * word_length, animations.Mode.FAST)
        # set selected to column 0
        self.select(0, 0)

    # visual methods
    def expand(self):
        """ 
        Precondition: self.key_index is set
        Propagates the history of the key_index
        """
        # already done
        if self.expanded:
            return
        self.expanded = True
        
        self.set_history_row_lengths()
        self.update_display()
        self.propagate_history()
        self.select(0, 0)
        # delete row 0
        self.set_row(
            0, 
            self.get_empty_word(self.key_index),
            self.get_empty_colors(self.key_index),
            animations.Mode.FAST
        )

    def minimize(self):
        # already done
        if not self.expanded:
            return
        self.expanded = False

        # update the grid display to original lengths
        # this clears the expanded display
        self.row_lengths = self.DEFAULT_ROW_LENGTHS
        self.update_display()
        
        # unset the key_index instance variable
        self.key_index = self.UNSET_INDEX

        # propagate the keys with the most recent in history
        for key_index, history in enumerate(self.history):
            # if the history is empty, leave as blank
            # otherwise set it as the most recent guess
            word = self.get_empty_word(key_index)
            colors = self.get_empty_colors(key_index)
            if history: 
                word = history[-1]
                colors = client.get_colors(word)
            self.set_row(
                self.key_index_to_row(key_index),
                word,
                colors,
                speed=animations.Mode.FAST
            )

    def select(self, row, col):
        """ 
        Precondition: row and col is selectable
        Sets the selecting and key_index instance variables
        Moves the selection to row, col
        """
        # move the current selected to row, col
        self.deselect()
        self.letter_grid[row][col].set_selected(True)
        self.selected_row, self.selected_col = row, col
        # sets the instance variables
        self.selecting = True
        if not self.expanded:
            self.key_index = self.row_to_key_index(row)

    def deselect(self):
        """
        Removes the letter selection at the current selected_row and col
        Sets selecting to False
        """
        row, col = self.selected_row, self.selected_col
        self.letter_grid[row][col].set_selected(False)
        # unsets the instance variables
        self.selecting = False
        self.selected_row, self.selected_col = self.UNSET_INDEX, self.UNSET_INDEX
        if not self.expanded:
            self.key_index = self.UNSET_INDEX

    # display
    def init_display(self):
        """ create the self.NUM_ROWS x self.NUM_COLS grid array with their visability """
        for row, col in it.product(range(self.NUM_ROWS), range(self.NUM_COLS)):
            self.letter_grid[row][col] = Letter(
                self,
                self.col_to_x(col),
                self.row_to_y(row),
                visibility=self.is_visible(row, col)
            )

    def update_display(self):
        for row, col in it.product(range(self.NUM_ROWS), range(self.NUM_COLS)):
            self.letter_grid[row][col].set_visibility(self.is_visible(row, col))
    
    # driver
    def run(self):
        self.init_display()

        try:
            while self.state():
                self.update()
                self.update_idletasks()
        except tk.TclError:
            pass

    # helper methods
    def get_word(self, row):
        row = self.letter_grid[self.selected_row]
        return ft.reduce(operator.add, (letter.letter for letter in row)).strip().lower()

    def set_row(self, row, word, colors, speed):
        # precondition: the row should be of equal length to colors
        for col, (char, color) in enumerate(zip(word, colors)):
            letter = self.letter_grid[row][col]
            letter.set_letter_color(char, color)

    def propagate_history(self, speed=animations.Mode.FAST, offset=0, N=None):
        # precondition: the update_display method should have been called
        # and the visibility in the grid should be correctly set
        if N is None: N = self.NUM_ROWS - 1 - offset # default for N
        history = self.history[self.key_index]
        for row, guess in zip(range(N), reversed(history)):
            # history starts at index 1 (offset is for shifting down)
            self.set_row(
                row + 1 + offset,                 
                guess,
                client.get_colors(guess),
                speed
            )
    
    def set_history_row_lengths(self, *, add=0):
        # local variables
        key_row = self.key_index_to_row(self.key_index)
        key_length = self.DEFAULT_ROW_LENGTHS[key_row]
        history = self.history[self.key_index]
        history_length = len(history)
        
        # update the grid display with new lengths
        # this also clears old displays
        self.row_lengths = [key_length] * (history_length + 1 + add) \
                + [0] * (self.NUM_ROWS - history_length - 1 - add)

    def is_selectable(self, row, col):
        # an index is selectable if the row is selectable
        # and the column is within the row length
        return row < self.NUM_ROWS and self.selectable_rows[row] and col < self.row_lengths[row] 

    def x_to_col(self, x):
        letter_size = Letter.SIZE + self.LETTER_HOR_MARGIN // 2
        return (x - self.SIDE_MARGIN) // letter_size

    def col_to_x(self, col):
        letter_size = Letter.SIZE + self.LETTER_HOR_MARGIN // 2
        x_left = letter_size * col + self.SIDE_MARGIN 
        return x_left + letter_size // 2

    def y_to_row(self, y):
        letter_size = Letter.SIZE + self.LETTER_VER_MARGIN // 2
        return (y - self.SIDE_MARGIN) // letter_size

    def row_to_y(self, row):
        letter_size = Letter.SIZE + self.LETTER_VER_MARGIN // 2
        y_top = letter_size * row + self.SIDE_MARGIN 
        return y_top + letter_size // 2
    
    def row_to_key_index(self, row):
        return row // 2

    def key_index_to_row(self, key_index):
        return key_index * 2

    def is_visible(self, row, col):
        return col < self.row_lengths[row]
    
    def get_empty_word(self, key_index):
        word_length = self.DEFAULT_ROW_LENGTHS[self.key_index_to_row(key_index)]
        return " " * word_length

    def get_empty_colors(self, key_index):
        word_length = self.DEFAULT_ROW_LENGTHS[self.key_index_to_row(key_index)]
        return [Color.WHITE] * word_length
    
    def set_empty_word(self, row, key_index, speed):
        self.set_row(
            row,
            self.get_empty_word(key_index),
            self.get_empty_colors(key_index),
            speed
        )
    
    def correct_guess(self, guess):
        # precondition: word is valid
        colors = client.get_colors(guess)
        return colors == [Color.GREEN] * len(colors)

if __name__ == "__main__":
    App().run()

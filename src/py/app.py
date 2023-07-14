import tkinter as tk
import itertools as it
import functools as ft
import operator
import time
import animations
import client
from enum import Enum, auto
from aux import *
from color import Color
from letter import Letter
from animations import Mode

"""
TODO:
    - do not allow user actions during animation playing

    - BUG -> instant animations are not instant
    - change order of animations:
    - update display should always create empty letters
    - reimplement with new animation changes:
        - play_sequential (wait for previous to start)
        - play_wave (fixed delay in between)
        - play_simultaneous (no delay wave)
"""

class Screen(Enum):
    HOME = auto()
    GAME = auto()
    END = auto()

class App(tk.Tk):
    # class variables
    NUM_ROWS = 6
    NUM_COLS = 8
    NUM_KEYS = 3
    KEY_LENGTHS = [5, 7, 8] 
    WIDTH = 720
    HEIGHT = 640
    UNSET_INDEX = -1
    LETTER_HOR_MARGIN = 20
    LETTER_VER_MARGIN = 24
    SIDE_MARGIN = 50
    
    def __init__(self):
        super().__init__()

        # create canvas
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()
        
        # instantiate variables
        self.key_index = 0 # this is how many keys the player has guessed
        self.letter_grid = [[None] * self.NUM_COLS for _ in range(self.NUM_ROWS)]
        self.row_lengths = self.home_row_lengths()
        self.selectable_rows = [bool(length) for length in self.row_lengths]
        self.history = [[] for _ in range(self.NUM_KEYS)]
        # state variables
        self.screen = Screen.HOME
        # during home screen, this is the row that can be expanded
        # during home screen, you can select and expand
        # during game screen, you can edit and minimize
        # during end screen, you can do nothing :D
        self.expanded_key_index = 0
        # this is the key that the player is current looking at
        self.selected_row = self.UNSET_INDEX
        # this is the row that is edited on during game screen

        # binding inputs
        self.bind('<Key>', self.key_pressed)
        self.bind('<Return>', self.return_key)
        
        # create display
        self.init_display()
        # start with row 0 selected and expanded
        self.select(0)
        self.expand(0)
        # debug
        self.bind('<Motion>', self.mouse_move)
        self.xy = self.canvas.create_text(40, 10, text="(0, 0)")
        
    def mouse_move(self, event):
        x, y = event.x_root - self.winfo_rootx(), event.y_root - self.winfo_rooty()
        row, col = self.y_to_row(y), self.x_to_col(x)
        self.canvas.itemconfig(self.xy, text=f"({x},{y}) ({row},{col})")

    def key_pressed(self, event):
        key = event.keycode
        self.play_fireworks()
        # if self.key_index == self.NUM_KEYS:
        #     print("FIX line101 app.py")
        #     self.images_cache = [] # so garbage collector does not delete images
        #     # replace ^ with a hashmap that animations manage
        #     filenames = [f"data/fireworks/animation0{frame}.jpg" for frame in range(5)]
        #     label = tk.Label(self.canvas)
        #     label.place(x=300, y=300)
        #     animation = animations.image_animation(filenames, time.perf_counter(), Mode.SLOW, label, self)
        #     animations.play_animation(animation)

        # define the methods
        def esc():
            if self.screen is not Screen.GAME:
                return
            self.minimize()
            self.select(0)

        def alphabet():
            if not self.can_edit():
                return

            char = chr(key)
            col = self.rightmost_column(self.selected_row)
            col = min(col, self.row_lengths[self.selected_row] - 1)
            if col < 0: print("WARNING SELECTING INVISIBLE ROW")
            letter = self.letter_grid[self.selected_row][col]
            letter.set_letter_color(char, Color.GRAY)
            ani = animations.letter_emphasis(letter, Mode.FAST, time.perf_counter())
            animations.play_animation(ani)

        def backspace():
            if not self.can_edit():
                return

            col = self.rightmost_column(self.selected_row) - 1
            if col < 0: return
            letter = self.letter_grid[self.selected_row][col]
            letter.set_letter_color(" ", Color.WHITE)
            ani = animations.letter_emphasis(letter, Mode.FAST, time.perf_counter())
            animations.play_animation(ani)

        def down():
            if self.screen is not Screen.HOME:
                return

            # change selected row
            self.selected_row = fit_bounds(self.selected_row + 1, 0, self.NUM_KEYS - 1)
            # update selection
            self.select(self.selected_row)
            self.update_selection_circle(self.selected_row)
        def up():
            if self.screen is not Screen.HOME:
                return

            # change selected row
            self.selected_row = fit_bounds(self.selected_row - 1, 0, self.NUM_KEYS - 1)
            # update selection
            self.select(self.selected_row)
            self.update_selection_circle(self.selected_row)
        
        # map methods to keycode
        if   key == 27: esc()
        elif key == 8: backspace()
        elif key == 40: down()
        elif key == 38: up()
        elif ord('A') <= key <= ord('Z'):
            alphabet()
    
    def return_key(self, _):
        if self.screen is Screen.HOME:
            # expand the current selected_row
            expanded_row = self.row_to_key_index(self.selected_row)
            self.expand(expanded_row) # this sets self.expanded_key_index
            self.select(0)
            return
        
        # limit to game screen actions
        if not self.can_edit():
            return

        word = self.get_word(self.selected_row)
        if not self.valid_word(word, self.key_index):
            # vibrate word
            letters = self.letter_grid[self.selected_row]
            mode = Mode.FAST
            start = time.perf_counter()
            N = self.row_lengths[self.selected_row]
            anis = [animations.letter_vibrate(letter, mode, start) for letter, _ in zip(letters, range(N))]
            animations.play_simultaneous(*anis)
            return
        
        # if word is correct
        # skip the moving history
        if self.correct_guess(word):
            self.history[self.key_index].append(word)
            animations.play_animation(self.propagate_history_ani(N=1, offset=-1)) # slow
            # wait a second then return back to home screen
            self.key_index += 1
            time.sleep(1)
            self.minimize()
            return
        
        # animations
        anis = []
        # update display
        self.set_history_row_lengths(add=1)
        self.update_display()
        # move everything down
        anis.append(self.propagate_history_ani(offset=1, speed=animations.Mode.FAST))
        # update history
        self.history[self.key_index].append(word)
        anis.append(self.propagate_history_ani(N=1, speed=animations.Mode.SLOW)) 
        # delete row 0
        word_length = len(word)
        anis.append(self.set_row_ani(0, " " * word_length, [Color.WHITE] * word_length, animations.Mode.FAST))

        # play animations
        animations.play_simultaneous(*anis)

    # visual methods
    def expand(self, index):
        """ 
        Precondition: self.key_index is set
        Propagates the history of the key_index
        """
        # already done
        if self.screen is Screen.GAME:
            return
        self.screen = Screen.GAME
        self.expanded_key_index = index
        # if the most recent guess was correct
        history = self.history[index]
        if history and self.correct_guess(history[-1]):
            self.set_history_row_lengths(add=-1)
            self.update_display()
            ani = self.propagate_history_ani(speed=animations.Mode.FAST, offset=-1)
            animations.play_animation(ani)
            return
        
        # move editing cursor to row 0
        self.selectable_rows = [True] + [False] * (self.NUM_ROWS - 1)
        self.select(0)
        self.update_selection_circle(0)
        self.set_history_row_lengths()
        self.update_display()
        anis = []
        if self.history[self.key_index]:
            anis.append(self.propagate_history_ani(speed=animations.Mode.FAST))
        # delete row 0
        anis.append(self.set_empty_word_ani(0, self.key_index, speed=Mode.INSTANT))
        # play
        animations.play_simultaneous(*anis)

    def minimize(self):
        # already done
        if self.screen is Screen.HOME:
            return
        self.screen = Screen.HOME
        # update the grid display to original lengths
        # this clears the expanded display
        self.expanded_key_index = self.UNSET_INDEX
        self.row_lengths = self.home_row_lengths()
        self.selectable_rows = [bool(length) for length in self.row_lengths]
        self.update_display()

        # propagate the keys with the most recent in history
        anis = []
        for key_index, history in zip(range(self.key_index + 1), self.history):
            # if the history is empty, leave as blank
            # otherwise set it as the most recent guess
            word = self.get_empty_word(key_index)
            colors = self.get_empty_colors(key_index)
            if history: 
                word = history[-1]
                colors = client.get_colors(word)
            anis.append(self.set_row_ani(
                self.key_index_to_row(key_index),
                word,
                colors,
                speed=animations.Mode.FAST
            ))
        animations.play_simultaneous(*anis)

    def select(self, row):
        """ 
        Precondition: row and col is selectable
        Sets the selecting and key_index instance variables
        Moves the selection to row, col
        """
        # move the current selected to row, col
        self.deselect()
        col = self.rightmost_column(row)
        # sets the instance variables
        self.selected_row = row

    def deselect(self):
        """
        Removes the letter selection at the current selected_row and col
        Sets selecting to False
        """
        row = self.selected_row
        col = self.rightmost_column(row)
        # unsets the instance variables
        self.selected_row = self.UNSET_INDEX
    
    # end_screen animation
    def firework_location(self):
        """ Generates a random location to play a random fireworks animation """
        print("update app.py 297")
        return (50, 50)

    def play_fireworks(self):
        """ Calls play_firework until the stop_fireworks button is stopped """
        # create button
        
        # create label
        label = tk.Label()
        x, y = self.firework_location()
        label.place(x=x, y=y)
        # create animation
        filenames = [f"data/fireworks/frame_{i}.jpg" for i in range(62)]
        self.images_cache = []
        ani = animations.image_animation(
            filenames,
            time.perf_counter(),
            Mode.VIDEO,
            label,
            self
        )
        animations.play_animation(ani)

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
        # create the yellow circle to the side of the selected_row
        self.circle = self.canvas.create_oval(0, 0, 0, 0, fill="yellow")
        self.update_selection_circle(0)

    def update_display(self):
        for row, col in it.product(range(self.NUM_ROWS), range(self.NUM_COLS)):
            # self.letter_grid[row][col].set_letter_color(" ", Color.WHITE)
            self.letter_grid[row][col].set_visibility(self.is_visible(row, col))
    
    # driver
    def run(self):
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

    def set_row_ani(self, row, word, colors, speed):
        # precondition: the row should be of equal length to colors
        return animations.flip_letter_row(self.letter_grid[row], colors, word, speed, time.perf_counter())

    def propagate_history_ani(self, speed=animations.Mode.FAST, offset=0, N=None):
        # precondition: the update_display method should have been called
        # and the visibility in the grid should be correctly set
        if N is None: N = self.NUM_ROWS - 1 - offset # default for N
        history = self.history[self.expanded_key_index]
        
        letters_rows = [self.letter_grid[row + 1 + offset] for row in range(N)]
        words = list(reversed(history))
        colors_rows = [client.get_colors(guess) for guess in words]
        return animations.flip_letter_grid(letters_rows, colors_rows, words, speed, time.perf_counter())
    
    def set_history_row_lengths(self, *, add=0):
        # local variables
        key_index = self.row_to_key_index(self.selected_row)
        key_length = self.key_length(self.expanded_key_index)
        history = self.history[self.expanded_key_index]
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
        return row

    def key_index_to_row(self, key_index):
        return key_index

    def is_visible(self, row, col):
        return col < self.row_lengths[row]
    
    def get_empty_word(self, key_index):
        return " " * self.key_length(key_index)

    def get_empty_colors(self, key_index):
        return [Color.WHITE] * self.key_length(key_index)
    
    def set_empty_word_ani(self, row, key_index, speed):
        return self.set_row_ani(
            row,
            self.get_empty_word(key_index),
            self.get_empty_colors(key_index),
            speed
        )
    
    def valid_word(self, word, key_index):
        return len(word) == self.key_length(key_index) and client.valid_word(word)

    def correct_guess(self, guess):
        # precondition: word is valid
        colors = client.get_colors(guess)
        return colors == [Color.GREEN] * len(colors)
    
    def rightmost_column(self, row):
        """ Returns the first visible column in the row that has no text """
        num_cols = self.row_lengths[row]
        has_text = [col if not letter.has_text() else num_cols
                    for col, letter in enumerate(self.letter_grid[row])]
        return min(has_text) 
    
    def key_length(self, key_index):
        return self.KEY_LENGTHS[self.key_index_to_row(key_index)]
    
    def home_row_lengths(self):
        return [length for index, length in enumerate(self.KEY_LENGTHS) if index <= self.key_index] \
            + [0] * (self.NUM_ROWS - self.key_index)
        
    def update_selection_circle(self, row):
        r = 10
        x = 25
        y = self.row_to_y(row)
        self.canvas.coords(self.circle, x-r, y-r, x+r, y+r)
    
    def can_edit(self):
        return self.screen is Screen.GAME \
                and self.key_index == self.expanded_key_index \
                and self.selected_row == 0

if __name__ == "__main__":
    App().run()

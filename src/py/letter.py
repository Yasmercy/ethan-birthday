import animations
import itertools as it
import tkinter as tk
from aux import *
from color import Color
from PIL import ImageTk, Image

FONT_DIRECTORY = "data/font"

class Letter:
    SIZE = 70  # px
    BORDER_WIDTH = 3 # px
    SELECTED_COLOR = 'orange'
    DESELECTED_COLOR = 'black'
    
    __slots__ = {
        "root",
        "center",
        "color",
        "image",
        "visibility",
        "selected",
        "grid_id",
        "widget_img",
        "letter"
    }

    def __init__(self, root, x, y, *, letter=" ", visibility=False, color=Color.WHITE, selected=False):
        self.root = root
        self.center = x, y

        # initialize with all defaults
        self.color = Color.WHITE
        self.letter = " "
        self.visibility = False
        self.selected = False
        
        # call the designated setters
        self.set_image()
        self.set_visibility(visibility)
        self.set_color(color)
        self.set_letter(letter)

    # could use a decorator for the setters to reduce boilerplate
    def set_visibility(self, visibility):
        if visibility == self.visibility:
            return
        
        self.visibility = visibility
        if self.visibility:
            self.show_display(self.root.canvas) 
        else:
            self.hide_display(self.root.canvas)

    def set_letter_color(self, letter, color):
        if color == self.color and letter == self.letter:
            return

        self.color = color
        self.letter = letter
        self.set_image()
        if self.visibility:
            self.update_display(self.root.canvas)

    def set_color(self, color, *, update=True):
        if color == self.color:
            return

        self.color = color
        if not update:
            return

        self.set_image()
        if self.visibility:
            self.update_display(self.root.canvas)
    
    def set_letter(self, letter, *, update=True):
        if letter == self.letter:
            return

        self.letter = letter
        if not update:
            return

        self.set_image()
        if self.visibility:
            self.update_display(self.root.canvas)
    
    def has_text(self):
        return self.visibility and not self.letter.strip() == ""

    # changing display (for animations)
    def v_stretch(self, scale):
        """ note: this resets the horizontal back to normal """
        edges = corners(
            *self.center, 
            self.SIZE // 2 - 2 * self.BORDER_WIDTH, 
            self.SIZE // 2 * scale - 2 * self.BORDER_WIDTH
        )
        self.resize(edges)

    def h_stretch(self, scale):
        edges = corners(
            *self.center, 
            self.SIZE // 2 * scale - 2 * self.BORDER_WIDTH,
            self.SIZE // 2 - 2 * self.BORDER_WIDTH, 
        )
        self.resize(edges)

    def dilate(self, scale):
        edges = corners(
            *self.center, 
            self.SIZE // 2 * scale - 2 * self.BORDER_WIDTH,
            self.SIZE // 2 * scale - 2 * self.BORDER_WIDTH
        )
        self.resize(edges)

    # helpers
    def resize(self, edges):
        canvas = self.root.canvas
        # change the grid
        # add back 2 * self.BORDER_WIDTH to edges
        w = - 2 * self.BORDER_WIDTH
        self.root.canvas.coords(
            self.grid_id,
            edges[0][0] + w, edges[0][1] + w,
            edges[1][0] - w, edges[1][1] + w,
            edges[2][0] - w, edges[2][1] - w,
            edges[3][0] + w, edges[3][1] - w,
            edges[0][0] + w, edges[0][1] + w,
        )
        # change the image
        (x0, y0), (x1, y1) = edges[0], edges[2]
        width = max(1, int(x1 - x0))  # cannot be 0
        height = max(1, int(y1 - y0)) # cannot be 0
        img = Image.open(self.get_filename())
        img = img.resize((width, height), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)
        self.update_display()
        self.root.update()

    def set_image(self):
        img = Image.open(self.get_filename())
        img = img.resize(
            (self.SIZE - 2 * self.BORDER_WIDTH, self.SIZE - 2 * self.BORDER_WIDTH), 
            Image.ANTIALIAS
        )
        self.image = ImageTk.PhotoImage(img)
    
    def corners(self):
        return corners(*self.center, self.SIZE // 2, self.SIZE // 2)

    def show_display(self, canvas):
        """
        Sets the widget_ids and the image instance variables
        widgets: grid, square, image
        """
        corners = self.corners()
        self.grid_id = canvas.create_line(*it.chain.from_iterable(corners), *corners[0])
        self.widget_img = tk.Label(canvas, image=self.image)
        self.widget_img.place(x=self.center[0], y=self.center[1], anchor='center')

    def hide_display(self, canvas):
        canvas.delete(self.grid_id)
        self.widget_img.destroy()

    def update_display(self, _=None):
        self.widget_img.config(image=self.image)

    def get_filename(self):
        letter_name = self.letter
        if letter_name == " ":
            letter_name = "empty"
        return f"{FONT_DIRECTORY}/{letter_name.upper()}_{self.color.value.lower()}.jpg"


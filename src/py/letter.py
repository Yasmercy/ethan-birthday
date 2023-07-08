import animations
import itertools as it
import tkinter as tk
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
        "widget_ids",
        "widget_img",
        "letter"
    }

    def __init__(self, root, x, y, *, letter=" ", visibility=False, color=Color.WHITE, selected=False):
        self.root = root
        self.center = x, y

        # initialize with all defaults
        self.widget_ids = []
        self.color = Color.WHITE
        self.letter = " "
        self.visibility = False
        self.selected = False
        
        # call the designated setters
        self.set_image()
        self.set_visibility(visibility)
        self.set_selected(selected)
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
    
    def set_selected(self, selected):
        if selected == self.selected:
            return

        self.selected = selected
        if self.selected:
            self.select(self.root.canvas)
        else:
            self.deselect(self.root.canvas)
    
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

    # helpers
    def set_image(self):
        img = Image.open(self.get_filename())
        img.resize(
            (self.SIZE - self.BORDER_WIDTH, self.SIZE - self.BORDER_WIDTH), 
            Image.ANTIALIAS
        )
        self.image = ImageTk.PhotoImage(img)
    
    def corners(self):
        (cx, cy), w, h = self.center, self.SIZE // 2, self.SIZE // 2
        return [
            (cx - w, cy - h),
            (cx + w, cy - h),
            (cx + w, cy + h),
            (cx - w, cy + h)
        ]

    def select(self, canvas):
        """ set the border color """
        # precondition: visibility = true
        canvas.itemconfig(self.widget_ids[0], fill=self.SELECTED_COLOR)

    def deselect(self, canvas):
        """ reset the border color """
        # precondition: visibility = true
        canvas.itemconfig(self.widget_ids[0], fill=self.DESELECTED_COLOR)

    def show_display(self, canvas):
        """
        Sets the widget_ids and the image instance variables
        widgets: grid, square, image
        """
        corners = self.corners()
        grid_id = canvas.create_line(*it.chain.from_iterable(corners), *corners[0])
        square_id = canvas.create_rectangle(*corners[0], *corners[2], width=0) # no border
        self.widget_ids = [grid_id, square_id]
        self.widget_img = tk.Label(canvas, image=self.image)
        self.widget_img.place(x=self.center[0], y=self.center[1], anchor='center')

    def hide_display(self, canvas):
        for id in self.widget_ids:
            canvas.delete(id)
        self.widget_img.destroy()

    def update_display(self, _):
        self.widget_img.config(image=self.image)

    def get_filename(self):
        letter_name = self.letter
        if letter_name == " ":
            letter_name = "empty"
        return f"{FONT_DIRECTORY}/{letter_name.upper()}_{self.color.value.lower()}.jpg"


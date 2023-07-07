from color import Color
import itertools as it
import math
import time 

class LetterDisplay:
    WIDTH = 80  # px
    HEIGHT = 80 # px
    
    def __init__(self, x, y, *, visibility = False, letter = ""):
        self.visibility = visibility # bool
        self.letter = letter # str
        self.center = (x, y) # tuple[int, int]
        self.selected = False # bool
        
        # [outline, filled_square, letter]
        self.widget_ids = [0, 0, 0]
    
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
        outline_id = canvas.create_line(*it.chain(*corners), *corners[0])
        square_id = canvas.create_rectangle(*corners[0], *corners[2], width=0) # no border

        # create the letter textbox
        letter_id = canvas.create_text(*self.center, text=self.letter, font=("Helvetica", "25"))
        
        # update widget_ids
        self.widget_ids = [outline_id, square_id, letter_id]

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
        canvas.itemconfig(self.widget_ids[2], text=letter)
        # bring letter to front again
        canvas.tag_raise(self.widget_ids[2], 'all')
    
    def map_color(self, color):
        if isinstance(color, str):
            return color
        return ["gray", "yellow", "green"][color.value]
    
    def animate(self, timestep, total_time, f):
        start = time.perf_counter()
        counter = 0
        num_steps = total_time / timestep
        while counter <= num_steps:
            t = counter * timestep
            if (time.perf_counter() - start) > t: 
                f(t)
                counter += 1

    def update_height(self, root, duration, t):
        # t is a parametric variable from [0, duration]
        scalar = 0.5 * math.cos(t * math.pi / duration) + 0.5
        new_height = self.HEIGHT * scalar
        
        cx, cy = self.center
        x0, x1 = cx - self.WIDTH // 2, cx + self.WIDTH // 2
        y0, y1 = cy - new_height // 2, cy + new_height // 2
        root.canvas.coords(self.widget_ids[0], x0, y0, x1, y0, x1, y1, x0, y1, x0, y0)
        root.canvas.coords(self.widget_ids[1], x0, y0, x1, y1)
        root.canvas.itemconfig(self.widget_ids[2], font=('Helvetica', str(int(25 * new_height / self.HEIGHT))))
        root.update()

    def set_color(self, root, color):
        # shrinking letter
        self.animate(0.0125, 0.25, lambda t: self.update_height(root, 0.25, t))
        # setting color of new letter
        self.color = self.map_color(color)
        root.canvas.itemconfig(self.widget_ids[1], fill=self.color)
        # expanding letter
        self.animate(0.0125, 0.25, lambda t: self.update_height(root, 0.25, t + 0.25))
        # bring letter to front again
        root.canvas.tag_raise(self.widget_ids[2], 'all')

    def reset_color(self, root, color):
        self.set_color(root, "white")

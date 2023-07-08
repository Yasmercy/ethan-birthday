import tkinter as tk
import time
from PIL import ImageGrab

def create_jpg(filename, text, color, font):
    """ 
    params: 
        filename : str
        text: str
        font: tuple[str, str]
    returns: void
    side effects: 
        create a file at the filename location (.jpg)
        that contains the specified letter
    """
    
    # set dimensions
    width, height = 80, 80
    x0, y0 = 100, 100
    x1, y1 = x0 + width, y0 + height
    # create window
    root = tk.Tk()
    root.geometry(f"{width}x{height}+{x0}+{y0}")
    canvas = tk.Canvas(root, width=width, height=height, bg=color)
    canvas.pack()
    # display a text block in the middle of the canvas
    text = tk.Label(canvas, font=font, text=text, bg=color)
    text.place(anchor='center', x=width // 2, y=height // 2)
    # update the window
    root.update()
    time.sleep(0.1)
    # screnshot the window
    xoffset = 185
    yoffset = 198
    ImageGrab.grab().crop((x0 + xoffset, y0 + yoffset, x1 + xoffset, y1 + yoffset)).save(filename)
    # close window
    root.destroy()

if __name__ == "__main__":
    for char in range(ord('A'), ord('Z') + 1):
        char = chr(char)
        for color in ("gray", "yellow", "green"):
            create_jpg(f"data/font/{char}_{color}.jpg", f"{char}", color, ("consolas", 25))


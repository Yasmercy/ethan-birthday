from enum import Enum, auto
from letter import Letter

class Mode(Enum):
    FAST = auto()
    NORMAL = auto()

# animations
# returns a callable that takes in a start time (from time.perf_counter())

def letter_emphasis(letter, mode):
    """ 
    Takes in a letter object and a speed mode
    Returns a callable that takes in a start time
    When called, will adjust the size of the letter 
        for an emphasis
    This is used for updating the text on a letter
    """

def flip_letter(letter, color, mode):
    """ Flips letter out, then sets color, then flip it back in """
    flip_letter_out(letter, mode)(time.perf_counter())
    letter.set_color(color)
    flip_letter_in(letter, mode)(time.perf_counter())

def play_group(*animations, delays=None):
    """ Plays a group of animations """
    if delays is None: delays = [0] * len(animations) # set no delay as default
    # uses multiprocessing 

# helper functions
def delay_animation(animation, delay):
    """ Returns a new animation with a start delay """

def flip_letter_out(letter, mode):
    """
    Takes in a letter object and a speed mode
    Returns a callable that takes in a start time
    When called, will flip the letter (and become invisible) 
    This is used for updating the color on a letter
    """

def flip_letter_in(letter, mode):
    """
    Takes in a letter object and a speed mode
    Returns a callable that takes in a start time
    When called, will flip the letter (and become full size) 
    This is used for updating the color on a letter
        (should be called after flip_letter_out)
    """

from enum import Enum, auto
from letter import Letter
from aux import *
from bisect import bisect_left
import itertools as it
import math
import time

class Mode(Enum):
    SLOW = auto()
    FAST = auto()
    INSTANT = auto()

def time_settings(mode):
    """ Returns the duration and step_time for the mode """
    FRAMES = 45
    if mode is Mode.FAST:
        return (2 ** -2, 1/FRAMES)
    elif mode is Mode.SLOW:
        return (2 ** -1, 1/FRAMES)
    elif mode is Mode.INSTANT:
        return (0, 1/FRAMES)
    print("WARNING: RECEIVED UNKNOWN MODE", mode)

class Animation:
    __slots__ = ("key_frames", "cur_frame", "func")

    def __init__(self, key_frames=None, func=None, *, cur_frame=0, **kwargs):
        self.cur_frame = cur_frame
        self.key_frames = key_frames
        self.func = func

    def __call__(self, time):
        """ Plays the animation if the current_time is on the next step """
        frame = self.time_to_frame(time)
        while frame > self.cur_frame:
            # call the function until match the step
            self.get_func()(time)
            self.cur_frame += 1

    def time_to_frame(self, time):
        """ Returns the current step that the animation is on """
        return bisect_left(self.key_frames, time, key=lambda x: x[0])

    def set_keyframes(self, start_time, end_time, step):
        """ Creates a list of tuple pairs for (time, func) """
        length = int((end_time - start_time) / step)
        self.key_frames = [(start_time + (step * index), self.func) for index in range(length)]
        self.key_frames.append((end_time, lambda _: self.func(end_time))) # ensure the final state 
        return self
    
    def delay(self, delay):
        self.key_frames = [
            (time + delay, func)
            for time, func in self.key_frames
        ]
        return self

    def get_func(self):
        return self.key_frames[self.cur_frame][1]
    
    def completed(self):
        return self.cur_frame == len(self.key_frames)

# animation methods
def create_animation_batch(*animations):
    """ Creates a group of animations """
    key_frames = merge(*(animation.key_frames for animation in animations))
    return Animation(key_frames=key_frames)

def play_animation(animation, sleep=0.005):
    while not animation.completed():
        animation(time.perf_counter())
        time.sleep(sleep)

def play_sequential(*animations, **kwargs):
    for animation in animations:
        play_animation(animation, **kwargs)

def play_wave(*animations, delay=1):
    # create animation group
    animations = [animation.delay(delay) for animation in animations]
    batch = create_animation_batch(*animations)
    play_animation(batch)

def play_simultaneous(*animations):
    play_wave(*animations, delay=0)

# individual animation factory functions
def letter_emphasis(letter, mode, start_time):
    """ 
    Takes in a letter object and a speed mode
    When called, will adjust the size of the letter 
        for an emphasis
    This is used for updating the text on a letter
    """

    AMPLITUDE = 0.25
    duration, step = time_settings(mode)
    end_time = start_time + duration
    def func(t):
        if duration == 0: return
        t = (t - start_time) / duration
        size_multipler = math.sin(2 * math.pi * t) * AMPLITUDE + 1
        letter.dilate(size_multipler)
    
    return Animation(func=func).set_keyframes(start_time=start_time, end_time=end_time, step=step)

def flip_letter_row(letters, colors, word, mode, start_time):
    """ Flips a list of letters with a desginated delay in between """
    wave_delay, _ = time_settings(mode) 
    animations = [flip_letter(letter, color, char, mode, start_time + wave_delay * index)
                  for index, (letter, color, char) in enumerate(zip(letters, colors, word))]
    return create_animation_batch(*animations)

def flip_letter_grid(letters_rows, colors_rows, words, mode, start_time):
    row_delay, _ = time_settings(mode)
    animations = [flip_letter_row(letters, colors, word, mode, start_time + index * row_delay)
                   for index, (letters, colors, word) in enumerate(zip(letters_rows, colors_rows, words))]
    return create_animation_batch(*animations)

def flip_letter(letter, color, char, mode, start_time):
    """ Creates an animation batch that: 
        flips letter out, then sets color, then flip it back in """
    duration, step = time_settings(mode)
    flip_out = flip_letter_out(letter, mode, start_time)
    color_change = change_letter(letter, color, char, start_time + duration / 2)
    flip_in = flip_letter_in(letter, mode, start_time + duration / 2)
    return create_animation_batch(flip_out, color_change, flip_in) 

# helper functions
def flip_letter_out(letter, mode, start_time):
    """
    Takes in a letter object and a speed mode
    When called, will flip the letter (and become invisible) 
    This is used for updating the color on a letter
    """
    
    duration, step = time_settings(mode)
    duration /= 2
    def func(t):
        if duration == 0: return
        t = (t - start_time) / duration
        size_multiplier = math.cos(math.pi * t) * 0.5 + 0.5
        letter.v_stretch(size_multiplier)

    return Animation(func=func).set_keyframes(start_time=start_time, end_time=start_time + duration, step=step)

def flip_letter_in(letter, mode, start_time):
    """
    Takes in a letter object and a speed mode
    When called, will flip the letter (and become full size) 
    This is used for updating the color on a letter
        (should be called after flip_letter_out)
    """
    
    duration, step = time_settings(mode)
    duration /= 2
    def func(t):
        if duration == 0: return
        t = (t - start_time) / duration
        size_multiplier = math.cos(math.pi * (t - 1)) * 0.5 + 0.5
        letter.v_stretch(size_multiplier)
    
    return Animation(func=func).set_keyframes(start_time=start_time, end_time=start_time + duration, step=step)

def change_letter(letter, color, char, time):
    return Animation(key_frames=[(time, lambda _: letter.set_letter_color(char, color))])

def merge(*arrs):
    arr = list(it.chain(*arrs))
    return sorted(arr, key=lambda x: x[0])


# reads in the file in fireworks and writes it to individual frames
import cv2

FIREWORKS_FOLDER_PATH = "data/fireworks"
FIREWORKS_FILENAME = f"{FIREWORKS_FOLDER_PATH}/fireworks.jpg"
IMAGE_WIDTH = -1
IMAGE_HEIGHT = -1
NUM_FRAMES = 5
NUM_ANIMATIONS = 4

def get_animation_y(animation):
    """ 
    animation: int
    returns a (int, int) tuple of the upper and lower bound of the image
    """
    
    lowers = [50, 290, 510, 760]
    uppers = [220, 460, 680, 930]
    return lowers[animation], uppers[animation]

def get_animation_x(frame):
    """ 
    frame: int
    returns a (int, int) tuple of the left and right bound of the image
    """
    
    lowers = [50, 210, 360, 565, 735, 980]
    uppers = [210, 360, 520, 725, 895, 1050]
    return lowers[frame], uppers[frame]

def write_animation_frame(animation, frame):
    """
    animation_number: int
    frame: int
    returns: void

    writes to a file in the fireworks folder in the format of
        animation{animation}{frame}.jpg
    """
    
    im = cv2.imread(FIREWORKS_FILENAME)
    x0, x1, y0, y1 = *get_animation_x(frame), *get_animation_y(animation)
    cropped = im[y0:y1, x0:x1]

    outfile = f"{FIREWORKS_FOLDER_PATH}/animation{animation}{frame}.jpg"
    cv2.imwrite(outfile, cropped)

# helpers
def set_image_dimensions():
    """ Sets the IMAGE_WIDTH/HEIGHT global variables """
    global IMAGE_WIDTH, IMAGE_HEIGHT
    IMAGE_WIDTH, IMAGE_HEIGHT, _ = cv2.imread(FIREWORKS_FILENAME).shape

# driver
def main():
    set_image_dimensions()
    for animation in range(NUM_ANIMATIONS):
        for frame in range(NUM_FRAMES):
            write_animation_frame(animation, frame)
    
if __name__ == "__main__":
    main()

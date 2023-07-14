# reads in the file in fireworks and writes it to individual frames
import cv2
import numpy as np

# const global variables
FIREWORKS_FOLDER_PATH = "data/fireworks"
FIREWORKS_FILENAME = f"{FIREWORKS_FOLDER_PATH}/fireworks.mp4"
FRAMES_PER_SECOND = 15
# mutable global variables
CURRENT_FRAME = 0

# functions
def load_video():
    """ returns a cv2 video object """
    return cv2.VideoCapture(FIREWORKS_FILENAME)

def black_to_white(frame):
    """ changes all (0, 0, 0) to (255, 255, 255) """
    WHITE = (255, 255, 255)
    BLACK = (25, 25, 25)
    black = (frame[:, :, 0] + frame[:, :, 1] + frame[:, :, 2]) < sum(BLACK)
    frame[black] = np.array(WHITE)
    return frame

def write_frame(vid):
    """ writes the current frame of the video as a jpg"""
    global CURRENT_FRAME

    # reading the frame
    _, frame = vid.read()
    # processing the frame
    frame = black_to_white(frame)
    # writing the frame
    filename = f"{FIREWORKS_FOLDER_PATH}/frame_{CURRENT_FRAME}.jpg"
    cv2.imwrite(filename, frame)
    # updating vars
    CURRENT_FRAME += 1

def increment_video(vid):
    """ goes to the next frame in the video """
    time = CURRENT_FRAME / FRAMES_PER_SECOND
    video_frame = time * vid.get(cv2.CAP_PROP_FPS)
    vid.set(cv2.CAP_PROP_POS_FRAMES, video_frame)

def write_video():
    """ writes all the frames of a video """
    vid = load_video()
    time = vid.get(cv2.CAP_PROP_FRAME_COUNT) / vid.get(cv2.CAP_PROP_FPS)
    num_write_frames = int(time * FRAMES_PER_SECOND)

    for _ in range(num_write_frames):
        write_frame(vid)
        increment_video(vid)

# driver
def main():
    write_video()
    
if __name__ == "__main__":
    main()

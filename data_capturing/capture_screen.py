from PIL import ImageGrab
import numpy as np
import cv2
import time

# This disables annoying DPI scaling
from ctypes import windll
windll.user32.SetProcessDPIAware()


def display_pixelated(img, scale=5, label=''):
    img = cv2.resize(img, (img.shape[1] * scale, img.shape[0] * scale), interpolation=cv2.INTERSECT_NONE)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow(label, img)

# [width, height] this is not by the opencv convention [height, width, channels]
screen = (1920, 1080)
center_area_size = (200, 200)
map_size = (150, 150)

# [x, y, width, height]
score_area = (screen[0] - 100, 40, 100, 220)


while True:
    last = time.time()
    
    img = np.array(ImageGrab.grab(bbox=(0, 0, screen[0], screen[1])))
    img_screen = cv2.resize(img, (screen[0] // 10, screen[1] // 10))
    
    img_center = img[img.shape[0] // 2 - center_area_size[1] // 2 : img.shape[0] // 2 + center_area_size[1] // 2,
                     img.shape[1] // 2 - center_area_size[0] // 2 : img.shape[1] // 2 + center_area_size[0] // 2]
    img_center = cv2.resize(img_center, (img_center.shape[1] // 4, img_center.shape[0] // 4))
    
    img_map = img[img.shape[0] - map_size[1] : img.shape[0],
                  img.shape[1] - map_size[0] : img.shape[1]]
    
    img_score = img[score_area[1] : score_area[1] + score_area[3],
                    score_area[0] : score_area[0] + score_area[2]]
    img_score = cv2.resize(img_score, (img_score.shape[1], img_score.shape[0]))

    
    display_pixelated(img_screen, label='screen')
    display_pixelated(img_center, label='center')
    display_pixelated(img_map, label='map')
    display_pixelated(img_score, label='score', scale=4)

    cv2.waitKey(1)
    print(1 / (time.time() - last))
    
cv2.destroyAllWindows()
from cv2 import cvtColor, COLOR_BGRA2RGB
from numpy import array
from torch.hub import load
from mss import mss
from pyautogui import size
from math import sqrt

model = load('', 'custom', path='best.pt', source='local')
screen = mss()

scale = int(input("Scale: "))

scx, scy = int(size()[0]/2), int(size()[1]/2-8)

monitor = {"top": scy-scale, "left": scx-scale, "width": scale*2, "height": scale*2}

while True:
    frame = array(screen.grab(monitor))
    frame = cvtColor(frame, COLOR_BGRA2RGB)

    results = model(frame)


    closest_distance = float('inf')
    closest_box = None

    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        x1 += monitor["left"]
        y1 += monitor["top"]
        x2 += monitor["left"]
        y2 += monitor["top"]

        center_x = (x1 + x2) /  2
        center_y = (y1 + y2) /  2

        for *box, conf, cls in results.xyxy[0]:
            distance = sqrt((center_x - scx)**2 + (center_y - scy)**2)
            if distance < closest_distance:
                closest_distance = distance
                closest_box = (x1, y1, x2, y2)
        
        print(closest_box)
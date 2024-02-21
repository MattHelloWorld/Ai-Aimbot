from cv2 import cvtColor, COLOR_BGRA2RGB
from numpy import array
from torch.hub import load
from mss import mss
from win32api import GetSystemMetrics, mouse_event
from win32con import MOUSEEVENTF_MOVE
from tkinter import Canvas, Tk
from pyautogui import size
from math import sqrt

model = load('', 'custom', path='best.pt', source='local')
screen = mss()

scale = int(input("Scale: "))
confidence = 50
linearSmooth = int(input("Speed: "))

scx, scy = int(size()[0]/2), int(size()[1]/2-8)

monitor = {"top": scy-scale, "left": scx-scale, "width": scale*2, "height": scale*2}

def createWindow():
    Width = GetSystemMetrics(0)
    Height = GetSystemMetrics(1)
    root = Tk()
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-toolwindow", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", '#000000')
    root.geometry(f"{Width}x{Height}")
    
    window = Canvas(root, width=Width, height=Height, bg='#000000')
    window.pack()
    return window

def drawBox(window, x1, y1, x2, y2, color):
    window.create_line(x1, y1, x2, y1, fill=color)
    window.create_line(x2, y1, x2, y2, fill=color)
    window.create_line(x2, y2, x1, y2, fill=color)
    window.create_line(x1, y2, x1, y1, fill=color)

def clearWindow(window):
    window.delete("all")

window1 = createWindow()
window2 = createWindow()
active_window = window1

while True:
    frame = array(screen.grab(monitor))
    frame = cvtColor(frame, COLOR_BGRA2RGB)

    results = model(frame)


    closest_distance = float('inf')  # Initialize the closest distance to infinity
    closest_box = None  # Initialize the closest box to None

    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        x1 += monitor["left"]
        y1 += monitor["top"]
        x2 += monitor["left"]
        y2 += monitor["top"]

        # Calculate the center of the bounding box
        center_x = (x1 + x2) /  2
        center_y = (y1 + y2) /  2

        # Calculate the Euclidean distance between the center of the bounding box and scx, scy
        for *box, conf, cls in results.xyxy[0]:
            distance = sqrt((center_x - scx)**2 + (center_y - scy)**2)

            # If this distance is smaller than the closest distance found so far, update closestX, closestY, and closest_distance
            if distance < closest_distance:
                closest_distance = distance
                closest_box = (x1, y1, x2, y2)
    
    if closest_box is not None:
        mouse_event(MOUSEEVENTF_MOVE, linearSmooth if (closest_box[0]+closest_box[2])/2 > scx else -linearSmooth, linearSmooth if (closest_box[1]+closest_box[3])/2 > scy else -linearSmooth,0,0)
    if closest_box:
        drawBox(active_window, closest_box[0], closest_box[1], closest_box[2], closest_box[3], "#FF0000")
    drawBox(active_window, scx-scale, scy-scale, scx+scale, scy+scale, "#FFFFFF")
    active_window.update()
    inactive_window = window2 if active_window == window1 else window1
    clearWindow(inactive_window)
    active_window, inactive_window = inactive_window, active_window
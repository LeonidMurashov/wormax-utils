import win32api as wapi
import time
import win32con

keyList = ['\b']
for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890':
    keyList.append(char)

def get_keys():
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)

    if wapi.GetAsyncKeyState(win32con.VK_MENU):
        keys.append('ALT')        
    if wapi.GetAsyncKeyState(win32con.VK_LEFT):
        keys.append('LEFT')
    if wapi.GetAsyncKeyState(win32con.VK_RIGHT):
        keys.append('RIGHT')
    if wapi.GetAsyncKeyState(win32con.VK_UP):
        keys.append('UP')
    return keys


import time
import numpy as np
from threading import Thread
from pynput.mouse import Listener
from functools import partial
import os
import win32api
import colorama

FPS = 30
save_batch_size = 6000 # 2000 - save every minute (30 FPS)
data_path = 'data'


isPressed = False
def on_click(x, y, button, pressed):
    global isPressed
    isPressed = pressed

def detect_clicks():
    with Listener(on_click=partial(on_click)) as listener:
        listener.join()


def main():
    print('Программа для записи действий в игре wormax.io.')
    print('Версия 2.')


    if not os.path.exists(data_path):
        os.mkdir(data_path)

    # New thread for click detecting
    thread = Thread(target=detect_clicks)
    thread.start()


    # Check for wrong DPI scaling or resolution
    if not (win32api.GetSystemMetrics(0) == 1920 and win32api.GetSystemMetrics(1) == 1080):
        colorama.init()
        print('\033[91m' + 'Программа поддерживает запись только в разрешении 1920х1080 с настройкой DPI scaling в Windows на 100%.' + '\033[0m')
        time.sleep(5)
        return


    print('Запись мыши и клавиатуры...')
    while True:
        data = np.zeros((save_batch_size, 11))
        for i in range(save_batch_size):
            keys = get_keys()
            x, y = win32api.GetCursorPos()
            data[i] = np.array([x, 
                                y, 
                                isPressed,
                                *[key in keys for key in ['Q', 'W', 'E', ' ', 'UP', 'RIGHT', 'LEFT']],
                                time.time()])
            time.sleep(1 / FPS)
        path = os.path.join(data_path, f'mouse-keys-{int(data[0][-1])}-{int(data[-1][-1])}.npy')
        np.save(path, data)
        print('Saved:', path)


if __name__ == '__main__':
    try: 
        main()
        os._exit(0)
    except KeyboardInterrupt:
        print('Interrupted')
        os._exit(0)

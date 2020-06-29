import time
import win32api
import obspython as obs
import win32con
import numpy as np
from threading import Thread
from pynput.mouse import Listener
from functools import partial
import os


save_period = 3
frames_per_minute = 30 * 60 # (30 FPS)
save_batch_size = frames_per_minute * save_period 
data_folder = 'D:/Wormax/data'


isPressed = False
def on_click(x, y, button, pressed):
    global isPressed
    isPressed = pressed

def detect_clicks():
    with Listener(on_click=partial(on_click)) as listener:
        listener.join()


keyList = ['\b']
for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890':
    keyList.append(char)

def get_keys():
    keys = []
    for key in keyList:
        if win32api.GetAsyncKeyState(ord(key)):
            keys.append(key)

    if win32api.GetAsyncKeyState(win32con.VK_MENU):
        keys.append('ALT')        
    if win32api.GetAsyncKeyState(win32con.VK_LEFT):
        keys.append('LEFT')
    if win32api.GetAsyncKeyState(win32con.VK_RIGHT):
        keys.append('RIGHT')
    if win32api.GetAsyncKeyState(win32con.VK_UP):
        keys.append('UP')
    return keys


class ControlsRecorder:
    def __init__(self):

        # New thread for click detecting
        thread = Thread(target=detect_clicks)
        thread.start()

    def start_recording(self):
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        self.data_batch = np.zeros((save_batch_size, 11))
        self.current_batch_size = 0
        self.recording_start_time = time.time()

        # Emptying buffer before recording
        get_keys()

    def stop_recording(self):
        self.save_batch()

        # Write metadata to metadata file
        with open(os.path.join(data_folder, 'metadata.txt'), 'a') as file:
            file.write(f'{self.recording_start_time}\n')

    def next_frame(self):
        keys = get_keys()
        x, y = win32api.GetCursorPos()
        self.data_batch[self.current_batch_size] = np.array(
                           [x, 
                            y, 
                            isPressed,
                            *[key in keys for key in ['Q', 'W', 'E', ' ', 'UP', 'RIGHT', 'LEFT']],
                            time.time()])

        self.current_batch_size += 1

        if self.current_batch_size >= save_batch_size:
            self.save_batch()

    def save_batch(self):
        to_save = self.data_batch[:self.current_batch_size]
        path = os.path.join(data_folder, f'mouse-keys-{int(to_save[0][-1])}-{int(to_save[-1][-1])}.npy')
        np.save(path, to_save)
        self.current_batch_size = 0
        print('Saved:', path)


####### OBS stuff ##########


recording_on = False
controls_recorder = ControlsRecorder()


def cb_recording_starting(callback_data):
    global recording_on

    print('Starting')
    controls_recorder.start_recording()
    recording_on = True
    return True


def cb_recording_stop(callback_data):
    global recording_on

    print('Stop')
    recording_on = False
    controls_recorder.stop_recording()
    return True


# This function is called every frame by OBS studio
def script_tick(seconds):
    if recording_on:
        controls_recorder.next_frame()


def script_load(settings):
    # Check for wrong DPI scaling or resolution # This warning doen't really work if DPI scaling is off
    if not (win32api.GetSystemMetrics(0) == 1920 and win32api.GetSystemMetrics(1) == 1080): 
        raise Exception('Ошибка! Программа поддерживает запись только в разрешении 1920х1080 с настройкой DPI scaling в Windows на 100%.')

    recording_signal_handler = obs.obs_output_get_signal_handler(obs.obs_frontend_get_recording_output())
    obs.signal_handler_connect(recording_signal_handler, "starting", cb_recording_starting)
    obs.signal_handler_connect(recording_signal_handler, "stop", cb_recording_stop)

    print('Script loaded')


def script_description():
    return 'Этот скрипт записывает действия мыши и клавиатуры для wormax.io.\nВерсия 4.'


def script_update(settings):
    global data_folder, save_period, save_batch_size
    data_folder = obs.obs_data_get_string(settings, 'data folder')
    save_period = obs.obs_data_get_int(settings, 'save period')
    save_batch_size = frames_per_minute * save_period 


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "data folder", data_folder)
    obs.obs_data_set_default_int(settings, "save period", save_period)


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "data folder", "Data folder", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "save period", "Save period (minutes)", 1, 20, 1)

    return props

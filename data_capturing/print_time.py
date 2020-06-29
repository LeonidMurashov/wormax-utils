import time
import datetime

from pynput.keyboard import Key, Controller

keyboard = Controller()

# for i in [Key.cmd_l, Key.alt, 'r']:
#     keyboard.press(i)    
# for i in [Key.cmd_l, Key.alt, 'r']:
#     keyboard.release(i)

while True:
	tm = round(time.time(), 5)
	print('time:', tm)#datetime.datetime.utcfromtimestamp(tm).strftime('%Y-%m-%d "%H:%M:%S.%f"'))
	time.sleep(0.01)
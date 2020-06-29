import os
import datetime

video_path = input('Input path to file: ')
unix_time = os.path.getctime(video_path)
converted = datetime.datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d "%H:%M:%S.%f"')

print(unix_time)
print(converted)
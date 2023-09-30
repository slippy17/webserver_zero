## Convert list of commands to IR codes
## send using 'pioneer or yamaha module built with 'IRSlinger'.
import os
import json
import time


def send_code(commands):
	with open("../static/p_codes.json", "r") as infile:
		cd_player = json.load(infile)
	for command in commands:
            yam = False
            code = (cd_player[command])
            if code[:2] == '5E': yam = True
            raw = bin(int(code, 16))[2:].zfill(32)
            if command == 'Play':
                time.sleep(8)
            print (command, code, raw)
            if gpio_avail :
                if yam:
                    os.system("sudo ./yamaha "+ raw)
                else:
                    os.system("sudo ./pioneer "+ raw)
                    print ('Pioneer code')
            if yam:
                print ('Yamaha code')
            else: print ('Pioneer code')
            time.sleep(0.6)
	return

gpio_avail = bool(int(input('GPIO 1/0 ')))
print(gpio_avail)

while True:
    com = input('Type command ')
    
    send_code([com])


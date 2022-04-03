import os
import time
import json

def send_code(code):
    raw = bin(int(code, 16))[2:].zfill(32)
    os.system("sudo ./pioneer "+ raw)
    return raw

try:
	with open('p_codes.json') as file:
		cd_player = json.load(file)
except:
	print('Codes loading failure')

code = (cd_player['Disc'])


print (code)

while True:
    print(send_code(code))
    print("\n send code")
    time.sleep(10)


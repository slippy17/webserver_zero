
from threading import Event, Thread
from flask import Flask, render_template, request, jsonify
import json
import time 
import os
import pandas as pd
import playtime as pt  ## Custom timer module for Play, Pause and Stop functions.

#### Environment variables.
## Used to autoset options if testing on laptop or running on Raspberr Pi.

ip_addr= os.environ['IP_ADDRESS']

gpio_avail= eval(os.environ['GPIO_AVAIL'])

bug = not gpio_avail ## debug mode off when running on Raspi.

print (f"IP ADDRESS {ip_addr} GPIO_AVAIL is {gpio_avail}")

if gpio_avail : os.system("sudo ./ledON")


class Juke():
    ### Juke class to keep time based on song length. Play, Pause, Stop and report status.

    playtimer = pt.Tmr()

    def __init__(self):
        self.is_playing = 0
        self.cur_disc = 40
        self.cur_track = 1
        self.cur_art = "No Artist" ## not used
        self.cur_song_title = ""
        self.song_len = 0
        self.end = 0        ## Not used. Time that songs ends.

    def call_repeatedly(self,interval, func, *args):
        stopped = Event()
        def loop():
            while not stopped.wait(interval): # the first call is in `interval` secs
                func(*args)
        Thread(target=loop).start()
        return stopped.set


    def play(self, disc_indx, track):
        self.cur_disc = disc_indx
        self.cur_track = track
        self.is_playing = 1

        x = self.df[(self.df["Disc_ID"] == self.cur_disc) & (self.df["Track_ID"] == self.cur_track)]
        self.song_len = int(x.Length/1000) - 4
        self.cur_art = x.Artist.to_string(index=False)
        self.cur_song_title = x.Song_Title.to_string(index=False)
        # print(self.cur_art)

        print(x.to_string())

        Juke.playtimer.run(self.song_len)
        self.cancel_future_calls = self.call_repeatedly(5, self.check_timer)

        return 'Playing', self.song_len


    def check_timer(self):
        if (Juke.playtimer.remaining <= 0 and self.is_playing == 1):
            self.stop()
            return
        return


    def pause(self):
        if self.is_playing == 1:
            self.is_playing = -1
            Juke.playtimer.pause()
            send_code(['Pause'])
            return self.is_playing, Juke.playtimer.remaining

        if self.is_playing == -1:
            self.is_playing = 1
            Juke.playtimer.resume()
            send_code(['Resume'])
            return self.is_playing

        return self.is_playing


    def stop(self):
        self.is_playing = 0
        self.song_len = 0
        self.cur_art = "No Artist"
        self.cur_song_title = ""
        self.cancel_future_calls()
        send_code(['Stop'])
        return 'Stop'

    def status(self):
        message = {}
        message['disk'] = self.cur_disc
        message['song'] = self.cur_track
        message['length']= self.song_len
        message['time'] = Juke.playtimer.elap
        message['is_playing'] = self.is_playing
        message['artist'] = self.cur_art
        message['s_title'] = self.cur_song_title
        # artist = self.df[(self.df["Disc_ID"] == self.cur_disc) & (self.df["Track_ID"] == self.cur_track)]

        # print (artist.Artist.to_string(), artist.Song_Title.to_string())
        return message

    ## Load database from .json file. Not used since dataframe introduced,
    def load(self):
    	with open("./static/cd_database.json", "r") as infile:
            self.cddb = json.load(infile)
            return

    ## Load DB from dataframe pickel file. Also create a album dataframe (adf) map cd>>slot.
    def load_df(self):
        self.df= pd.read_pickle("./static/cd_database.pkl")
        self.df.Length = self.df.Length.astype('int32')
        self.df.Disc_ID = self.df.Disc_ID.astype('int')
        self.adf= self.df[['Album', 'Disc_ID', 'Artist']].copy()
        self.adf= self.adf.drop_duplicates(subset=['Album'], ignore_index=True)
        return

    def album_stats_df(self,index_no):  ## ************** TESTED ************
        check = (self.adf.index ==index_no).any()
        if check==False:
            print('Disk Index Excceded')
            index_no = index_no-1
        db = self.adf.loc[index_no]
        d_id = db.Disc_ID
        tracks_df = self.df[self.df["Disc_ID"] == d_id]
        tracks_df = tracks_df.sort_values(by=['Track_ID'], ignore_index=True)
           ## Album info for the album at that Disc_ID.
        tracks = tracks_df.Song_Title.count()   ## The number 0f tracks in the album
        return tracks_df

    def search_DB(self,input):
        result = self.df[(self.df["Song_Title"].str.contains(input, case= False, regex=False))  |
                (self.df["Album"].str.contains(input, case= False, regex=False))  |
                (self.df["Artist"].str.contains(input, case= False, regex=False)) ]

        return result


app = Flask(__name__)

player = Juke()
#player.load()
player.load_df()

## Convert list of commands to IR codes and send using 'pioneer module built with 'IRSlinger'.
def send_code(commands):
	with open("./static/p_codes.json", "r") as infile:
		cd_player = json.load(infile)
	for command in commands:
            code = (cd_player[command])
            raw = bin(int(code, 16))[2:].zfill(32)
            if command == 'Play':
                time.sleep(8)
            print (command, code)
            if gpio_avail : os.system("sudo ./pioneer "+ raw)
            time.sleep(0.6)
	return


## Build command sequence to play a song based on disk and track number.
def command_builder(s_cd, s_track):
    c_builder = ['Pause']

    if (int(s_cd)>100) or (len(s_track)>2):
        print("Error in the length of numbers")

    a1= s_cd[0]
    c_builder.append(a1)

    if len(s_cd) == 2:
        a2= s_cd[1]
        c_builder.append(a2)

    if len(s_cd) == 3:
        a2= s_cd[1]
        c_builder.append(a2)
        a3 = s_cd[2]
        c_builder.append(a3)

    c_builder.append('Disc')
    b1= s_track[0]
    c_builder.append(b1)
    if len(s_track) == 2:
        b2= s_track[1]
        c_builder.append(b2)
    c_builder.append('Track')

    c_builder.append('Play')
    return c_builder



@app.route('/stat', methods=['POST', 'GET'])
def init():
	if gpio_avail : os.system("sudo ./ledOFF")
	stat = player.status()
	if gpio_avail : os.system("sudo ./ledON")
	return jsonify(stat)  # serialize and use JSON headers



@app.route('/pause', methods=['GET'])
def  pause_request():
    message = player.pause()
    return jsonify(message)  # serialize and use JSON headers



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search')   # /<query> removed from url.
def search():
    return render_template('search.html')

@app.route('/searchDB/<query>', methods=['GET'])
def search_DB(query):                     # query removed from function.
    result = player.search_DB(query)
    result = result.to_dict(orient="index")
    ##sname=render_template(request.args['sname'])
    ##print(result)
    return jsonify(result)

@app.route('/loadDatabase/<index_no>', methods=['GET','POST'])
def load_DB(index_no):
	index_no = int(index_no)
	data = player.album_stats_df(index_no) ## changed from .ablum_stats

	data = data.to_dict( orient="records")

	return jsonify(data)

##@app.route('/requestSong/<s_cd>/<s_track>', methods=['POST','GET'])
@app.route('/requestSong/', methods=['POST'])
def requestSong():
	if request.method == 'POST':

		data = request.json
		s_idx = data['Index']
		print(data)
## request song from search page is disk slot+100, request otherwise is alpha index. 
	if (s_idx > 100):
		sel_cd = str(s_idx-100)
	else:
		sel_cd = str(player.adf.loc[s_idx].Disc_ID) 
            ## Lookup the Disc_ID from that Index.

	sel_track = str(data['Song']+1)

	command_list = command_builder(sel_cd, sel_track)
	send_code(command_list)

	player.play(int(sel_cd), int(sel_track))

	return '200'



if __name__=="__main__":
	app.run(debug=bug, host=ip_addr)
	

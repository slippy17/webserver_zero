# Scrap code to verify JSON cd data format and convert to dataframe.

import json
import pandas as pd

def read():
		try:
			with open("cd_database.json", "r") as infile:
				cddb = json.load(infile)
				return cddb
			    
			    
		except:
                            print("There was a problem reading database!!")
                            return
                        
##### ***************** Code below takes json database and converts to df dataframe   *********** ####################
                        
disc_id = '1'
track = 11

def db_to_df():
    
    json_formatted = read()

    df = pd.DataFrame(columns= ['Disc_ID', 'Artist', 'Album', 'Track_ID', 'Song_Title', 'Length'])

    for disc_id in range(1,100):
        id = str(disc_id)
        if json_formatted[id] == None:
            break
        num_tracks = json_formatted[id]['disc']['release-list'][0]['medium-list'][0]['track-count']
    
        for track in range(0,num_tracks,1):
            song = json_formatted[id]['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['title']
            artist = json_formatted[id]["disc"]["release-list"][0]["artist-credit-phrase"]
            album = json_formatted[id]['disc']['release-list'][0]['title']
            length = json_formatted[id]['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['length']
        
            s_row = pd.Series([id, artist, album, track+1, song, length], index=df.columns)
            df= df.append(s_row, ignore_index=True)
            #print (f'Disk ID:{id} Artist:{artist} Album:{album} Track_ID:{track+1} Song {song} Length:{length}')
    return df
    
df = db_to_df()
        
##### ***************** Code above takes json database and converts to df dataframe   *********** ####################
        

#df= pd.read_pickle("cd_database.pkl") ## reads pickle already created by code above.

#####  sort and format the data.
df = df.sort_values(by=['Artist', 'Album'], ignore_index=True) #df sorted by artist
df['Disc_ID'] = df['Disc_ID'].astype(int)
#subset of albums and disc_ID with duplicate albums dropped.
album_df = df[['Album', 'Disc_ID', 'Artist']].copy()
album_df=album_df.drop_duplicates(subset=['Album'], ignore_index=True)

##data = df.query('Disc_ID=="58"')

#print(df.sort_values(by=['Album']))

#print(df[df["Song_Title"] == "Airbag"])

#print(df[df["Album"] == "Airbag / How Am I Driving?"])



## a =  df[(df["Album"] != "Airbag / How Am I Driving?") & (df["Artist"] == "Radiohead")]
## find rows with Album <> "Airbag" and Artist equals "Radiohead".


#df.to_pickle("cd_database.pkl")

# #album_df.to_pickle("album_df.pkl")
## ******** Code above already created a pickle file. Note: The format has been sorted in previous code and two dataframes and pickel files created.

# df['Disc_ID'] = df['Disc_ID'].astype(int)


def album_stats(index_no):
    db = album_df.loc[index_no]
    message = []
    #message is a list with element 0 num of tracks, element 1 list of tracks, element2 artistname, element 3 album
    #tracks = db['medium-list'][0]['track-count']
    #track_list = db['medium-list'][0]['track-list']
    
    artist =  db.Artist
    album = db.Album
    d_id = db.Disc_ID
    tracks_df = df[df["Disc_ID"] == d_id]   ## Album info for the album at that Disc_ID.
    tracks = tracks_df.Song_Title.count()   ## The number 0f tracks in the album
    
    result = tracks_df.to_json(orient="records")
    parsed = json.loads(result)
    #print (json.dumps(parsed, indent=4))    
    #print(result)
    
    #message.append({'tracks':tracks})
    message.append(tracks_df)
    #message.append({'artistname':artist})
    #message.append({'album':album})
    return tracks_df



##
##result = df.to_json(orient="split")
##
##parsed = json.loads(result)
##
##json.dumps(parsed, indent=4)
##

# df[(df["Disc_ID"] == 65) & (df["Track_ID"] == 1)].Length

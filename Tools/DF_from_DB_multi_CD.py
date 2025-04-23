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
    
    cd = 0 ## for tracking multi disc albums
    
    

    for disc_id in range(1,100):
        id = str(disc_id)
        
        if id == '22': cd = 1   ## 22 Tom Dunne Hack. Get CD2 tracklist
        
        if json_formatted[id] == None:
            break
        
        num_tracks = json_formatted[id]['disc']['release-list'][0]['medium-list'][cd]['track-count']
        multi_album = len(json_formatted[id]['disc']['release-list'][0]['medium-list'])-1 ##num of disks on a multi-album
        #print (multi_album)
    
        for track in range(0,num_tracks,1):
            song = json_formatted[id]['disc']['release-list'][0]['medium-list'][cd]['track-list'][track]['recording']['title']
            artist = json_formatted[id]["disc"]["release-list"][0]["artist-credit-phrase"]
            album = json_formatted[id]['disc']['release-list'][0]['title']
            length = json_formatted[id]['disc']['release-list'][0]['medium-list'][cd]['track-list'][track]['recording']['length']
            
            if multi_album: album = album + " "+ str(cd+1) # add a 1 or 2 to the Album title.
        
            s_row = pd.Series([id, artist, album, track+1, song, length], index=df.columns)
            df= df.append(s_row, ignore_index=True)
            #print (f'Disk ID:{id} Artist:{artist} Album:{album} Track_ID:{track+1} Song {song} Length:{length}')
        #is_double_album = len(json_formatted[id]['disc']['release-list'][0]['medium-list'])-1 # set cd variable to pick cd 1 or cd 2 track list.
        if (multi_album) :
            if (cd==multi_album):
                cd=0
            else:
                cd=cd+1
        
        if id == '52': cd = 0 ## 22 Tom Dunne and 52 REM double albums with no disc 2 (lost). Haha hack!!
                
        
    return df
  
  
 #**************************************************** 
df = db_to_df() ##Call function to create df ##*********************>>>>>>>>>>>>>>
        
##### ***************** Code above takes json database and converts to df dataframe   *********** ####################
        


#****************************************************
#df= pd.read_pickle("cd_database.pkl") ## reads pickle already created by code above. **************>>>>>>>>>>>>

#####  sort and format the data.
df = df.sort_values(by=['Artist', 'Album'], ignore_index=True) #df sorted by artist
df['Disc_ID'] = df['Disc_ID'].astype(int)
df['Artist'] = df['Artist'].map(str)
#df['Album'] = df['Album'].map(str)


#subset of albums and disc_ID with duplicate albums dropped.
album_df = df[['Album', 'Disc_ID', 'Artist']].copy()
album_df=album_df.drop_duplicates(subset=['Album'], ignore_index=True)

##data = df.query('Disc_ID=="58"')

#print(df.sort_values(by=['Album']))

#print(df[df["Song_Title"] == "Airbag"])

#print(df[df["Album"] == "Airbag / How Am I Driving?"])



## a =  df[(df["Album"] != "Airbag / How Am I Driving?") & (df["Artist"] == "Radiohead")]
## find rows with Album <> "Airbag" and Artist equals "Radiohead".




# #album_df.to_pickle("album_df.pkl")
## ******** Code above already created a pickle file. Note: The format has been sorted in previous code and two dataframes and pickel files created.

# df['Disc_ID'] = df['Disc_ID'].astype(int)


def album_stats(index_no):
    try:
        db = album_df.loc[index_no]
    except:
        print(f'Index {index_no} not returned from database')
        return 
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

def search_song(song):
    result = df[df["Song_Title"].str.contains(song, case= False, regex=False)]  ##df[df["Song_Title"] == song]
    
    return result

def search_album(album):
    result = album_df[album_df["Album"].str.contains(album, case= False, regex=False)]  ##df[df["Song_Title"] == song]
    
    return result

def search_artist(artist):
    result = album_df[album_df["Artist"].str.contains(artist, case= False, regex=False)]  ##df[df["Song_Title"] == song]
    
    return result

def compound_search(input):
    
    result = df[(df["Song_Title"].str.contains(input, case= False, regex=False))  |
                (df["Album"].str.contains(input, case= False, regex=False))  |
                (df["Artist"].str.contains(input, case= False, regex=False)) ]

    return result

def update_artist(dfIndex, artist):
    ### This function will update Artist at a given Index. It can be used to update where artist name in completation CD tags as Various
    df.loc[dfIndex, "Artist"] = artist
    return
    

a = compound_search('Mellon').to_string()

print(a)

#Some Artist changes from Various.
#update_artist(1136, "Rick Astley")
##update_artist(1001, "Radiohead")
##update_artist(1048, "Groove Armada")
##update_artist(1066, "The Sultans Of Ping")
##update_artist(1060, "The Stunning")
##update_artist(1056, "A House")
##update_artist(1059, "An Emotional Fish")








#****************** Write to Pickle ************************
#df.to_pickle("cd_database.pkl")  # *************************
#****************** uncomment to use ************************




##with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.precision', 3):
##print(a.to_markdown())
#print(f"{Art} {Alb} {Sng}")
##result = df.to_json(orient="split")
##
##parsed = json.loads(result)
##
##json.dumps(parsed, indent=4)
##

# df[(df["Disc_ID"] == 65) & (df["Track_ID"] == 1)].Length


## Change Artist for index num   df.loc[1001, "Artist"] = "Radiohead"



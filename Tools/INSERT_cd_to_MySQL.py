import discid
import musicbrainzngs
import pandas as pd
from sqlalchemy import create_engine, text, event
##############################################################################
## Algorithm                                                                
## 1) Get CD info from MusicBrainzngs.
## 2) Check if artist exists in artists table.
## 3) INSERT artist into artists table if not already there.
## 4) Get artist ID
## 5) Check if album exists in album table against that artist ID.
## 6) INSERT album with artist ID into albums table if not already there.
## 7) Get album ID
## 8) INSERT tracks with album ID into tracks table
## 9) Perform steps 5 to 8 for multiple CD albums. 

# -----------------------------
# Database connection
# -----------------------------
#engine = create_engine("mysql+pymysql://root:123@192.168.0.115/cddb", echo=False)
engine = create_engine(
    "mysql+pymysql://root:123@192.168.0.115/cddb?charset=utf8mb4", echo=False
)

@event.listens_for(engine, "connect")
def set_utf8mb4(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET character_set_connection = utf8mb4")
    cursor.execute("SET character_set_client = utf8mb4")
    cursor.execute("SET character_set_results = utf8mb4")
    cursor.close()


# -----------------------------
# Initialize MusicBrainz user agent
musicbrainzngs.set_useragent("python-discid-example", "0.1", "your@mail")

def fetch_cd_metadata():
    try:
        disc = discid.read()
        print(f"Disc ID: {disc.id}")
        cd_data = musicbrainzngs.get_releases_by_discid(disc.id, includes=["artists", "recordings"])
    except musicbrainzngs.ResponseError:
        print("Disc not found or bad response")
        return None
    
    is_multi = len(cd_data['disc']['release-list'][0]['medium-list']) ##num of disks on a multi-album
    cd_obj=[] 
    
    for cd in range(is_multi):
        if "disc" in cd_data:
            release = cd_data["disc"]["release-list"][0]
            artist_name = release['artist-credit-phrase']
            album_name = release['title']
            if is_multi>1: album_name = album_name + " "+ str(cd+1) # add a 1 or 2 etc to the Album title.
            tracks = release['medium-list'][cd]['track-list']
            print(f"CD Artist:\t{artist_name}")
            print(f"CD Album title:\t{album_name}\n")
            track_list=[]
            for track in tracks:
                song_title = track['recording']['title']
                length = int(track['recording'].get('length', 0))
                position = int(track['position'])
                #print (artist_name, album_name, position, song_title, length)
                track_list.append([position, song_title, length])
            cd_dict= {
                "album": album_name,
                "artist": artist_name,
                "tracks": track_list,
                "multi": is_multi
                }
            cd_obj.append(cd_dict)

            
        elif "cdstub" in cd_data:
            stub = cd_data["cdstub"]
            print(f"CD Stub Title:\t{stub.get('title', 'Unknown')}")
    
    return cd_obj

def check_artist(artist_name):
    query = "SELECT * FROM artists WHERE artist="+artist_name
    with engine.connect() as conn:
        result = conn.execute(text(query))
        output= result.all()
        if len(output):
            return output
        else:
            return -1
        
def insert_artist(artist_name):
    query = "INSERT INTO artists (artist) VALUES ("+artist_name+")"
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()
        return
    
def check_album(album_name):
    query = text("SELECT * FROM albums WHERE album_title= :title")
    with engine.connect() as conn:
        result = conn.execute(query, {"title":album_name})
        output= result.all()
        if len(output):
            return output
        else:
            return -1

# def insert_album(artist_id, album_title):
#     query = "INSERT INTO albums(artist_id,album_title,disc_id ) VALUES ("+artist_id+","+album_title+",16)"
#     with engine.connect() as conn:
#         conn.execute(text("SET NAMES utf8mb4"))
#         conn.execute(text(query))
#         conn.commit()
#         return
    
def insert_album(artist_id, album_title):
    album_title = album_title.replace("‐", "-")  # Replace U+2010 with ASCII hyphen
    query = text("""
        INSERT INTO albums (artist_id, album_title, disc_id)
        VALUES (:artist_id, :album_title, :disc_id)
    """)

    with engine.connect() as conn:
        # no need to do SET NAMES if engine charset is utf8mb4
        conn.execute(query, {
            "artist_id": artist_id,
            "album_title": album_title,
            "disc_id": 0
        })
        conn.commit()    
    
    

    
def insert_tracks(album_id, tracks):
    for track in tracks:
        song_title = track[1]
        song_title = song_title.replace("'", "")
        track_number, length = str(track[0]), str(track[2])
        query = "INSERT IGNORE INTO tracks(album_id,track_number,song_title, length_seconds ) VALUES ("+album_id+","+track_number+",'"+song_title+"',"+length+")"
        
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        print(query)
    return


## 1) Get CD info from MusicBrainzngs.
cd_info = fetch_cd_metadata()
num_cds = cd_info[0]['multi']

for cd in range (num_cds):

    artist_name =  "'"+cd_info[cd]['artist']+"'"
    album_name = cd_info[cd]['album']
    album_name = album_name.replace("‐", "-")  # Replace U+2010 with ASCII hyphen
    tracks = cd_info[cd]['tracks']
    ## 2) Check if artist exists in artists table.
    if check_artist(artist_name) == -1:
        print('Artist does not exist in artists table.')
        x = input(f'Would you like to add {artist_name} to the artists table? Y/N> ')
        if not x.lower()=='y':
            print("*** OK: artists table in database not changed ***")
            break
    ## 3) INSERT artist into artists table if not already there.
        insert_artist(artist_name)
        print(f"*** OK: artist {artist_name} added to artists table in database. ***")
    else: print("*** Artists exists in the artists table in database not changed ***")

    ## 4) Get artist ID
    art_info = check_artist(artist_name)
    artist_id = str(art_info[0][0])
    ##artist_name = art_info[0][1]
    
    ## 5) Check if album exsists in album table 
    album_info = check_album(album_name)
    if album_info == -1:
        print('Album does not exist in album table.')
        x = input(f'Would you like to add {album_name} to the albums table under Artist {artist_name}? Y/N> ')
        if not x.lower()=='y':
            print("*** OK albums table in database not changed ***\n")
            continue
## 6) INSERT album with artist ID into albums table if not already there.
        insert_album(artist_id, album_name)
        print(f"*** OK: album {album_name} added to albums table in database. ***")
        album_info = check_album(album_name)
    else: print("*** Album exists in the album table in database not changed ***")

## 7) Get album ID
    album_id = str(album_info[0][0])


## 8) INSERT tracks with album ID into tracks table

    x = input(f'Would you like to add tracks to the tracks table under Artist {artist_name}? Y/N> ')
    if not x.lower()=='y':
        print("*** OK tracks table in database not changed ***")
        break
    insert_tracks(album_id, tracks)
    
    

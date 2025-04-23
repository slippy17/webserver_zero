## Note this is the most recent version to add cds to the database.

import discid
import musicbrainzngs
import pandas as pd

# Load existing CD database
df = pd.read_pickle("cd_database.pkl")

# Initialize MusicBrainz user agent
musicbrainzngs.set_useragent("python-discid-example", "0.1", "your@mail")

def fetch_cd_metadata():
    try:
        disc = discid.read()
        print(f"Disc ID: {disc.id}")
        result = musicbrainzngs.get_releases_by_discid(disc.id, includes=["artists", "recordings"])
    except musicbrainzngs.ResponseError:
        print("Disc not found or bad response")
        return None

    if "disc" in result:
        release = result["disc"]["release-list"][0]
        print(f"CD Artist:\t{release['artist-credit-phrase']}")
        print(f"CD Album title:\t{release['title']}\n")
    elif "cdstub" in result:
        stub = result["cdstub"]
        print(f"CD Stub Title:\t{stub.get('title', 'Unknown')}")
    
    return result

def show_cd_slots():
    global df
    unique_discs = df[df['Disc_ID'].between(1, 101)].drop_duplicates(subset=['Disc_ID'])
    display_df = unique_discs.drop(columns=['Length', 'Artist','Song_Title', 'Track_ID'])
    display_df = display_df.sort_values(by='Disc_ID')
    print(display_df.to_string(index=False))
    return display_df

def add_cd_to_database(slot, query_result):
    global df
    if not query_result or "disc" not in query_result:
        print("No valid disc information found.")
        return

    release = query_result['disc']['release-list'][0]
    tracks = release['medium-list'][0]['track-list']
    artist = release['artist-credit'][0]['artist']['name']
    album = release['title']

    for track in tracks:
        song_title = track['recording']['title']
        length = int(track['recording'].get('length', 0))
        position = int(track['position'])
        new_entry = pd.Series(
            [slot, artist, album, position, song_title, length],
            index=df.columns
        )
        df.loc[len(df)] = new_entry
    df = df.sort_values(by=['Artist', 'Album'], ignore_index=True)

def list_track_titles(query_result):
    if not query_result or "disc" not in query_result:
        print("No valid track information found.")
        return

    tracks = query_result['disc']['release-list'][0]['medium-list'][0]['track-list']
    song_titles = [track['recording']['title'] for track in tracks]
    print(song_titles)

# Example usage
cd_metadata = fetch_cd_metadata()


# Show track info
list_track_titles(cd_metadata)



#show_cd_slots()

#Uncomment below line to add CD metadata to slot 91
#add_cd_to_database(92, cd_metadata)

show_cd_slots()

# write to pickle file.
#df.to_pickle("cd_database.pkl")



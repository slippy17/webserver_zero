import pandas as pd
from sqlalchemy import create_engine, text

##############################################################################
##
## This Tool creates a pkl file from the data in MySQL database.
## 
##
## Algorithm                                                                
## 1) Load pickle file
## 2) Use columns from pickle file to buid SELECT query.
## 3) Connect to DB
## 4) Run SELECT query + Capture the query in a dataframe
## 5) Convert the dataframe to match format of pkl file.
## 6) Save as pickle file.
##
## Note: A the current in-use pkl file is loaded so DF and DB can be compared.
##
##############################################################################

## 1) Load pickle file
df = pd.read_pickle("../static/cddb.pkl")

## 2) Use columns from pickle file.
cols = df.columns

# -----------------------------
# Database connection
## 3) Connect to DB
# -----------------------------
engine = create_engine("mysql+pymysql://root:123@192.168.0.115/cddb", echo=False)


def query_db():
    query = "select * from v_song_catalog;"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        output= result.all()
        
        return output
    
def convert_cols(cols,db):
    db = db.drop("track_id", axis=1)            ## drop track_id
    db = db.reindex(sorted(db.columns), axis=1) ## sort db columns
    c = cols.sort_values()                      ## sort df columns from pkl so they match
    db = db.set_axis(c, axis=1)                 ## rename db columns as in pkl file
    db = db[cols]                               ## put columns back in order as orginal pkl
    db['Disc_ID'] = db['Disc_ID'].fillna(0)     ## Disc_ID became a float. Need to make Nulls a 0
    #db = db.drop(db[db["Disc_ID"] == 0].index)  ## Drop Disc_ID=0 as CD not in CD player.
    db['Disc_ID'] = db['Disc_ID'].astype('int64')# Convert to int64
    db['Track_ID'] = db['Track_ID'].astype('object')
    db['Length'] = db['Length'].astype('object')
    
    return db

def show_cd_slots(df):
    
    unique_discs = df[df['Disc_ID'].between(1, 101)].drop_duplicates(subset=['Disc_ID'])
    display_df = unique_discs.drop(columns=['Length', 'Artist','Song_Title', 'Track_ID'])
    display_df = display_df.sort_values(by='Disc_ID')
    print(display_df.to_string(index=False))
    return display_df

def compare_dfs(df,df2):
    df1 = df.copy()
    cond = df1['Album'].isin(df2['Album'])
    df1.drop(df1[cond].index, inplace = True)
    return df1

## 4) Run SELECT query + Capture the query in a dataframe
db = pd.DataFrame(query_db())

## 5) Convert the dataframe to match format of pkl file.
db = convert_cols(cols,db)

## 6) Save as pickle file.
pd.to_pickle(db, "../static/cd_database.pkl")


## show albums in slot 0
##   db[db["Disc_ID"] == 0].drop_duplicates(subset=['Album'])
##   db[db["Disc_ID"] == 0].drop_duplicates(subset=['Album']).Album


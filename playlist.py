import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np

# Set up here is taken (and modified) from https://www.linkedin.com/pulse/extracting-your-fav-playlist-info-spotifys-api-samantha-jones/
cid = 'CID HERE'
secret = 'SECRET HERE'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

##FUNCTION EXPANDED FROM https://www.linkedin.com/pulse/extracting-your-fav-playlist-info-spotifys-api-samantha-jones/. Basis function from there. I added a lot to it, but started w/ that source.
def call_playlist(creator, playlist_id):

    # List of features
    playlist_features_list = ["artist","album","release_date", "track_name",  "track_id", "popularity", "danceability", "acousticness", "energy","liveness", "valence","key", "mode" ,"tempo", "duration_ms",]
    #Creating data frame, with cols as features
    playlist_df = pd.DataFrame(columns = playlist_features_list)

    # Next few lines (until for track in results) are taken DIRECTLY from https://stackoverflow.com/questions/55690063/is-there-a-method-to-retrieve-all-tracks-from-a-playlist-using-spotipy, w/ slight modification.
    # sp.user_play_list has a limit of 100 songs; with code below, i override that limit
    response = sp.user_playlist_tracks(creator, playlist_id, limit=100)
    results = response["items"]

    # Runs until end of playlist, instead of default limit of 100. Again, taken from https://stackoverflow.com/questions/55690063/is-there-a-method-to-retrieve-all-tracks-from-a-playlist-using-spotipy
    while len(results) < response["total"]:
        response = sp.user_playlist_tracks(
            creator, playlist_id, limit=100, offset=len(results)
        )
        results.extend(response["items"])

    for track in results:
        try:
            # Empty dict
            playlist_features = {}

            # Getting basic information of songs (artist, album, name, unique id)
            playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]
            # I added the code in the line below. Gets the tracjs release date
            playlist_features["release_date"] = track["track"]["album"]["release_date"]
            # https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50
            playlist_features["popularity"] = track["track"]["popularity"]

            # Getting audio features data
            audio_features = sp.audio_features(playlist_features["track_id"])[0]
            for feature in playlist_features_list[6:]:
                playlist_features[feature] = audio_features[feature]

            # Concat the dataframes
            track_df = pd.DataFrame(playlist_features, index = [0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)
            # Added line below, extract year from date,
            # https://stackoverflow.com/questions/25146121/extracting-just-month-and-year-separately-from-pandas-datetime-column &  https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
            playlist_df["year"] = pd.to_datetime(playlist_df["release_date"]).dt.year
            # Round year down (floor), divide by 10, multiply by 10. This method gives you the decade (as an int)
            playlist_df["Decade"] = (np.floor( playlist_df["year"]/ 10)*10).astype(int)

            # Next, I will be creating bins in the dataframe. This will allow me to group data that is in the same range (for example, grouping together songs w/ a popularity betwee 0 and .10)
            # https://www.statology.org/data-binning-in-python/
            # First, making making bins for data that's between 0 and 1
            bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
            #Then, creating labels for these bins
            labels = ["0.0-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4",  "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"]
            for feature in playlist_features_list[6:11]:
                # Creating cols in the dataframe that indicate which bin the audio featusres fall into (ex. is it between 0 and .1, or .1 and .2, etc.)
                playlist_df[f'{feature}_bin'] = pd.cut(playlist_df[f'{feature}'], bins, labels =labels)


            # Next, will make bins for tempo
            tempobin = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 100000]
            playlist_df['Tempo'] = pd.cut(playlist_df['tempo'], tempobin,
            labels =["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100", "100-110", "110-120", "120-130","130-140", "140-150", "150-160", "160-170", "170-180","180-190", "190-200", "200+"])

            # Next I will convert milliseconds to seconds
            playlist_df['duration_sec'] = playlist_df['duration_ms'] / 1000

            # Then I will create bins grouping songs by diff minutes
            secbin= [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, float("inf")]
            # Then, creating minutes col in datagrame, which indicates between how many minutes a song is.
            playlist_df['Minutes'] = pd.cut( playlist_df['duration_sec'], secbin, labels =["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8","8-9", "9-10", "10+"])

            # https://stackoverflow.com/questions/57543981/i-want-to-replace-numbers-in-a-data-frame-with-string-based-on-conditions
            # So, mode is an indicator variable for major and minor. Spotify says 0 means it's in minor key, while 1 is in major. Here, Replacing 0 w/ minor, 1 w/ major
            playlist_df.loc[playlist_df['mode']==0 ,'mode']='Minor'
            playlist_df.loc[playlist_df['mode']==1 ,'mode']='Major'

            # Key is also a variable where an integer represents a caterogical variable. Using this integer to key mapping, let's replace integers w/ keys.  https://medium.com/@FinchMF/praise-questions-and-critique-spotify-api-38e984a4174b
            # Method of changing df coloumn from https://stackoverflow.com/questions/51422062/how-can-i-replace-int-values-with-string-values-in-a-dataframe
            # Note, Spotify API says key value of -1 means spotify has no key on record for that track
            mapping = {-1: 'No Key Found',0:'C', 1: 'C♯/D♭', 2: 'D', 3:'D♯/E♭', 4: 'E', 5: 'F', 6:'F♯/G♭', 7:'G', 8:'G♯/A♭', 9:'A', 10:'A♯/B♭', 11:'B'}
            playlist_df['Key'] = playlist_df['key'].map(mapping)

        except: 
            print("Track not found. Skipping")
            #Returning dataframe
    return playlist_df
        
    

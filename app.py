# API https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track
# Spotipy set up help https://www.youtube.com/watch?v=3RGm4jALukM&ab_channel=DanArwady

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px
import plotly
import os
from flask import Flask, flash, redirect, render_template, request, session, make_response, Response
from flask_session import Session
from playlist import call_playlist


#  Set up from Spotipy team's github - https://github.com/spotipy-dev/spotipy/blob/master/examples/app.py
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

# Setting spotify API keys
SPOTIPY_CLIENT_ID= 'ENTER YOUR ID HERE'
SPOTIPY_CLIENT_SECRET= 'ENTER YOUR SECRET HERE'
## default redirect is 5000. Can changed in code and in Spotify dev dashboard.
SPOTIPY_REDIRECT_URI= 'http://localhost:5000/'

# Must set IDs as environment variables for Spotipy authroization. Doing that below.
os.environ["SPOTIPY_CLIENT_ID"] ='ENTER YOUR ID HERE'
os.environ["SPOTIPY_CLIENT_SECRET"] = 'ENTER YOUR SECRET HERE'
os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost:5000/'

# Defining bins that will later be used to generate graphs
bins =  ["0.0-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4",  "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"]


@app.route('/')
def index():
    if request.method == "POST":
        return redirect("nav.html")
    # MOSTLY TAKEN FROM https://github.com/spotipy-dev/spotipy/blob/master/examples/app.py. How user logs in
    else:
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                                cache_handler=cache_handler,
                                                show_dialog=True,
                                                client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI)

        if request.args.get("code"):
            # Redirect from Spotify authorization page
            auth_manager.get_access_token(request.args.get("code"))
            return redirect('/')

        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Prompt sign in if user has no token
            auth_url = auth_manager.get_authorize_url()
            html= render_template("signin.html", auth_url=auth_url)
            response = make_response(html)
            return response

        # If signed in, display index page
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        name =  spotify.me()["display_name"]
        html =  render_template("index.html", name=name)
        response = make_response(html)
        return response


# Taken from https://github.com/spotipy-dev/spotipy/blob/master/examples/app.py
@app.route('/sign_out')
def sign_out():
    # Log user out.
    session.pop("token_info", None)
    return redirect('/')


@app.route("/nav", methods=["GET","POST"])
# Taken from https://github.com/spotipy-dev/spotipy/blob/master/examples/app.py
def nav():
    if request.method == "POST":
        # get link from form
        link  = request.form.get("link")
        # if link isn't a playlist link. Return error text
        if 'open.spotify.com/playlist' not in link:
            return make_response("Please go back and enter valid URL, in the format open.spotify.com/playlist")
        else:
            link  = request.form.get("link")
            # prompt sign in if not signed in
            cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
            auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                return redirect('/')
            spotify = spotipy.Spotify(auth_manager=auth_manager)
            #creates dataframe of data from playlist using user input
            df = call_playlist("", link)
            # setting link and dataframe as session info.
            session['link'] = link
            session['df'] = df
            return render_template("nav.html")
    else:
            cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
            auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                return redirect('/')
            return render_template("nav.html")



# https://kenneho.net/2021/07/11/plotly-without-dash/
# https://stackoverflow.com/questions/31029560/plotting-categorical-data-with-pandas-and-matplotlib
# https://plotly.com/python/figure-labels/

#Above links helped me write the code below. Spefically, the format and use of plotly.offline.plot command is largely based on the first link
@app.route("/decade")
def decade():
        # Get data frame
        df = session.get('df')
        # Plot value counts (occurences) of each decade, as a %. Normalize = True generates the relative frequency (percents as decimal. Multiply by 100 to get percents, not decimals)
        fig = px.bar(df['Decade'].value_counts(normalize = True) * 100, title = "Percentage of Songs Released Each Decade")
        # Generate html for graph
        plot_as_string = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        # Check if user is logged in, if not, prompt log in.
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        # Show graph
        return render_template("decade.html", decade=plot_as_string)

@app.route("/minutes")
def minutes():
    # Get data frame
    df = session.get('df')
    time =px.bar(df['Minutes'].value_counts(normalize = True) * 100 ,title = "Percentage of Songs w/ Given Length")
    # Order axis from shortest to longest
    # https://stackoverflow.com/questions/68061197/re-order-axis-in-plotly-graph (used this source to help everywhere I used updated axis function)
    time.update_xaxes(categoryorder='array', categoryarray= ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8","8-9", "9-10", "10+"])
    timeplot = plotly.offline.plot(time, include_plotlyjs=False, output_type='div')
    # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    #creates graph of mins from user input
    return render_template("minutes.html", minutes=timeplot)




@app.route("/mode")
def mode():
    # Plotting Mode
    df = session.get('df')
    mode =px.pie(df, names='mode', title='Percentage of Songs in Major v Minor Key')
    mode1 = plotly.offline.plot(mode, include_plotlyjs=False, output_type='div')
    # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("mode.html", mode=mode1)



@app.route("/dance")
def dance():
    # Plotting Danaceability
    df = session.get('df')
    dance = px.bar(df['danceability_bin'].value_counts(normalize = True) * 100,title="Danceability of Songs (As Percentage)")
    # Fix order, using bins defined at the top.
    dance.update_xaxes(categoryorder='array', categoryarray= bins)
    dance1 = plotly.offline.plot(dance, include_plotlyjs=False, output_type='div')
    # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("dance.html", dance=dance1)

@app.route("/aco")
def aco():
    # Plotting Acoustiness
    df = session.get('df')
    aco = px.bar(df['acousticness_bin'].value_counts(normalize = True) * 100,title="Acousticness of Songs (As Percentage)")
    # Fix order of axes
    aco.update_xaxes(categoryorder='array', categoryarray= bins)
    aco1 = plotly.offline.plot(aco, include_plotlyjs=False, output_type='div')
   # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("aco.html", aco=aco1)

@app.route("/ene")
def ene():
    # Plotting energy
    df = session.get('df')
    ene = px.bar(df['energy_bin'].value_counts(normalize = True) * 100,title="Energy of Songs (As Percentage)")
    ene.update_xaxes(categoryorder='array', categoryarray= bins)
    ene1 = plotly.offline.plot(ene, include_plotlyjs=False, output_type='div')
   # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("ene.html", ene=ene1)


@app.route("/liv")
def liv():
    # Plotting Liveness
    df = session.get('df')
    liv = px.bar(df['liveness_bin'].value_counts(normalize = True) * 100,title="Liveness of Songs (As Percentage)")
    # Fix axis order
    liv.update_xaxes(categoryorder='array', categoryarray= bins)
    liv1 = plotly.offline.plot(liv, include_plotlyjs=False, output_type='div')
   # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("liv.html", liv=liv1)

@app.route("/val")
def val():
    # Plotting Valence
    df = session.get('df')
    v = px.bar(df['valence_bin'].value_counts(normalize = True) * 100,title="Valence of Songs (As Percentage)")
    # Fix axis order
    v.update_xaxes(categoryorder='array', categoryarray= bins)
    v1 = plotly.offline.plot(v, include_plotlyjs=False, output_type='div')
    # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("val.html", v=v1)


@app.route("/tempo")
def tempo():
    # Plotting Tempo
    df = session.get('df')
    tempo =px.bar(df['Tempo'].value_counts(normalize = True) * 100 ,title = "Percentage of Songs w/ Given Tempo")
    # Fix order
    tempo.update_xaxes(categoryorder='array', categoryarray=
    ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100", "100-110", "110-120", "120-130","130-140", "140-150", "150-160", "160-170", "170-180","180-190", "190-200", "200+"])
    tempo1= plotly.offline.plot(tempo, include_plotlyjs=False, output_type='div')
   # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("tempo.html", tempo=tempo1)

@app.route("/key")
def key():
    # Plotting Key
    df = session.get('df')
    key = px.pie(df, names='Key', title='Percentage of Songs in Each Key')
    key1 = plotly.offline.plot(key, include_plotlyjs=False, output_type='div')
   # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("key.html", key=key1)

@app.route("/raw")
def raw():
    df = session.get('df')
    # Selecting only cols I want to show
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_html.html
    table = df[["artist", "album", "release_date", "track_name", "popularity", "danceability", "acousticness", "energy", "liveness", "valence", "mode", "tempo", "Minutes", "Key"]]
    # Removing index col, adding space btwn cols, and centering text.
    raw = table.to_html(index=False, col_space= "100px", justify="center")
    # Require login to access page
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return render_template("raw.html", raw=raw)

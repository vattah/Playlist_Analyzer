## This is a project I worked on for CS50 in Fall 2022. It is a Spotify playlist data visualization website that retrieves data from songs in a public playlist and displays it in an easy-to-understand format for the user. See the video below for the demo.


## YouTube Presentation URL: [https://www.youtube.com/watch?v=BBq3hvi6LLk&ab_channel=CS50](https://www.youtube.com/watch?v=BBq3hvi6LLk&ab_channel=CS50)

# How to run

# Installation of packages





First, download my files, and import them to visual studio code. You can do this by downloading the zip, opening the file location, and then unzipping it. Then, you can go to VSCode and import the folder. Then, make sure you’re in the right directory (one containing my project folder). The first thing you need to do is go to your visual studio code and install all required packages.





Run the following commands in your terminal.





pip install spotipy



pip install pandas



pip install plotly.express



pip install plotly



pip install flask



pip install flask_session



pip install numpy





# Local setup



After installing the required packages and making sure you’re in the proper directory, you can run the program. To access the website, use flask run --port 5000. Click the link in the terminal. If for some reason, the link does work, manually visit the following site: [http://localhost:5000/](http://localhost:5000/). 

Also, you must visit https://developer.spotify.com/dashboard, create an app, and generate your own API keys/client IDs. Alternatively, you can contact me, and I can add your email associated with your Spotify account to a list of approved users for the app.





# Using the site





Click the Sign In button under the Spotify logo. This should take you to the sign in page for Spotify. Login (or register if you don’t have an account), then press agree. Then, go to a public playlist, copy the link, and paste it into the textbox. The playlist HAS to be public, so follow [this link](https://www.androidauthority.com/make-spotify-playlist-public-3075538/) to make your playlist public. The playlist does not need to be made by you; as long as it is public, it will work. Note that the "Your Top Songs" Spotify playlist cannot be made public/viewable by others. Additionally, playlist must not include podcast episodes, as the data for podcasts isn't the same as songs. Also, please avoid playlists with local files. Spotify API isn't able to get data on these songs, since they are locally hosted on devices, and not spotify servers.



If you want an example playlist link to use, [use mine](https://open.spotify.com/playlist/3Rbj8196hjpjRdqSdivkF8?si=f98b1285d9cc4e8e)





After entering the link, press analyze. This will take you to the navigation page, where you can navigate the website. Click any of the links to view your data for the respective category; if you want to learn more about each category, click “understanding data” at the top of the page. Use the links on each page to navigate between pages. If you want to analyze a new playlist, click Playlist Analyzer at the top left. When you want to sign out, press sign out at the top right.

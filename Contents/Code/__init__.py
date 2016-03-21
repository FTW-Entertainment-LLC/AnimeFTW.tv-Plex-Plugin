
TITLE = 'AnimeFTW'
PREFIX = '/video/animeftw'

ART = 'art-default.png'
ICON = 'icon-default.png'
ICON_FOLDER = 'icon-folder.png'

BASEURL  = 'https://www.animeftw.tv/api/v2/?devkey=kAsq-suUj-qG4t-Nxhx'
REMEMBER = '&remember=true'

###################################################################################################
def Start():
	
	# set default title for the plugin
	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)

	TVShowObject.thumb = R(ICON_FOLDER)
	TVShowObject.art = R(ART)

	DirectoryObject.thumb = R(ICON_FOLDER)
	DirectoryObject.art = R(ART)
	
	EpisodeObject.thumb = R(ICON_FOLDER)
	EpisodeObject.art = R(ART)
	
	VideoClipObject.thumb = R(ICON_FOLDER)
	VideoClipObject.art = R(ART)

	HTTP.Headers['User-Agent'] = 'plex-animeftw'

###################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer(no_cache = True)
	if not Prefs['username'] or not Prefs['password']:
		Log.Error("animeftw.bundle ----> No username and password, showing preferences")
		oc.add(PrefsObject(title=L('Preferences')))
		return oc
	else:
		# Create an object container for the menu and add the menu items
		oc.add(DirectoryObject(key=Callback(LatestMenu, count=25), title=("Latest...")))
		oc.add(DirectoryObject(key=Callback(MoviesMenu), title=L("BrowseMovies")))
		oc.add(DirectoryObject(key=Callback(SeriesMenu), title=L("BrowseSeries")))

	return oc

###################################################################################################
@route(PREFIX + '/latest')
def LatestMenu(count):
	
	if 'token' not in Dict:
		token = GetApiToken()
	else:
		token = Dict['token']

	# Create list of shows available to be viewed
	oc = ObjectContainer()
	oc.title1 = ("Latest...")
	
	# send request to validate credentials
	json_url = BASEURL + "&token=" + token + "&action=display-episodes&latest" + "&count=" + count
	latestList = JSON.ObjectFromURL(json_url)
	
	# TODO: this should be replaced with date from json response
	seriesArt = "https://d206m0dw9i4jjv.cloudfront.net/video-images/eyes_1_screen.jpeg"
	
	for latest in latestList["results"]:
		
		#Log(latest)
		
		# Create movie and add to container
		#oc.add(TVShowObject(
		#					key=Callback(EpisodeMenu, token=token, SeriesId=latest["id"], seriesTitle=latest["fullSeriesName"], seriesArt=seriesArt),
		#					rating_key="animeftw-" + latest["id"],
		#					title=latest["fullSeriesName"] + " - " + latest["epnumber"] + " - " + latest["epname"],
		#					thumb=latest["image"],
		#					art=latest["image"]
		#					))
	
		ListType = 'Latest'
		oc.add(CreateVideoClipObject(latest, ListType))
	
	return oc

###################################################################################################
@route(PREFIX + '/movies')
def MoviesMenu():
	
	if 'token' not in Dict:
		token = GetApiToken()
	else:
		token = Dict['token']
	
	# Create list of shows available to be viewed
	oc = ObjectContainer()
	oc.title1 = L("BrowseMovies")
	
	# send request to validate credentials
	json_url = BASEURL + "&token=" + token + "&action=display-movies&count&count=1000"
	moviesList = JSON.ObjectFromURL(json_url)
	
	# TODO: this should be replaced with date from json response
	seriesArt = "https://d206m0dw9i4jjv.cloudfront.net/video-images/eyes_1_screen.jpeg"
	
	for movies in moviesList["results"]:
		
		#Log(movies)
		
		# Create movie and add to container
		#oc.add(TVShowObject(
		#	key=Callback(EpisodeMenu, token=token, SeriesId=movies["id"], seriesTitle=movies["fullSeriesName"], seriesArt=seriesArt),
		#					rating_key="animeftw-" + movies["id"],
		#					title=movies["fullSeriesName"],
		#					thumb=movies["image"],
		#					art=movies["image"]
		#					))
		
		ListType = 'Movies'
		oc.add(CreateVideoClipObject(movies, ListType))
	
	return oc

###################################################################################################
@route(PREFIX + '/series')
def SeriesMenu():
	
	if 'token' not in Dict:
		token = GetApiToken()
	else:
		token = Dict['token']

	# Create list of shows available to be viewed
	oc = ObjectContainer()
	oc.title1 = L("BrowseSeries")

	# send request to validate credentials
	json_url = BASEURL + "&token=" + token + "&action=display-series&count=4000"
	seriesList = JSON.ObjectFromURL(json_url)

	# TODO: this should be replaced with date from json response
	seriesArt = "https://d206m0dw9i4jjv.cloudfront.net/video-images/eyes_1_screen.jpeg"

	for series in seriesList["results"]:
	
	#Log(series)

		# Create tv show and add to container
		oc.add(TVShowObject(
			key=Callback(EpisodeMenu, token=token, seriesId=series["id"], seriesTitle=series["fullSeriesName"], seriesArt=seriesArt),
			rating_key="animeftw-" + series["id"],
			title=series["fullSeriesName"],
			summary=series["description"],
			thumb=series["image"],
			art=series["image"]
		))
	
	return oc


###################################################################################################
@route(PREFIX + '/episodes')
def EpisodeMenu(token, seriesId, seriesTitle, seriesArt = ""):

	Log("token: " + token + "; id: " + seriesId + "; seriesTitle: " + seriesTitle + "; seriesArt: " + seriesArt)

	# Create list of shows available to be viewed
	oc = ObjectContainer()
	oc.title1 = seriesTitle

	# send request to validate credentials
	json_url = BASEURL + "&token=" + token + "&action=display-episodes&id=" + seriesId
	episodeList = JSON.ObjectFromURL(json_url)

	episodes = sorted(episodeList["results"], key=lambda x: int(x["epnumber"]))
	#Log(episodes)

	for episode in episodes:
		# create a video clip object for each episode and add to container
		ListType = 'Series'
		oc.add(CreateVideoClipObject(episode, ListType))
		
	return oc


###################################################################################################
@route(PREFIX + '/VideoClipObject')
def CreateVideoClipObject(episode, ListType, include_container=False):

	if ListType == 'Latest':
		title = episode["fullSeriesName"] + " - " + episode["epnumber"] + " - " + episode["epname"]
	else:
		title = episode["epname"]

	if "video-1080p" in episode:
		url = episode["video-1080p"]
	else:
		if "video-720p" in episode:
			url = episode["video-720p"]
		else:
			url = episode["video"]

	summary = ""
	image = episode["image"]
	resolution = episode["vidwidth"]
	episode_number = int(episode["epnumber"])

	# determine the container type
	container_type = Container.MP4

	videoclip_obj = EpisodeObject(
		key=Callback(CreateVideoClipObject, episode=episode, ListType=ListType, include_container=True),
		rating_key=url,
		title=title,
		summary=summary,
		thumb=image,
		art=image,
		index=episode_number,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
				],
				container = container_type,
				video_resolution = resolution
			)
		]
	)

	if include_container:
		Log.Info("animeftw.bundle ----> Playing video file - " + url)
		return ObjectContainer(objects=[videoclip_obj])
	else:
		return videoclip_obj


###################################################################################################
def GetApiToken():

	# ensure that username / password are not empty
	username = Prefs['username']
	password = Prefs['password']

	Log.Debug("validating the username and password")

	if not (username and password):
		Log.Error("failed username / password empty test")
		raise Ex.MediaNotAuthorized

	# send request to validate credentials
	json_url = BASEURL + REMEMBER + "&username=" + username + "&password=" + password
	tokenRequest = JSON.ObjectFromURL(json_url)

	if (tokenRequest["status"] != "200"):
		Log.Error("failed credential test")
		raise Ex.MediaNotAuthorized

	Log.Debug("token was acquired: " + tokenRequest["message"])
	Dict['token'] = tokenRequest["message"]
	return tokenRequest["message"]



import urllib.request

import pylast
from gmusicapi import Mobileclient

config = dict(lastfm=dict(API_KEY='', API_SECRET='',
                          username='', password=''),
              gpm=dict(username='', password='',
                       device_id='1234567890abcdef'))


class LastFM:
    api = None
    neighbours_re = '<section class="neighbours-items-section">([\w\W]*?)<\/section>'
    neighbours_url = 'https://www.last.fm/user/{0}/neighbours'
    user_url = 'href="/user/([^\/]*?)"'

    def __init__(self):
        password_hash = pylast.md5(config['lastfm']['password'])
        self.api = pylast.LastFMNetwork(api_key=config['lastfm']['API_KEY'], api_secret=config['lastfm']['API_SECRET'],
                                        username=config['lastfm']['username'], password_hash=password_hash)

    def get_loved_tracks(self, user):
        return user.get_loved_tracks(limit=None)

    def get_neighbours(self):
        f = urllib.request.urlopen(self.neighbours_url.format(self.api.get_authenticated_user().get_name()))
        page = f.read().decode('utf-8')
        import re
        match = re.search(self.neighbours_re, page)
        div = match.group(1)
        users = re.findall(self.user_url, div)
        return list(set(users))


class GoogleMusicProvider:
    api = None

    def __init__(self, login, password, android_id, *args):
        self.api = Mobileclient()
        auth = self.api.login(login, password, android_id)
        if not auth:
            self.api.get
        print('GPM login: {0}'.format(auth))

    def search(self, query):
        return self.api.search(query, max_results=1)['song_hits'][0]['track']

    def getUrl(self, id):
        return self.api.get_stream_url(id)

    def add_playlist(self, name):
        return self.api.create_playlist(name)

    def add_to_playlist(self, trackId, playlistId):
        self.api.add_songs_to_playlist(playlist_id=playlistId, song_ids=trackId)


def collect_tracks_titles(user):
    print('- fetching loved for {0}'.format(user))
    tracks = last.get_loved_tracks(user)
    titles = list(map(lambda x: '{0}'.format(x[0]), tracks))
    print('  got {0}'.format(len(titles)))
    return titles


gmp = GoogleMusicProvider(config['gpm']['username'], config['gpm']['password'], config['gpm']['device_id'])

if gmp.api.is_authenticated():
    last = LastFM()
    track_list = []
    for user in last.get_neighbours():
        track_list += collect_tracks_titles(last.api.get_user(user))

    # add self?
    # track_list += collect_tracks_titles(last.api.get_authenticated_user())

    track_list = set(track_list)
    print('total tracks count: {0}'.format(len(track_list)))

    list_count = 900
    list_prefix = 'neighbours_{0}'
    current_list = 0

    for i, track in enumerate(track_list):
        if i % list_count == 0:
            current_list += 1
            current_prefix = list_prefix.format(current_list)
            current_playlist = gmp.add_playlist(current_prefix)
            print('using playlist {0}'.format(current_prefix))
        try:
            gmp_track = gmp.search(track)
            gmp.add_to_playlist(gmp_track['storeId'], current_playlist)
        except:
            print('No track: {0}'.format(track))
else:
    from gmusicapi.utils import utils

    print('read logs {0}'.format(utils.log_filepath))

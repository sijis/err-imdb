import logging

from errbot import BotPlugin, botcmd

log = logging.getLogger(name='errbot.plugins.Imdb')

try:
    from omdb import Client
except ImportError:
    log.error("Please install 'omdb' python package")


class IMDb(BotPlugin):
    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'apikey': None,
        }
        return config

    def _check_config(self, option):

        # if no config, return nothing
        if self.config is None:
            return None
        else:
            # now, let's validate the key
            if option in self.config:
                return self.config[option]
            else:
                return None

    def _connect(self):
        """ connection to imdb """

        api_key = self._check_config('apikey')

        imdb = Client(apikey=api_key)

        return imdb

    def _parse_movie_results(self, results):
        response = []
        count = 1
        for result in results:
            # X. Title (year) / <code>
            response.append('{0}. {1} ({2}/{3})'.format(
                count,
                result.title,
                result.year,
                result.imdb_id,
            ))
            count = count + 1
        return ' '.join(response)

    @botcmd
    def imdb(self, msg, args):
        ''' Search for movie titles
            Example:
            !imdb The Dark Knight
        '''
        imdb = self._connect()
        results_to_return = 5

        results = imdb.get(search=args)

        if not results:
            return 'No results for "{0}" found.'.format(args)

        movies = self._parse_movie_results(results[:results_to_return])
        return movies

    @botcmd
    def imdb_movie(self, msg, args):
        ''' Get movie details
            Example:
            !imdb movie tt0468569
        '''

        imdb = self._connect()
        movie_id = args

        movie = imdb.get(imdbid=movie_id)

        if not movie:
            return 'Movie with id ({0}) not found.'.format(movie_id)

        # Title (year), Plot: ..., Release: xxxx-xx-xx, imdb-url
        response = '{0} ({1}), Plot: {2} Released: {3}, {4}'.format(
            movie.title,
            movie.year,
            movie.plot,
            movie.released,
            'http://www.imdb.com/title/{0}/'.format(movie.imdb_id),
        )

        return response

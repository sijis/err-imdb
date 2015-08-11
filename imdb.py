from errbot import BotPlugin, botcmd
import logging

log = logging.getLogger(name='errbot.plugins.Imdb')

try:
    from imdbpie import Imdb
except ImportError:
    log.error("Please install 'imdbpie' python package")


class IMDb(BotPlugin):

    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'anonymize': False,
            'cache': False,
            'cache_dir': u'/tmp/imdbpiecache',
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

        anonymize = self._check_config('anonymize') or False
        cache = self._check_config('cache') or False
        cache_dir = self._check_config('cache_dir') or '/tmp/imdbpiecache'

        imdb = Imdb({
                    'anonymize': anonymize,
                    'cache': cache,
                    'cache_dir': cache_dir,
                    })

        return imdb

    def _parse_movie_results(self, results):
        response = []
        count = 1
        for result in results:
            # X. Title (year) / <code>
            response.append('{0}. {1} ({2}/{3})'.format(
                count,
                result['title'],
                result['year'],
                result['imdb_id'],
                )
            )
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

        results = imdb.search_for_title(args)
        results_total = len(results)

        if results_total == 0:
            self.send(msg.frm,
                      'No results for "{0}" found.'.format(args),
                      message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            return

        movies = self._parse_movie_results(results[:results_to_return])
        self.send(msg.frm,
                  '{0}'.format(movies),
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

    @botcmd
    def imdb_movie(self, msg, args):
        ''' Get movie details
            Example:
            !imdb movie tt0468569
        '''

        imdb = self._connect()
        movie_id = args

        if not imdb.title_exists(movie_id):
            self.send(msg.frm,
                      'Movie id ({0}) not valid.'.format(movie_id),
                      message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            return

        movie = imdb.get_title_by_id(movie_id)

        # Title (year), Plot: ..., Release: xxxx-xx-xx, imdb-url
        response = '{0} ({1}), Plot: {2} Released: {3}, {4}'.format(
            movie.title,
            movie.year,
            movie.plot_outline,
            movie.release_date,
            'http://www.imdb.com/title/{0}/'.format(movie.imdb_id),
        )

        self.send(msg.frm,
                  response,
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

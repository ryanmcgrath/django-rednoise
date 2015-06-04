from __future__ import absolute_import

from os.path import isfile

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles import finders

from whitenoise.django import DjangoWhiteNoise

A404 = '404 NOT FOUND'
PI = 'PATH_INFO'


class DjangoRedNoise(DjangoWhiteNoise):
    rednoise_config_attrs = [
        'should_serve_static',
        'should_serve_media'
    ]

    debug = False
    should_serve_static = True
    should_serve_media = True

    def __init__(self, application):
        """Basic init stuff. We allow overriding a few extra things.
        """
        self.charset = settings.FILE_CHARSET
        self.application = application
        self.staticfiles_dirs = []
        self.static_files = {}
        self.media_files = {}

        # Allow settings to override default attributes
        # We check for existing WHITENOISE_{} stuff to be compatible, but then
        # add a few RedNoise specific ones in order to not be too confusing.
        self.check_and_set_settings('WHITENOISE_{}', self.config_attrs)
        self.check_and_set_settings('REDNOISE_{}', self.rednoise_config_attrs)

        # If DEBUG=True in settings, then we'll just default Rednoise to debug.
        try:
            setattr(self, 'debug', getattr(settings, 'DEBUG'))
        except AttributeError:
            pass

        # Grab the various roots we care about.
        if self.should_serve_static:
            self.static_root, self.static_prefix = self.get_structure('STATIC')
            try:
                setattr(self, 'staticfiles_dirs', getattr(
                    settings, 'STATICFILES_DIRS'
                ))
            except AttributeError:
                pass

        if self.should_serve_media:
            self.media_root, self.media_prefix = self.get_structure('MEDIA')

    def __call__(self, environ, start_response):
        """Checks to see if a request is inside our designated media or static
        configurations.
        """
        if self.should_serve_static and self.is_static(environ[PI]):
            asset = self.load_static_file(environ[PI])
            if asset is not None:
                return self.serve(asset, environ, start_response)
            else:
                start_response(A404, [('Content-Type', 'text/plain')])
                return ['Not Found']

        if self.should_serve_media and self.is_media(environ[PI]):
            asset = self.load_media_file(environ[PI])
            if asset is not None:
                return self.serve(asset, environ, start_response)
            else:
                start_response(A404, [('Content-Type', 'text/plain')])
                return ['Not Found']

        return self.application(environ, start_response)

    def file_not_modified(self, static_file, environ):
        """We just hook in here to always return false (i.e, it was modified)
        in DEBUG scenarios. This is optimal for development/reloading
        scenarios.

        In a production scenario, you want the original Whitenoise setup, so
        super().
        """
        if self.debug:
            return False
        return super(DjangoRedNoise, self).file_not_modified(
            static_file,
            environ
        )

    def add_cache_headers(self, static_file, url):
        """Again, we hook in here to blank on adding cache headers in DEBUG
        scenarios. This is optimal for development/reloading
        scenarios.

        In a production scenario, you want the original Whitenoise setup, so
        super().
        """
        if self.debug:
            return
        super(DjangoRedNoise, self).add_cache_headers(static_file, url)

    def check_and_set_settings(self, settings_key, attributes):
        """Checks settings to see if we should override something.
        """
        for attr in attributes:
            key = settings_key.format(attr.upper())
            try:
                setattr(self, attr, getattr(settings, key))
            except AttributeError:
                pass

    def get_structure(self, key):
        """This code is almost verbatim from the Whitenoise project Django
        integration. Little reason to change it, short of string substitution.
        """
        url = getattr(settings, '%s_URL' % key, None)
        root = getattr(settings, '%s_ROOT' % key, None)
        if not url or not root:
            raise ImproperlyConfigured('%s_URL and %s_ROOT \
                must be configured to use RedNoise' % (key, key))
        prefix = urlparse.urlparse(url).path
        prefix = '/{}/'.format(prefix.strip('/'))
        return root, prefix

    def is_static(self, path):
        """Checks to see if a given path is trying to be all up in
        our static director(y||ies).
        """
        return path[:len(self.static_prefix)] == self.static_prefix

    def add_static_file(self, path):
        """Custom, ish. Adopts the same approach as Whitenoise, but instead
        handles creating of a File object per each valid static/media request.
        This is then cached for lookup later if need-be.

        If REDNOISE_DEBUG is True, then this will also scan extra
        STATICFILES_DIRS.

        See also: self.add_media_file()
        """
        file_path = None
        is_file = False
        if self.debug:
            result = finders.find(path.replace(self.static_prefix, ''))
            if result:
                is_file = True
                file_path = result

        if not is_file:  # Account for stuff like admin, etc
            file_path = ('%s/%s' % (
                self.static_root, path.replace(self.static_prefix, '')
            )).replace('\\', '/')
            is_file = isfile(file_path)

        if is_file:
            files = {}
            files[path] = self.get_static_file(file_path, path)
            if not self.debug:
                self.find_gzipped_alternatives(files)
            self.static_files.update(files)

    def load_static_file(self, path):
        """Retrieves a static file, optimizing along the way.
        Very possible it can return None. TODO: perhaps optimize that
        use case somehow.
        """
        asset = self.static_files.get(path)
        if asset is None or self.debug:
            self.add_static_file(path)
            asset = self.static_files.get(path)

        return asset

    def is_media(self, path):
        """Checks to see if a given path is trying to be all up in our
        media director(y||ies).
        """
        return path[:len(self.media_prefix)] == self.media_prefix

    def add_media_file(self, path):
        """Custom, ish. Adopts the same approach as Whitenoise, but instead
        handles creating of a File object per each valid static/media request.
        This is then cached for lookup later if need-be.

        Media and static assets have differing properties by their very
        nature, so we have separate methods.
        """
        file_path = ('%s/%s' % (
            self.media_root, path.replace(self.media_prefix, '')
        )).replace('\\', '/')
        if isfile(file_path):
            files = {}
            files[path] = self.get_static_file(file_path, path)
            self.media_files.update(files)

    def load_media_file(self, path):
        """Retrieves a media file, optimizing along the way.
        """
        asset = self.media_files.get(path)
        if asset is None or self.debug:
            self.add_media_file(path)
            asset = self.media_files.get(path)

        return asset

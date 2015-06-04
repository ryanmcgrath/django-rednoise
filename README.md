RedNoise
==========
Django as a framework is great, but file handling within any setup has never been particularly fun to configure. **[WhiteNoise](https://whitenoise.readthedocs.org/)** makes this, to borrow its own term, "radically simplified", and for the most part I've found it to be an ideal solution - though there are a few things I found myself wanting from time to time.

RedNoise is a different take on the DjangoWhiteNoise module from WhiteNoise. It aims to be (and as of writing, should be) completely compatible with the existing WhiteNoise API, but takes a different approach on a few things. I consider this an opinionated third-party addon to the WhiteNoise project, however I hope it goes without saying that anything here is up for grabs as a pull request or merge.

Getting Started
====================
1. `pip install django-rednoise`
2. Follow the WhiteNoise configuration guidelines - they all should work.
3. Modify your wsgi file as follows:

``` python
from django.core.wsgi import get_wsgi_application
from rednoise import DjangoRedNoise

application = get_wsgi_application()
application = DjangoRedNoise(application)
```

...and that's it. You can read on for additional configuration options if you think you need them, but the defaults are more or less sane. DjangoRedNoise is the only Class in this package; existing guides/documentation for WhiteNoise should still suffice.

Differences from WhiteNoise
-----------------------------------

- **RedNoise allows you to serve user-uploaded media**  
  Note that it performs no gzipping of content or anything; the use case this satisfied (for me, at least) was that users within a CMS
  needed to be able to upload images as part of a site; configuring storages and some S3 setup just got annoying to deal with. 
  
- **RedNoise respects Django's DEBUG flag**  
  When DEBUG is True, RedNoise will mimic the native Django static files handling routine. With this change, RedNoise can be used while
  in development (provided you're developing with uwsgi) so your environment can simulate a production server. I've found this to be
  faster than using Django's static serving in urls.py solution, YMMV.
  
- **When DEBUG is false, RedNoise mimics WhiteNoise's original behavior**  
  ...with two exceptions. One, being that Media can also be served, and two - whereas WhiteNoise scans all static files on startup,
  RedNoise will look for the file upon user request. If found, it will cache it much like WhiteNoise does - the advantage of this
  approach is that one can add static file(s) as necessary after the fact without requiring a restart of the process.
  
- **RedNoise 404s directly at the uwsgi level, rather than through the Django application**  
  Personally speaking, I don't see why Django should bother processing a 404 for an image that we know doesn't exist. This is, of
  course, a personal opinion of mine.


License
-------

MIT Licensed

Contact
-------
Questions, concerns? ryan [at] venodesigns dot net

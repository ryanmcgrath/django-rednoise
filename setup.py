import os
import codecs
from setuptools import setup, find_packages


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

def read(*path):
    full_path = os.path.join(PROJECT_ROOT, *path)
    with codecs.open(full_path, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='django-rednoise',
    version='1.0.5',
    author='Ryan McGrath',
    author_email='ryan@venodesigns.net',
    url='https://github.com/ryanmcgrath/django-rednoise/',
    packages=find_packages(exclude=['tests*']),
    install_requires=['django', 'whitenoise'],
    license='MIT',
    description="Opinionated Django-specific addon for Whitenoise.",
    long_description=read('README.rst'),
    keywords=['django', 'static', 'wsgi'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

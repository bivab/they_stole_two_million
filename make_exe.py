# modified version, original from http://www.moviepartners.com/blog/2009/03/20/making-py2exe-play-nice-with-pygame/

# py2exe setup program
from distutils.core import setup
import py2exe
import sys
import os
import glob
import shutil
import fnmatch
sys.argv.append("py2exe")
 
VERSION = '0.0.0.dev'
AUTHOR_NAME = 'Your Name'
AUTHOR_EMAIL = 'your_email@somewhere.com'
AUTHOR_URL = "http://www.urlofyourgamesite.com/"
PRODUCT_NAME = "GameName"
SCRIPT_MAIN = 'gamelib/main.py'
VERSIONSTRING = PRODUCT_NAME + " ALPHA " + VERSION
ICONFILE = 'icon.ico'
 
# Remove the build tree on exit automatically
REMOVE_BUILD_ON_EXIT = True
 
if os.path.exists('dist/'): shutil.rmtree('dist/')

import pygame
pygamedir = os.path.split(pygame.base.__file__)[0]

def opj(*args):
    path = os.path.join(*args) #'/'.join(args)
    return os.path.normpath(path)

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if 'svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    if not filename.endswith('pyc') and not filename.endswith('pyo'):
                        names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

extra_files = find_data_files("data", '*')
            #[ #("",[ICONFILE,'icon.png','readme.txt']),
                   #("data",[name for name in glob.glob(os.path.join('data','*.*')) if name[-3:] not in ['pyc', 'pyo']]),
                   #("gfx",glob.glob(os.path.join('gfx','*.jpg'))),
                   #("gfx",glob.glob(os.path.join('gfx','*.png'))),
                   #("fonts",glob.glob(os.path.join('fonts','*.ttf'))),
                   #("music",glob.glob(os.path.join('music','*.ogg'))),
                   #("snd",glob.glob(os.path.join('snd','*.wav'))),
                   #]


# List of all modules to automatically exclude from distribution build
# This gets rid of extra modules that aren't necessary for proper functioning of app
# You should only put things in this list if you know exactly what you DON'T need
# This has the benefit of drastically reducing the size of your dist
 
MODULE_EXCLUDES =[
    '_LWPCookieJar',
    '_MozillaCookieJar',
    '_ssl',
    'AppKit',
#    'base64',
    'BaseHTTPServer',
    'bdb',
    'compiler',
    'curses',
    'difflib',
    'distutils',
    'email',
    'Foundation',
    'ftplib',
    'gopherlib',
    'hashlib',
    'htmllib',
    'httplib',
    'mimetools',
    'mimetypes',
    'pydoc'
    'rfc822',
    'setuptools',
    'socket',
    'tcl',
    'Tkconstants',
    'Tkinter',
    'tty',
    'urllib',
    'urllib2',
    'urlparse',
    'webbrowser',
    ]
 
INCLUDE_STUFF = ['encodings',"encodings.latin_1", "gamelib"]
 
setup(windows=[
             {'script': SCRIPT_MAIN,
               'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)],
               #'icon_resources': [(1,ICONFILE)]}],
               }],
         options = {"py2exe": {
                             "optimize": 2,
                             "includes": INCLUDE_STUFF,
                             "compressed": 1,
                             "ascii": 1,
                             "bundle_files": 2,
                             "ignores": ['tcl','AppKit','Numeric','Foundation'],
                             "excludes": MODULE_EXCLUDES} },
          name = PRODUCT_NAME,
          version = VERSION,
          data_files = extra_files,
          zipfile = None,
          author = AUTHOR_NAME,
          author_email = AUTHOR_EMAIL,
          url = AUTHOR_URL)
 
# Create the /save folder for inclusion with the installer
#shutil.copytree('save','dist/save')
 
if os.path.exists('dist/tcl'): shutil.rmtree('dist/tcl') 
 
# Remove the build tree
if REMOVE_BUILD_ON_EXIT:
     shutil.rmtree('build/')
 
if os.path.exists('dist/tcl84.dll'): os.unlink('dist/tcl84.dll')
if os.path.exists('dist/tk84.dll'): os.unlink('dist/tk84.dll')

# copy pygame dll
for name in glob.glob(os.path.join(pygamedir, '*.dll')):
    shutil.copy(name, os.path.join('dist', os.path.split(name)[1]))
# copy pygame default font
shutil.copy(os.path.join(pygamedir, 'freesansbold.ttf'), 'dist/freesansbold.ttf')

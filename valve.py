#!/usr/bin/python3

from ModelBuilder import ModelBuilder
from parameters import parameters

from pywavefront import visualization
from pyglet.gl import *
from pyglet.window import key

import getopt
import ctypes
import sys
import os
from time import sleep

try:
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, 'm:f:v')
 
except getopt.GetoptError:
    print ("Invalid argument(s). Valid arguments are m:f:v")

fileName = "parameters.rcp"
modelFile = ""
verbose = False

for opt in opts:
    if opt[0][1] == 'f':
        fileName = opt[1]
    elif opt[0][1] == 'v':
        verbose = True
    elif opt[0][1] == 'm':
        modelFile = opt[1]

# Read in a new parameters file
p = parameters(fileName, verbose)

# Make sure we've got a pointer to the list of models
if ( modelFile != "" ):  # Model file passed in on the command line. Override parameters
    if ( p.check_index("MODEL_FILE") ) :
        p.set_value_by_index("MODEL_FILE", modelFile)
    else:
        p.set_value("string", "MODEL_FILE", modelFile)
elif ( not p.check_index("MODEL_FILE") or p.get_value_by_index("MODEL_FILE") == "" ):
       p.set_value("string", "MODEL_FILE", "model.lis")

modelFile = p.get_value_by_index("MODEL_FILE")
if ( len(modelFile) == 0 ):
    print("Unable to determine model file. Bailing")
    quit(1)

if verbose:
    print("Reading from %s" % modelFile)

try:
    file = open(modelFile, "r")
except FileNotFoundError:
    print("File %s not found" % modelFile)
    quit()

########## Load the model files into a list ##########
models = {}
for l in file:
    line = l.rstrip()

    if verbose:
        print(line)

    if line[0] == '#':
        continue

    elif line[0] == 'f':
        filename = line.split(',')[1]
        if verbose:
            print("models[%d]" % len(models), end=" " )
        models[len(models)] = ModelBuilder(filename, verbose)

    elif ( line[0] == 'i' ):
        vals = line.split(',')
        if ( len(vals) < 7 ):
            print("Unknown line format %s" % line)
            continue

        models[len(models)-1].set_initial_values(vals[1:7])
        
file.close()

############################## Set up the window ##############################
window = pyglet.window.Window(width=1280, height=720, resizable=True)
keys = key.KeyStateHandler()
window.push_handlers(keys)

rotation = 0.0
phi = 0.0
theta = 180.0
position = -2.0
lightfv = ctypes.c_float * 4

@window.event
def on_resize(width, height):
    viewport_width, viewport_height = window.get_framebuffer_size()
    glViewport(0, 0, viewport_width, viewport_height)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable( GL_BLEND );

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45., float(width)/height, 0.1, 5.)
    glMatrixMode(GL_MODELVIEW)
    return True

@window.event
def on_draw():
    window.clear()
    glLoadIdentity()

    glLightfv(GL_LIGHT0, GL_POSITION, lightfv(-1.0, 1.0, 1.0, 0.0))

    global position, phi, theta

    if ( phi > 360 ):
        phi = 0
    elif ( phi < 0 ):
        phi = 360

    if ( theta > 360 ):
        theta = 0
    elif ( theta < 0 ):
        theta = 360

    if ( position < -4.5 ):
        position = -4.5
    elif ( position > 0 ):
        position = 0

    glTranslated(0., 0., position)
    glRotatef( phi,   0,0,1 )
    glRotatef( theta, 1,0,0 )

    for model in models:
        glTranslatef(models[model].x, models[model].y, models[model].z)
        glRotatef(models[model].phi, 0,0,1)
        glRotatef(models[model].theta, 1,0,0)

        visualization.draw(models[model].get_scene())
        
        glRotatef(models[model].theta, -1,0,0)
        glRotatef(models[model].phi, 0,0,-1)
        glTranslatef(-models[model].x, -models[model].y, -models[model].z)

@window.event
def on_key_press(symbol, modifiers):

    if ( symbol == key.Q ):
        window.clear()
        window.close()
        pyglet.app.exit()

    pass

@window.event
def on_text_motion(motion):

    global position, phi, theta
    if ( motion == key.MOTION_UP ):
        theta -= 360.0*(3.6/window.height)
    elif ( motion == key.MOTION_DOWN ):
        theta += 360.0*(3.6/window.height)
    elif ( motion == key.MOTION_LEFT ):
        phi -= 360.0 * (3.6 / window.width)
    elif ( motion == key.MOTION_RIGHT ):
        phi += 360.0 * (3.6 / window.width)
    elif ( motion == key.MOTION_PREVIOUS_PAGE ):
        position += 0.25
    elif ( motion == key.MOTION_NEXT_PAGE ):
        position -= 0.25
    
    pass

@window.event
def on_key_release(symbol, modifiers):
    pass

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global position
    position += 0.25*scroll_y

@window.event
def on_mouse_drag(x,y,dx,dy,button,modifiers):

    global phi,theta

    if ( button == pyglet.window.mouse.MIDDLE ):
        phi   += 360.0 * (dx / window.width)
        theta += 360.0*(dy / window.height)

    pass

def update(dt):
    pass

#pyglet.clock.schedule(update)
pyglet.app.run()

for model in models:
    del model

quit()


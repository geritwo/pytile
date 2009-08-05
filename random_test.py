
import pygame
from pygame.locals import *
import sys, os, random, math

pygame.init()

# Size of the screen
X_SCREEN = 1000
Y_SCREEN = 500

# Set offsets of origin of depiction of 1D noise
X_OFFSET_LEFT = 10
X_OFFSET_RIGHT = 200
Y_OFFSET = Y_SCREEN / 2

# Set size of the 1D noise output
X_LIMIT = X_SCREEN - X_OFFSET_LEFT - X_OFFSET_RIGHT
Y_LIMIT = Y_SCREEN / 2 - 10

# Colours
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

period = 1
num_octaves = 4
# Octaves from 0 to X
# Octave 1 is period 1, Octave 2 is period 1/2, Octave 3 is period 1/4 etc.

# pixels per period (in x dimension), 20 is smallest which looks good
PPP = 400
# In y dimension the equivalent value is taken by multiplying by the Y_LIMIT, assuming a value between 0 and 1


screen = pygame.display.set_mode([X_SCREEN, Y_SCREEN])
surface = pygame.Surface([X_SCREEN, Y_SCREEN])

persistence = 0.2

# Random values should always be between 0 and 1
def get_random():
    return random.random()

def gen_1D_values(length):
    vals = []
    for l in range(length):
        vals.append(get_random())
    return vals

def LinearInterpolate(a, b, x):
    return a*(1-x) + b*x

def CosineInterpolate(a, b, x):
    ft = x * math.pi
    f = (1 - math.cos(ft)) * 0.5
    return a*(1-f) + b*f

def regen_seed():
    random.seed()
    r = random.randint(0,100)
    return r

def generate(ppp, r):
    random.seed(r)
    allvals = []
    # First generate the seeds for each octave
    randoms = []
    for o in range(num_octaves):
        randoms.append(random.randint(0,100))
    # Octaves in range 1, num_octaves+1
    for o in range(num_octaves):
        random.seed(randoms[o])
        # Calculate length of one period for this octave in pixels
        # Total x length divided by the pixels per period value divided by the octave
        length, remainder = divmod(X_LIMIT, ppp / pow(2,o))
        if remainder > 0:
            allvals.append(gen_1D_values(length + 2))
        else:
            allvals.append(gen_1D_values(length + 1))

    print allvals

    surface.fill(BLACK)
    # draw x axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,Y_OFFSET), (X_OFFSET_LEFT+X_LIMIT,Y_OFFSET))
    # draw y axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,Y_OFFSET-Y_LIMIT), (X_OFFSET_LEFT,Y_OFFSET+Y_LIMIT))

    # Generate array of colours, divide 255 by number of octaves
    colours = []
    b = 100.0 / num_octaves
    c = 200.0 / num_octaves
    for d in range(num_octaves):
        colours.append((255 - int(c * d), 100, 155 + int(b * d)))

    surface.lock()
    for x in range(X_LIMIT):
        yvals = []
        for o, vals in enumerate(allvals):
            # Number of units along, number of pixels in one unit along
            xdiv, xmod = divmod(x, ppp / pow(2,o))
            if xmod != 0:
                # Convert number of pixels along in a period into a % value for the interpolation function
                percentalong = float(xmod) / ppp * pow(2,o)
            else:
                percentalong = 0
            yvals.append(CosineInterpolate(vals[xdiv], vals[xdiv+1], percentalong))
        # Finally draw the individual and resultant lines
        for o, y in enumerate(yvals):
            surface.set_at((X_OFFSET_LEFT+x,Y_OFFSET-y*Y_LIMIT), colours[o])
        y = sum(yvals) / len(yvals)
        surface.set_at((X_OFFSET_LEFT+x,Y_OFFSET*2-y*Y_LIMIT), RED)
        

    # draw all random points on the line at correct interval
    for o, vals in enumerate(allvals):
        for n, v in enumerate(vals):
            pos = (X_OFFSET_LEFT+n*ppp/pow(2,o),Y_OFFSET-v*Y_LIMIT)
            pygame.draw.circle(surface, GREEN, pos, 2)
            # For the main period also draw some red markers on the axis line
            if o == 0:
                pygame.draw.circle(surface, RED, (pos[0], Y_OFFSET), 3)
        pygame.draw.circle(surface, RED, pos, 3)
    surface.unlock()


def mainloop():
    ppp = PPP
    r = 50
    while 1:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT or key[K_ESCAPE]:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(surface, "Perlin Noise.png")
            if event.type == KEYDOWN and event.key == K_r:
                r = regen_seed()
                generate(ppp, r)
            if event.type == KEYDOWN and event.key == K_p:
                ppp += 10
                generate(ppp, r)
            if event.type == KEYDOWN and event.key == K_o:
                ppp -= 10
                if ppp <= 0:
                    ppp = 20
                generate(ppp, r)
        
        screen.blit(surface,(0,0))
        pygame.display.flip()

generate(PPP, 50)
mainloop()


##def LinearInterpolate(a, b, x):
##    return a*(1-x) + b*x
##
##def CubicInterpolate(v0, v1, v2, v3, x):
##    P = (v3 - v2) - (v0 - v1)
##    Q = (v0 - v1) - P
##    R = v2 - v0
##    S = v1
##    return P*math.pow(x,3) + Q*math.pow(x,2) + R*x + S
##
##def Noise(i, x, y):
####    random.seed(i)
##    return random.random()
##
##def SmoothedNoise(i, x, y):
##    corners = (Noise(i, x-1, y-1) + Noise(i, x+1, y-1) + Noise(i, x-1, y+1) + Noise(i, x+1, y+1)) / 16
##    sides = (Noise(i, x-1, y) + Noise(i, x+1, y) + Noise(i, x, y-1) + Noise(i, x, y+1) ) / 8
##    center = Noise(i, x, y) / 4
##    return corners + sides + center
##
##def InterpolatedNoise(i, x, y):
##    x_int = int(x)
##    x_frac = x - x_int
##    y_int = int(y)
##    y_frac = y - y_int
####    print x, y, x_int, y_int, x_frac, y_frac
##
##    v1 = SmoothedNoise(i, x_int, y_int)
##    v2 = SmoothedNoise(i, x_int+1, y_int)
##    v3 = SmoothedNoise(i, x_int, y_int+1)
##    v4 = SmoothedNoise(i, x_int+1, y_int+1)
##
####    i1 = LinearInterpolate(v1, v2, x_frac)
####    i2 = LinearInterpolate(v3, v4, x_frac)
####    return LinearInterpolate(i1, i2, y_frac)
##
##    return CubicInterpolate(v1, v2, v3, v4, x_frac)
##
##def PerlinNoise_2D(x, y):
####    print x, y
##    total = 0
##    p = persistence
##    n = num_octaves
##
##    for i in range(0, n):
##        frequency = math.pow(2,i)
##        amplitude = math.pow(p,i)
##
##        total += InterpolatedNoise(i, x*frequency, y*frequency) * amplitude
##
##    return total
##
##

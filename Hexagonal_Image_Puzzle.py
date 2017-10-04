# "Hexagonal_Image_Puzzle" By: Group 5

from math import *
from skimage import io
import numpy as np
import scipy.misc
from PIL import ImageTk
from Tkinter import *
import random

# ----------------------------------------------------------------------------------------------------------------------
#                                                   GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

global xunit
global yunit

global pos
global av
global avTags
global blankTag
global original
global images
global image
global difficulty
global tags
global free_space
global prev_move
global m
pos = {}
av = {}
avTags = {}
blankTag = 0;
original = {}
images = {}
image = "Images/statue.jpg"
difficulty = 2
tags = {}
free_space = 0
prev_move = 0
m = 0

total_moves = 0
mix_complete = False
stack_of_player_moves = []

# ----------------------------------------------------------------------------------------------------------------------
#                                               CANVAS AND IMAGE CREATION
# ----------------------------------------------------------------------------------------------------------------------

root = Tk()
root.title("Puzzle")

canvas = Canvas(root, width=1400, height=650, bg="black")
canvas.grid(row=1, columnspan=4)

# ----------------------------------------------------------------------------------------------------------------------
#                                                  HELPING FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------


def easy():
    global difficulty
    difficulty = 2
    action_bar.config(text="Difficulty: Easy (2 hexagon rings)")


def med():
    global difficulty
    difficulty = 3
    action_bar.config(text="Difficulty: Medium (3 hexagon rings)")


def hard():
    global difficulty
    difficulty = 4
    action_bar.config(text="Difficulty: Hard (4 hexagon rings)")


def vhard():
    global difficulty
    difficulty = 5
    action_bar.config(text="Difficulty: Very Hard (5 hexagon rings)")


def ehard():
    global difficulty
    difficulty = 6
    action_bar.config(text="Difficulty: Extremely Hard (6 hexagon rings)")


def getl(h, w, rings):
    if w/h > (2*rings+2+rings)/(sqrt(3)*(2*rings+1)):
        l = floor(h/((2*rings+1)*sqrt(3)))
    else:
        l = floor(w/(2*rings+rings+2))
    return l


def x(a, pos, xunit, yunit):
    if a > 0:
        return [pos[0] + int(1.5 * xunit), pos[1] + yunit]
    else:
        return [pos[0] - int(1.5 * xunit), pos[1] - yunit]


def y(a, pos, xunit, yunit):
    if a > 0:
        return [pos[0] - int(1.5 * xunit), pos[1] + yunit]
    else:
        return [pos[0] + int(1.5 * xunit), pos[1] - yunit]


def z(a, pos, xunit, yunit):
    if a > 0:
        return [pos[0], pos[1]+2*yunit]
    else:
        return [pos[0], pos[1]-2*yunit]


def available(position):
    global av
    global avTags
    global xunit
    global yunit
    temp = []

    tpos = z(-1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    tpos = z(+1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    tpos = x(-1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    tpos = x(+1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    tpos = y(-1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    tpos = y(+1, position, xunit, yunit)
    temp.append(tpos)
    if getTag(tpos) == -1: temp.pop()
    av = temp


def getTag(position):
    for i in pos.keys():
        if position == pos[i]: return i
    return -1


def cropping(immage, pos, xunit, yunit, tag):
    global images

    cropped = np.copy(immage[pos[1]-int(yunit)+1: pos[1]+int(yunit)-1, pos[0]-int(xunit):pos[0]+int(xunit)])
    nh = 2*yunit-2; nw = 2*xunit

    for y in range(0, int(yunit) + 3):
        for x in range(0, int(xunit/2) + 3):
            if y <= int(floor(x * (-sqrt(3))) + yunit):
                cropped[y, x] = [0, 0, 0, 0]
                cropped[nh - 1 - y, x] = [0, 0, 0, 0]
                cropped[y, nw - 1 - x] = [0, 0, 0, 0]
                cropped[nh - 1 - y, nw - 1 - x] = [0, 0, 0, 0]
    cropped = scipy.misc.toimage(cropped)
    images[tag] = cropped


def imgChoice(msg):
    global image
    image = msg
    action_bar.config(text="You chose an image. Now select your difficulty or press start.")


def initialize_game():
    start_button.config(state=NORMAL)
    solve_button.config(state=DISABLED)
    reset_button.config(state=DISABLED)
    # main_canvas.create_image(350, 225, image=saw, anchor=CENTER)


def reset_game():
    global pos
    pos = {}
    global av
    av = {}
    global blankTag
    blankTag = 0
    global original
    original = {}
    global images
    images = {}
    global image
    image = "Images/statue.jpg"
    global difficulty
    difficulty = 2
    global tags
    tags = {}
    canvas.delete(ALL)
    initialize_game()
    action_bar.config(text='A new game has been started. Please pick an image and your difficulty then press "START"')


def checkWin():
    for i in pos.keys():
        if not(pos[i] == original[i]): return

    win()


def win():
    while av: av.pop()
    images[0].save("temp.png", format="png")
    images[0] = ImageTk.PhotoImage(file="temp.png")
    tags[0] = canvas.create_image(pos[0][0], pos[0][1], image=images[0])
    action_bar.config(text='YOU WON! Press "RESET" and follow the instructions, if you want to play again!')


def move(tag):
    canvas.move(tags[tag], pos[blankTag][0]-pos[tag][0], pos[blankTag][1]-pos[tag][1])
    # canvas.move(blankTag, pos[tag][0]-pos[blankTag][0], pos[tag][1]-pos[blankTag][1])
    temp = pos[tag]
    pos[tag] = pos[blankTag]
    pos[blankTag] = temp

    canvas.update(); available(pos[blankTag])


def mouseEvent(event, tag):
    if pos[tag] in av: move(tag); stack_of_player_moves.append(tag); checkWin()
    else: print "not possible"


# ----------------------------------------------------------------------------------------------------------------------
#                                                 GAME FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------


def generatePos(immage, rings, h, w):
    global xunit
    global yunit
    l = getl(h, w, rings)
    if h % 2 == 0: h -= 1
    if w*2 == 0: w -= 1
    center = [w/2, h/2]

    xunit = int(floor(l/2.0)*2)
    yunit = int(floor(l*sqrt(3)/4)*2)

    pos[0] = center
    cropping(immage, center, xunit, yunit, 0)
    i = 1
    curpos = [center[0]+int(xunit*1.5), center[1]+yunit]
    cropping(immage, curpos, xunit, yunit, i)

    for ring in range(1, rings+1):
        pos[i] = curpos
        cropping(immage, curpos, xunit, yunit, i)
        i += 1
        for j in range(0, ring):
            curpos = z(-1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        for j in range(0, ring):
            curpos = x(-1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        for j in range(0, ring):
            curpos = y(1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        for j in range(0, ring):
            curpos = z(1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        for j in range(0, ring):
            curpos = x(1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        for j in range(0, ring-1):
            curpos = y(-1, curpos, xunit, yunit); pos[i] = curpos; cropping(immage, curpos, xunit, yunit, i); i += 1
        if ring < rings:
            curpos = [curpos[0]+3*xunit, curpos[1]]


def start():
    global tags
    global m
    global original
    start_button.config(state=DISABLED)
    reset_button.config(state=NORMAL)

    m = 6*difficulty*(difficulty+1)/4

    myImage = io.imread(image)
    # height, width, aux = myImage.shape
    if image == "Images/beach.jpg":
        width, height = 1400, 620
    else:
        width, height = 1400, 650
    myImage1 = np.zeros(shape=(height, width, 4))
    for row in range(0, height):
        for column in range(0,
                            width):  # red                    green                    blue         new = alpha (0-255)
            myImage1[row, column] = [myImage[row, column][0], myImage[row, column][1], myImage[row, column][2], 255]

    generatePos(myImage1, difficulty, height, width)
    original = pos.copy()
    available(pos[blankTag])

    for i in pos.keys():
        if not i == 0:
            images[i].save("temp.png", format="png")
            images[i] = ImageTk.PhotoImage(file="temp.png")
            tags[i] = canvas.create_image(pos[i][0], pos[i][1], image=images[i])
            canvas.tag_bind(tags[i], '<ButtonPress-1>', lambda event, arg=i: mouseEvent(event, arg))
    mixup(1)
    solve_button.config(state=NORMAL)


def mixup(n):
    global prev_move
    action_bar.configure(text="Scrambling puzzle please wait a moment...")
    if n < m:
        tile_choice = getTag(random.choice(av))  # Choose a random movable tile. The free_space is the key in the dict.
        while tile_choice == prev_move:  # Prevent trivial moves (back-and-forth of one tile)
            tile_choice = getTag(random.choice(av))
        prev_move = tile_choice  # The new free_space is now where the last tile used to be
        move(tile_choice)  # move the selected tile
        stack_of_player_moves.append(tile_choice)
        print "Stack of all moves so far:", stack_of_player_moves
        canvas.after(300, lambda: mixup(n+1))  # recursively call mix_up with a delay.

    else:
        mix_complete = True
        action_bar.configure(text="The puzzle has been sufficiently scrambled. You may begin.")
        solve_button.configure(state=NORMAL)


def solve():
    solve_button.config(state=DISABLED)
    k = 0
    while stack_of_player_moves:  # True until the list is empty.
        undo_move = stack_of_player_moves.pop()
        print "Undoing this move:", undo_move
        move(undo_move)
        k += 1  # Just a counter for the # of moves made to solve using simple "reverse all moves" strategy.
    checkWin()


# ----------------------------------------------------------------------------------------------------------------------
#                                               ENTRY BOXES & LABELS
# ----------------------------------------------------------------------------------------------------------------------

message = 'The game has been initialized! Please pick an image and your difficulty then press "START"'
action_bar = Label(root, text=message, bg='red', fg='yellow')
action_bar.grid(row=2, column=0, columnspan=4, sticky='EW')

# Label(root, text="Number of Moves Completed").grid(row=3, column=0)
# moves_box = Entry(justify=CENTER)
# moves_box.grid(row=4, column=1)

# ----------------------------------------------------------------------------------------------------------------------
#                                                       BUTTONS
# ----------------------------------------------------------------------------------------------------------------------

start_button = Button(root, text="START", cursor='hand2', command=start)
start_button.grid(row=3, column=0)

solve_button = Button(root, text="SOLVE", command=solve)
solve_button.grid(row=3, column=1)

reset_button = Button(root, text="RESET", cursor='X_cursor', command=reset_game)
reset_button.grid(row=3, column=2)

# ----------------------------------------------------------------------------------------------------------------------
#                                                        MENUS
# ----------------------------------------------------------------------------------------------------------------------

menu = Menu(root)
root.configure(menu=menu)

imgMenu = Menu(menu)
menu.add_cascade(label="Pick an image here.", menu=imgMenu)
imgMenu.add_command(label="Buddha", command=lambda: imgChoice("Images/statue.jpg"))
imgMenu.add_command(label="Deadpool", command=lambda: imgChoice("Images/pool.jpg"))
imgMenu.add_command(label="Suicide Squad", command=lambda: imgChoice("Images/squad.jpg"))
imgMenu.add_command(label="Airplane View", command=lambda: imgChoice("Images/peaks.jpg"))
imgMenu.add_command(label="Iron Man", command=lambda: imgChoice("Images/iron.jpg"))
imgMenu.add_command(label="Canyon", command=lambda: imgChoice("Images/can.jpg"))
imgMenu.add_command(label="Floating Islands", command=lambda: imgChoice("Images/float.jpg"))
imgMenu.add_command(label="Wall of China", command=lambda: imgChoice("Images/chin.jpg"))
imgMenu.add_command(label="Woman with Flower", command=lambda: imgChoice("Images/girl.jpg"))
imgMenu.add_command(label="Beach Walkway", command=lambda: imgChoice("Images/beach.jpg"))

# Difficulty menu
diffMenu = Menu(menu)
menu.add_cascade(label="Choose your difficulty here.", menu=diffMenu)
diffMenu.add_command(label="Easy                   (2 rings)", command=easy)
diffMenu.add_command(label="Medium            (3 rings)", command=med)
diffMenu.add_command(label="Hard                   (4 rings)", command=hard)
diffMenu.add_command(label="Very Hard          (5 rings)", command=vhard)
diffMenu.add_command(label="Extremely Hard (6 rings)", command=ehard)

initialize_game()

root.mainloop()

"""
File: project.py
----------------
This program is a game, named "Karel Jump" which is inspired by a game called "Doodle Jump".
In this game Karel keeps jumping as long as it lands on a surface, each time it jumps. As Karel jumps up
on the paddles above, it goes higher up, and the paddles left below are removed.
As Karel goes up, the score increases, and the goal is to earn higher scores.
A challenge faced by the player is that as Karel goes higher, the size of the paddles decrease, up to the
point where they turn into a square block, and jumping on them becomes more difficult.
It's worth noting that Karel needs to land on its downward facing foot, or else it will fall down.
"""

import pygame
import tkinter as tk
import time
import random
from PIL import ImageTk
from PIL import Image

pygame.init()

KAREL_HEIGHT = 60
FOOT_POS_LEFT = 27      # In Karel's image used in this program, the foot begins from the 27th pixel
FOOT_POS_RIGHT = 41     # In Karel's image used in this program, the foot ends in the 41st pixel

CANVAS_WIDTH = 1500      # Width of drawing canvas in pixels
CANVAS_HEIGHT = 800     # Height of drawing canvas in pixels

# Dimensions of the jumping paddles and their vertical distance from each other
PADDLE_WIDTH = 200
PADDLE_HEIGHT = 50
PADDLE_DIST = 192

# Determines how many frames per second are the animations
FRAMERATE = 30

KAREL_SPEED = 23  # Karel's initial speed when jumping
PADDLE_SPEED = 12  # Speed of the paddles while going one level up


def main():
    canvas = make_canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Karel Jump')  # Creating a blank canvas

    karel_file = ImageTk.PhotoImage(Image.open("karel.png"))
    karel_y = CANVAS_HEIGHT - PADDLE_HEIGHT - KAREL_HEIGHT  # Karel's initial position
    karel = canvas.create_image(((CANVAS_WIDTH/2)-25), karel_y, anchor="nw",
                                image=karel_file)  # Bring Karel into the canvas (Half the Karel's width is 25 pixels)

    # paddles is a list in which all the current paddles present on the screen are stored
    paddles = first_scene(canvas)

    score = 0
    score_board = canvas.create_text(10, 10, anchor='nw', font='Orbitron 16',
                                     text=('Score: ' + str(score)))  # Shows the live score on the corner of the canvas

    dy = KAREL_SPEED  # Karel's initial speed when jumping is 22 pixels per (1/FRAMERATE) of a second
    while True:
        karel_y = canvas.coords(karel)[1]  # Determines Karel's y position in each loop
        karel_y = jump(canvas, karel, karel_y, dy, score)  # Karel jumps and returns its final y position
        dy = KAREL_SPEED  # After on jump completes, the speed is set back to the initial speed
        if karel_y < (CANVAS_HEIGHT - 250):  # Each time Karel gets up high enough, the game goes one level up
            paddles = move_up(canvas, paddles, karel, karel_y, score)
            score += 1
            score_board = update_score(canvas, score, score_board)
            dy = PADDLE_SPEED  # After going one level up, Karel still needs to go up a little bit more with this initial speed


def update_score(canvas, score, score_board):
    '''
    Takes the current score and replaces it in the place of the old score shown on the screen.
    '''
    canvas.delete(score_board)
    score_board = canvas.create_text(10, 10, anchor='nw', font='Orbitron 16', text=('Score: ' + str(score)))
    return score_board


def first_scene(canvas):
    '''
    Creates the first set of paddles to be shown on the screen. Creates a list and puts all the paddles inside
    that list and returns it.
    '''
    # paddle0 is a paddle as wide as the canvas, located at the starting point of the game
    paddle0 = canvas.create_rectangle(4, (CANVAS_HEIGHT - PADDLE_HEIGHT), CANVAS_WIDTH, CANVAS_HEIGHT, fill="black")
    paddles = [paddle0]
    for i in range(4):
        x = random.randint(0, (CANVAS_WIDTH-PADDLE_WIDTH))  # Position for the left side of the paddle
        y = (y_position(canvas, paddles[i]) - PADDLE_DIST)  # Position for the top of the paddle
        new_paddle = canvas.create_rectangle(x, y, (x + PADDLE_WIDTH), (y + PADDLE_HEIGHT), fill="blue")
        paddles.append(new_paddle)  # Add the newly made paddle to paddles list
    return paddles


def y_position(canvas, element):
    y = canvas.coords(element)[1]
    return y


def move_up(canvas, paddles, karel, karel_y, score):
    '''
    Keeps Karel's y position fixed, while moving everything else down by the distance between two paddles.
    '''
    bounce = pygame.mixer.Sound("swoosh.wav")  # Sound effect for moving up
    pygame.mixer.Sound.play(bounce)
    new_paddle = create_paddle(canvas, paddles, score)  # Creating a new paddle
    paddles.append(new_paddle)  # Adding the newly made paddle to the list of paddles
    dy = PADDLE_SPEED
    for i in range(int(PADDLE_DIST/dy)):  # Animation loop
        karel_x = canvas.winfo_pointerx()
        canvas.moveto(karel, karel_x, karel_y)  # Keeping Karel's y position fixed and x position connected to mouse
        for paddle in paddles:  # Moving all the paddles in a single frame
            canvas.move(paddle, 0, dy)  # Not changing the x position of the paddles
        canvas.update()
        time.sleep(1/FRAMERATE)
    canvas.delete(paddles[0])  # Deleting the bottom paddle which has gone out of the frame
    paddles.pop(0)  # Removing the deleted paddle from the paddles list
    return paddles


def create_paddle(canvas, paddles, score):
    '''
    Creates a new paddle at the top of the canvas with a random x position.
    The length of the paddle decreases as the score increases,
    but the smallest size is when the paddle is square-shaped.
    The color of the paddle depends on its length.
    '''
    x = random.randint(0, (CANVAS_WIDTH - PADDLE_WIDTH))
    y = (y_position(canvas, paddles[-1]) - PADDLE_DIST)
    # While the score is not high enough to create a square-shaped paddle, the paddle size will be decreased by the
    # amount of achieved score.
    if score < (PADDLE_WIDTH - PADDLE_HEIGHT):
        length = PADDLE_WIDTH - score * 1
        # Each time the paddle length is decreased by the below mentioned amount, its color will change
        constant = int((PADDLE_WIDTH - PADDLE_HEIGHT)/4)
        if length > (PADDLE_WIDTH - constant):
            color = "blue"
        elif length > (PADDLE_WIDTH - (2 * constant)):
            color = "green"
        elif length > (PADDLE_WIDTH - (3 * constant)):
            color = "yellow"
        elif length > (PADDLE_WIDTH - (4 * constant)):
            color = "orange"
        else:
            color = "red"
        new_paddle = canvas.create_rectangle(x, y, (x + length), (y + PADDLE_HEIGHT), fill=color)
    else:  # The square-shaped paddles will all be red
        new_paddle = canvas.create_rectangle(x, y, (x + PADDLE_HEIGHT), (y + PADDLE_HEIGHT), fill="red")
    return new_paddle


def karel_on_paddle(canvas, karel_x, karel_y):
    '''
    Determines whether or not Karel has landed on surface.
    '''
    x1 = karel_x + FOOT_POS_LEFT  # Left of Karel's foot (27th pixel from the left)
    y1 = karel_y + KAREL_HEIGHT - 1  # Bottom of Karel's foot (59th pixel from above)
    x2 = karel_x + FOOT_POS_RIGHT  # Right of Karel's foot (41st pixel from the left)
    y2 = karel_y + KAREL_HEIGHT  # Bottom of Karel's foot (60th pixel from above)
    results = canvas.find_overlapping(x1, y1, x2, y2)
    return len(results) > 1


def jump(canvas, karel, karel_y, dy, score):
    '''
    Makes Karel jump up, steadily decelerate, and then land back down.
    '''
    while karel_y < CANVAS_HEIGHT:
        karel_x = canvas.winfo_pointerx()  # Move Karel along the x axis according to mouse movement
        dy -= 1  # Accounting for the gravitational acceleration
        karel_y -= dy
        canvas.moveto(karel, karel_x, karel_y)
        canvas.update()
        time.sleep(1 / FRAMERATE)
        if dy < -1:  # Karel's foot's overlapping should only be considered as landing, when Karel is decelerating
            if karel_on_paddle(canvas, karel_x, karel_y):  # When Karel lands on a surface, the jump is completed
                return karel_y
        if karel_y > CANVAS_HEIGHT:  # When Karel falls off beyond the canvas height, the game is over
            pygame.mixer.music.load("death.wav")  # Sound effect for game over
            pygame.mixer.music.set_volume(0.1)  # Decreasing the sound effect volume
            pygame.mixer.music.play()
            game_over(canvas, score)
            canvas.mainloop()


def game_over(canvas, score):
    '''
    Displays the "Game Over!" sign and shows the final score.
    In order to keep the score sign in the middle, different codes are written for different amount of digits.
    '''
    canvas.delete("all")
    canvas.create_text(((CANVAS_WIDTH / 2) - 250), ((CANVAS_HEIGHT / 2) - 100), anchor='nw', font='Orbitron 52',
                       text='GAME OVER!')
    if score < 10:
        canvas.create_text(((CANVAS_WIDTH / 2) - 74), ((CANVAS_HEIGHT / 2) + 50), anchor='nw', font='Orbitron 26',
                           text='Score: ' + str(score))
    elif score < 100:
        canvas.create_text(((CANVAS_WIDTH / 2) - 83), ((CANVAS_HEIGHT / 2) + 50), anchor='nw', font='Orbitron 26',
                           text='Score: ' + str(score))
    elif score < 1000:
        canvas.create_text(((CANVAS_WIDTH / 2) - 92), ((CANVAS_HEIGHT / 2) + 50), anchor='nw', font='Orbitron 26',
                           text='Score: ' + str(score))
    else:
        canvas.create_text(((CANVAS_WIDTH / 2) - 101), ((CANVAS_HEIGHT / 2) + 50), anchor='nw', font='Orbitron 26',
                           text='Score: ' + str(score))


def make_canvas(width, height, title=None):
    '''
    Creates a blank canvas.
    '''
    top = tk.Tk()
    top.minsize(width=width, height=height)
    if title:
        top.title(title)
    canvas = tk.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    return canvas


if __name__ == '__main__':
    main()

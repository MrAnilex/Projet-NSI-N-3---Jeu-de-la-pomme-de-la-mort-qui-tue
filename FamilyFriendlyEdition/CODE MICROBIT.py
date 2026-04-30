from microbit import *

SEUIL = 200

while True:
    x = accelerometer.get_x()
    y = accelerometer.get_y()

    dx = 0
    dy = 0

    # gauche / droite
    if x < -SEUIL:
        dx = 1
    elif x > SEUIL:
        dx = -1

    # haut / bas
    if y < -SEUIL:
        dy = -1
    elif y > SEUIL:
        dy = 1

    # envoi vers le PC par USB série
    print("{};{}".format(dx, dy))

    sleep(50)

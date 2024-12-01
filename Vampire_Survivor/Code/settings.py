
#Importacion de librerias necesarias
import pygame               #Motor grafico
from os.path import join    #Manejo de rutas
from os import walk, listdir         #Manejo de directorios
from pytmx.util_pygame import load_pygame #Manejo de mapas
from random import choice   #Manejo de listas aleatorias

#Configuracion de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
#Tamaño de los tiles
TILE_SIZE = 32

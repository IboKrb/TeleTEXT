# main.py
import pygame
from game.app import Game

def main():
    pygame.init()
    pygame.font.init()
    try:
        game = Game()
        game.run()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()

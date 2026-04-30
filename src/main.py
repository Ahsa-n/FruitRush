import sys
import os

# Ensure package root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ui.game import Game

def main():
    print("Welcome to FRUIT RUSH: AI Pathfinding & ML Prediction!")
    print("Starting Game UI...")
    

    app = Game()
    app.run()

if __name__ == "__main__":
    main()
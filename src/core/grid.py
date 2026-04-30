import numpy as np
import random

class Grid:
    def __init__(self, width=20, height=20, obstacle_density=0.2):
        self.width = width
        self.height = height
        self.obstacle_density = obstacle_density
        # 0 = empty, 1 = wall
        self.grid = np.zeros((self.width, self.height), dtype=int)
        self.start = (0, 0)
        self.goal = (self.width - 1, self.height - 1)
        self.fruits = set()
        
    def generate_random_walls(self):
        self.grid.fill(0)
        num_obstacles = int((self.width * self.height) * self.obstacle_density)
        placed = 0
        while placed < num_obstacles:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) != self.start and (x, y) != self.goal and self.grid[x, y] == 0:
                self.grid[x, y] = 1
                placed += 1

    def spawn_fruits(self, num_fruits=3):
        self.fruits.clear()
        placed = 0
        while placed < num_fruits:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            pos = (x, y)
            if pos != self.start and pos != self.goal and self.grid[x, y] == 0 and pos not in self.fruits:
                self.fruits.add(pos)
                placed += 1

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x, y] == 0
        return False
        
    def get_neighbors(self, x, y):
        # Manhattan moves only: Up, Down, Left, Right
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

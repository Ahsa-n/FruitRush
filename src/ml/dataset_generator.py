import pandas as pd
import random
import os
import sys

# Ensure imports work from terminal
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.grid import Grid
from src.ai.astar import astar, get_turning_points, manhattan_distance

def generate_dataset(num_samples=1000, output_file="dataset.csv"):
    print(f"Generating {num_samples} samples...")
    data = []
    
    for i in range(num_samples):
        # Varying obstacle density to create simple & complex maps
        density = random.uniform(0.1, 0.4)
        grid = Grid(width=20, height=20, obstacle_density=density)
        
        # Start and goal are at opposite corners by default, but let's randomize goal slightly
        grid.goal = (random.randint(10, 19), random.randint(10, 19))
        grid.start = (random.randint(0, 9), random.randint(0, 9))
        
        grid.generate_random_walls()
        
        path = astar(grid)
        
        if path is not None:
            # Valid path found!
            steps = len(path) - 1
            turns = get_turning_points(path)
            euclidean = ((grid.goal[0] - grid.start[0])**2 + (grid.goal[1] - grid.start[1])**2)**0.5
            
            data.append({
                "obstacle_density": density,
                "euclidean_distance": euclidean,
                "turning_points": turns,
                "steps": steps
            })
            
        if (i+1) % 100 == 0:
            print(f"Processed {i+1}/{num_samples} maps.")
            
    df = pd.DataFrame(data)
    
    # Label paths: > median steps means "Complex" (1), else "Simple" (0)
    median_steps = df['steps'].median()
    df['complexity'] = (df['steps'] > median_steps).astype(int)
    
    # Save features without the actual step count label to avoid target leakage, since step count is only known after A* completes
    df = df[['obstacle_density', 'euclidean_distance', 'turning_points', 'complexity']]
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}. Median steps: {median_steps}. Shape: {df.shape}")

if __name__ == "__main__":
    generate_dataset(output_file="data/dataset.csv")
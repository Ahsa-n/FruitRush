import pygame
import sys
import os
import random
import joblib
import pandas as pd
import numpy as np
import math

# Adjust path to find src packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.grid import Grid
from src.ai.astar import astar, constraint_astar, get_turning_points

# --- Constants & Colors (Theme: Modern Dark/Neon) ---
FPS = 60
CELL_SIZE = 30
GRID_W = 20
GRID_H = 20
WINDOW_WIDTH = GRID_W * CELL_SIZE + 300  # Extra space for UI sidebar
WINDOW_HEIGHT = max(600, GRID_H * CELL_SIZE)

BG_COLOR = (30, 30, 46)          # Catppuccin Base
GRID_COLOR = (49, 50, 68)        # subtle grid lines
WALL_COLOR = (147, 153, 178)     # Soft grey walls
START_COLOR = (166, 227, 161)    # Neon Green
GOAL_COLOR = (243, 139, 168)     # Neon Red
PATH_COLOR = (137, 180, 250)     # Neon Blue
FRUIT_COLOR = (203, 166, 247)    # Neon Purple
PLAYER_COLOR = (249, 226, 175)   # Neon Yellow
AI_COLOR = (137, 180, 250)       # Neon Blue
TEXT_COLOR = (205, 214, 244)     # Crisp white/grey

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("FRUIT RUSH: AI & ML")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 36, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 18)
        
        self.grid_obj = Grid(width=GRID_W, height=GRID_H)
        
        self.load_model()
        self.state = "MENU"
        self.prediction = "N/A"
        self.highest_level = 1
        
    def load_model(self):
        try:
            model_data = joblib.load("data/model.pkl")
            self.ml_model = model_data['model']
            self.ml_scaler = model_data['scaler']
            print("ML Model loaded successfully.")
        except Exception as e:
            print(f"Could not load ML model: {e}")
            self.ml_model = None
            self.ml_scaler = None

    def predict_complexity(self):
        if not self.ml_model:
            return "Model Error"
        path = astar(self.grid_obj)
        if not path:
            return "No Valid Path"
        
        turns = get_turning_points(path)
        euclid = ((self.grid_obj.goal[0] - self.grid_obj.start[0])**2 + (self.grid_obj.goal[1] - self.grid_obj.start[1])**2)**0.5
        density = np.sum(self.grid_obj.grid) / (GRID_W * GRID_H)
        
        df = pd.DataFrame([{
            'obstacle_density': density,
            'euclidean_distance': euclid,
            'turning_points': turns
        }])
        
        scaled = self.ml_scaler.transform(df)
        pred = self.ml_model.predict(scaled)[0]
        return "Complex" if pred == 1 else "Simple"

    def draw_text(self, text, font, color, x, y):
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_button(self, text, x, y, w, h, hover):
        color = (69, 71, 90) if hover else (49, 50, 68)
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(self.screen, PATH_COLOR, (x, y, w, h), 2, border_radius=8)
        text_surf = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
        self.screen.blit(text_surf, text_rect)
        return pygame.Rect(x, y, w, h)

    def draw_grid_render(self, current_paths=None, px=None, py=None, ax=None, ay=None, explored_nodes=None):
        for x in range(GRID_W):
            for y in range(GRID_H):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Base grid
                pygame.draw.rect(self.screen, BG_COLOR, rect)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                
                # Explored nodes (for visualization)
                if explored_nodes and (x, y) in explored_nodes:
                    # Draw a distinct, pleasant teal color to clearly visualize the search
                    pygame.draw.rect(self.screen, (148, 226, 213), rect)  # Neon Teal
                
                # Path (Optional passed)
                if current_paths and (x, y) in current_paths:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                    
                # Redraw grid lines so they stay visible over colors
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                
                # Walls
                if self.grid_obj.grid[x, y] == 1:
                    # Draw base wall and an inner block for extra detail
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                    inner_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
                    pygame.draw.rect(self.screen, (110, 115, 141), inner_rect)
                    
                # Start / Goal
                if (x, y) == self.grid_obj.start:
                    pygame.draw.rect(self.screen, START_COLOR, rect)
                if (x, y) == self.grid_obj.goal:
                    pygame.draw.rect(self.screen, GOAL_COLOR, rect)
                    
                # Fruits
                if (x, y) in self.grid_obj.fruits:
                    pygame.draw.circle(self.screen, FRUIT_COLOR, (x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + CELL_SIZE//2), CELL_SIZE//3)
                    # Add detail inside fruit
                    pygame.draw.circle(self.screen, (255, 255, 255), (x * CELL_SIZE + CELL_SIZE//2 + 2, y * CELL_SIZE + CELL_SIZE//2 - 2), CELL_SIZE//8)
        
        # Smooth Players
        if px is not None and py is not None:
            pygame.draw.circle(self.screen, PLAYER_COLOR, (int(px), int(py)), CELL_SIZE//2 - 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(px), int(py)), CELL_SIZE//2 - 2, 2)
            pygame.draw.circle(self.screen, (200, 150, 50), (int(px), int(py)), CELL_SIZE//4) # inner core
        
        if ax is not None and ay is not None:
            pygame.draw.circle(self.screen, AI_COLOR, (int(ax), int(ay)), CELL_SIZE//2 - 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(ax), int(ay)), CELL_SIZE//2 - 2, 2)
            pygame.draw.circle(self.screen, (50, 100, 200), (int(ax), int(ay)), CELL_SIZE//4) # inner core

    def draw_sidebar(self):
        sb_x = GRID_W * CELL_SIZE + 20
        self.draw_text("AI & ML Pathfinding", self.title_font, PATH_COLOR, sb_x, 20)
        self.draw_text(f"Prediction: {self.prediction}", self.font, GOAL_COLOR if self.prediction == "Complex" else START_COLOR, sb_x, 80)
        self.draw_text("Mode: " + self.state, self.small_font, TEXT_COLOR, sb_x, 120)
        self.draw_text("Press ESC to Main Menu", self.small_font, WALL_COLOR, sb_x, WINDOW_HEIGHT - 40)

    # --- Mode Runners ---
    
    def generate_valid_map(self, num_fruits):
        # Guarantee a solvable map for Mode 1 & 2
        while True:
            self.grid_obj.generate_random_walls()
            self.grid_obj.spawn_fruits(num_fruits)
            path, _ = constraint_astar(self.grid_obj)
            if path:
                # If path exists, both player and AI can fully traverse the map for all objectives
                break

    def run_menu(self):
        self.screen.fill(BG_COLOR)
        
        # --- Background Animation ---
        t = pygame.time.get_ticks() / 1000.0
        # Slow-moving, subtle background grid
        offset_x = (t * 20) % CELL_SIZE
        offset_y = (t * 20) % CELL_SIZE
        for x in range(0, WINDOW_WIDTH + int(CELL_SIZE), int(CELL_SIZE)):
            pygame.draw.line(self.screen, (40, 40, 56), (x - offset_x, 0), (x - offset_x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT + int(CELL_SIZE), int(CELL_SIZE)):
            pygame.draw.line(self.screen, (40, 40, 56), (0, y - offset_y), (WINDOW_WIDTH, y - offset_y), 1)
            
        # Floating particles (representing fruits/path nodes)
        for i in range(12):
            px = (math.sin(t + i*2.1) * 250) + WINDOW_WIDTH/2
            py = (math.cos(t * 0.7 + i*1.3) * 200) + WINDOW_HEIGHT/2
            rad = 7 + math.sin(t * 3 + i)*2
            anim_color = PATH_COLOR if i % 3 == 0 else (START_COLOR if i % 3 == 1 else FRUIT_COLOR)
            # Faded colors for deep background
            r, g, b = anim_color
            fade_color = (max(r-80, 20), max(g-80, 20), max(b-80, 20))
            if rad > 0:
                pygame.draw.circle(self.screen, fade_color, (int(px), int(py)), int(rad))

        mx, my = pygame.mouse.get_pos()
        clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        # Animated Title Hover
        title_y = 100 + math.sin(t * 2) * 8
        self.draw_text("FRUIT RUSH: Pathfinding & ML", self.title_font, PATH_COLOR, 150, int(title_y))
        
        b1 = self.draw_button("Mode 1: Constraint A* (Fruits)", 150, 200, 350, 50, 150 <= mx <= 500 and 200 <= my <= 250)
        b2 = self.draw_button("Mode 2: AI Survival Chase", 150, 280, 350, 50, 150 <= mx <= 500 and 280 <= my <= 330)
        b3 = self.draw_button("Custom Map Editor", 150, 360, 350, 50, 150 <= mx <= 500 and 360 <= my <= 410)

        # Developer Credits
        dev_text = "Developed by: Ahsan Faizan & Ahzam Hassan"
        dev_surf = self.small_font.render(dev_text, True, (147, 153, 178)) # WALL_COLOR
        dev_rect = dev_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(dev_surf, dev_rect)

        if clicked:
            if b1.collidepoint((mx, my)):
                self.generate_valid_map(3)
                self.prediction = self.predict_complexity()
                self.state = "MODE1"
                self.mode1_init()
            elif b2.collidepoint((mx, my)):
                self.mode2_level = 1
                self.generate_valid_map(3) # Starts with 3 fruits
                self.prediction = self.predict_complexity()
                self.state = "MODE2"
                self.mode2_init()
            elif b3.collidepoint((mx, my)):
                self.grid_obj.grid.fill(0)
                self.grid_obj.fruits.clear()
                self.grid_obj.start = (0, 0)
                self.grid_obj.goal = (GRID_W - 1, GRID_H - 1)
                self.prediction = self.predict_complexity()
                self.state = "EDITOR"

    def mode1_init(self):
        # Pre-calculate path
        self.path, self.search_history = constraint_astar(self.grid_obj)
        self.search_index = 0
        self.path_index = 0
        # Start state at 'SEARCHING' to visualize nodes first
        self.mode1_state = "SEARCHING"
        self.explored_nodes = set()
        
        if self.path:
            self.p_px = self.path[0][0] * CELL_SIZE + CELL_SIZE//2
            self.p_py = self.path[0][1] * CELL_SIZE + CELL_SIZE//2
        else:
            self.p_px = self.grid_obj.start[0] * CELL_SIZE + CELL_SIZE//2
            self.p_py = self.grid_obj.start[1] * CELL_SIZE + CELL_SIZE//2
    
    def mode2_init(self):
        # Player coordinates (grid logic) starts at Start
        self.player_coord = list(self.grid_obj.start)
        
        # Pixel coordinates for smooth animation
        self.p_px = self.grid_obj.start[0] * CELL_SIZE + CELL_SIZE//2
        self.p_py = self.grid_obj.start[1] * CELL_SIZE + CELL_SIZE//2
        
        # Multi-agent support: spawn N agents where N = 1 + floor((level-1)/6)
        self.ai_agents = []
        num_agents = 1 + (self.mode2_level - 1) // 6

        # gather walkable candidate positions (exclude start)
        candidates = [
            (x, y) for x in range(GRID_W) for y in range(GRID_H)
            if self.grid_obj.grid[x, y] == 0 and (x, y) != self.grid_obj.start
        ]

        for i in range(num_agents):
            if i == 0:
                # first agent starts at the Goal (original behavior)
                coord = list(self.grid_obj.goal)
            else:
                # pick a spawn position different from the goal and other agents
                spawn = None
                for _ in range(50):
                    if not candidates:
                        break
                    choice = random.choice(candidates)
                    if choice != tuple(self.grid_obj.goal) and all(choice != tuple(a['coord']) for a in self.ai_agents):
                        spawn = choice
                        break
                if spawn is None:
                    # fallback: first available non-goal candidate or goal if none
                    spawn = next((c for c in candidates if c != tuple(self.grid_obj.goal)), tuple(self.grid_obj.goal))
                coord = [spawn[0], spawn[1]]

            a_px = coord[0] * CELL_SIZE + CELL_SIZE//2
            a_py = coord[1] * CELL_SIZE + CELL_SIZE//2
            agent = {
                'coord': coord,        # grid coord [x,y]
                'a_px': a_px,          # visual x
                'a_py': a_py,          # visual y
                'timer': i * 50,       # stagger timers slightly
                'path_cache': []
            }
            self.ai_agents.append(agent)

        # Base speed is 400ms, decreases by 40ms per level but must not exceed player's speed
        # Compute player's per-tile time (ms) from visual smoothing used in run_mode2
        player_visual_speed = 8  # pixels/frame used for player smoothing in run_mode2
        player_ms_per_tile = int(CELL_SIZE * 1000 / (player_visual_speed * FPS))
        self.ai_speed = max(player_ms_per_tile, 400 - (self.mode2_level - 1) * 40)
        self.mode2_status = "PLAYING" # States: PLAYING, WON, LOST

    def move_smooth(self, current, target, speed):
        # Interpolate visually
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        dist = (dx**2 + dy**2)**0.5
        if dist < speed:
            return target[0], target[1]
        
        return current[0] + (dx/dist)*speed, current[1] + (dy/dist)*speed

    def run_editor(self):
        self.screen.fill(BG_COLOR)
        
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // CELL_SIZE, my // CELL_SIZE
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                elif event.key == pygame.K_s and 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                    self.grid_obj.start = (gx, gy)
                    self.grid_obj.grid[gx, gy] = 0
                    self.prediction = self.predict_complexity()
                elif event.key == pygame.K_g and 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                    self.grid_obj.goal = (gx, gy)
                    self.grid_obj.grid[gx, gy] = 0
                    self.prediction = self.predict_complexity()
                elif event.key == pygame.K_c:
                    self.grid_obj.grid.fill(0)
                    self.grid_obj.fruits.clear()
                    self.prediction = self.predict_complexity()
                elif event.key == pygame.K_f and 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                    pos = (gx,gy)
                    if pos in self.grid_obj.fruits:
                        self.grid_obj.fruits.remove(pos)
                    else:
                        if self.grid_obj.is_walkable(gx, gy) and pos != self.grid_obj.start and pos != self.grid_obj.goal:
                            self.grid_obj.fruits.add(pos)
                elif event.key == pygame.K_SPACE:
                    self.state = "MODE1"
                    self.prediction = self.predict_complexity()
                    self.mode1_init()
                elif event.key == pygame.K_RETURN:
                    self.state = "MODE2"
                    self.mode2_level = 1
                    # Don't clear fruits for editor, but spawn randomly if none are placed
                    if not self.grid_obj.fruits:
                        self.grid_obj.spawn_fruits(3)
                    self.prediction = self.predict_complexity()
                    self.mode2_init()
                        
        left_click, _, right_click = pygame.mouse.get_pressed()
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            if left_click and (gx, gy) != self.grid_obj.start and (gx, gy) != self.grid_obj.goal:
                self.grid_obj.grid[gx, gy] = 1
                if (gx, gy) in self.grid_obj.fruits: self.grid_obj.fruits.remove((gx, gy))
                self.prediction = self.predict_complexity()
            elif right_click:
                self.grid_obj.grid[gx, gy] = 0
                self.prediction = self.predict_complexity()

        self.draw_grid_render()
        self.draw_sidebar()
        
        sy = 160
        sb_x = GRID_W * CELL_SIZE + 20
        self.draw_text("Editor Controls:", self.small_font, TEXT_COLOR, sb_x, sy)
        self.draw_text("- L-Click: Add Wall", self.small_font, WALL_COLOR, sb_x, sy+20)
        self.draw_text("- R-Click: Remove Wall", self.small_font, WALL_COLOR, sb_x, sy+40)
        self.draw_text("- Hover+S: Set Start", self.small_font, START_COLOR, sb_x, sy+60)
        self.draw_text("- Hover+G: Set Goal", self.small_font, GOAL_COLOR, sb_x, sy+80)
        self.draw_text("- Hover+F: Toggle Fruit", self.small_font, FRUIT_COLOR, sb_x, sy+100)
        self.draw_text("- C: Clear Board", self.small_font, TEXT_COLOR, sb_x, sy+120)
        
        self.draw_text("Play Mode:", self.font, PATH_COLOR, sb_x, sy+160)
        self.draw_text("- SPACE -> Start Mode 1", self.small_font, TEXT_COLOR, sb_x, sy+190)
        self.draw_text("- ENTER -> Start Mode 2", self.small_font, TEXT_COLOR, sb_x, sy+210)


    def run_mode1(self):
        self.screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "MENU"

        # Smooth Animation Engine
        anim_speed = 5
        
        if self.mode1_state == "SEARCHING":
            # Show a clear, slow flow of nodes being searched
            nodes_per_frame = 3  # 3 nodes per frame (180 nodes per second) for slightly faster animation
            for _ in range(nodes_per_frame):
                if self.search_index < len(self.search_history):
                    self.explored_nodes.add(self.search_history[self.search_index])
                    self.search_index += 1
            
            if self.search_index >= len(self.search_history):
                self.mode1_state = "MOVING"

        elif self.mode1_state == "MOVING":
            if self.path and self.path_index < len(self.path):
                target_grid = self.path[self.path_index]
                target_px = target_grid[0] * CELL_SIZE + CELL_SIZE//2
                target_py = target_grid[1] * CELL_SIZE + CELL_SIZE//2
                
                self.p_px, self.p_py = self.move_smooth((self.p_px, self.p_py), (target_px, target_py), anim_speed)
                
                if abs(self.p_px - target_px) < 1 and abs(self.p_py - target_py) < 1:
                    self.path_index += 1
                    if target_grid in self.grid_obj.fruits:
                        self.grid_obj.fruits.remove(target_grid)
        
        # Render passing explored_nodes
        self.draw_grid_render(
            current_paths=self.path if self.mode1_state == "MOVING" else None,
            px=self.p_px if self.mode1_state == "MOVING" else None,
            py=self.p_py if self.mode1_state == "MOVING" else None,
            explored_nodes=getattr(self, 'explored_nodes', None)
        )
        self.draw_sidebar()
        
        if self.mode1_state == "SEARCHING":
            self.draw_text("SEARCHING...", self.font, PATH_COLOR, GRID_W * CELL_SIZE + 20, 200)
        elif not self.path:
            self.draw_text("NO PATH FOUND!", self.font, GOAL_COLOR, GRID_W * CELL_SIZE + 20, 200)
        elif self.path_index >= len(self.path):
            self.draw_text("FINISHED!", self.title_font, START_COLOR, GRID_W * CELL_SIZE + 20, 200)

    def run_mode2(self):
        self.screen.fill(BG_COLOR)
        dt = self.clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                
                if self.mode2_status == "PLAYING":
                    # Player Grid Movement
                    nx, ny = self.player_coord[0], self.player_coord[1]
                    if event.key == pygame.K_UP: ny -= 1
                    elif event.key == pygame.K_DOWN: ny += 1
                    elif event.key == pygame.K_LEFT: nx -= 1
                    elif event.key == pygame.K_RIGHT: nx += 1
                    
                    if self.grid_obj.is_walkable(nx, ny):
                        self.player_coord = [nx, ny]
                        # check fruit collection
                        if tuple(self.player_coord) in self.grid_obj.fruits:
                            self.grid_obj.fruits.remove(tuple(self.player_coord))
                
                elif self.mode2_status == "WON":
                    if event.key == pygame.K_SPACE:
                        self.mode2_level += 1
                        self.highest_level = max(self.highest_level, self.mode2_level)
                        num_fruits = 3 + (self.mode2_level - 1) // 2
                        self.generate_valid_map(num_fruits)
                        self.prediction = self.predict_complexity()
                        self.mode2_init()
                elif self.mode2_status == "LOST":
                    if event.key == pygame.K_SPACE:
                        self.state = "MENU"

        if self.mode2_status == "PLAYING":
            # AI Logic for multiple agents
            for agent in self.ai_agents:
                agent['timer'] += dt
                if agent['timer'] > self.ai_speed:
                    agent['timer'] = 0

                    # Target selection logic (same as single-AI behavior)
                    target = tuple(self.player_coord)
                    if random.random() < 0.3:
                        if self.grid_obj.fruits:
                            # Find closest fruit relative to this agent
                            target = min(self.grid_obj.fruits, key=lambda f: abs(f[0]-agent['coord'][0]) + abs(f[1]-agent['coord'][1]))
                        else:
                            target = self.grid_obj.goal

                    # A* dynamically from agent to Target
                    orig_start = self.grid_obj.start
                    orig_goal = self.grid_obj.goal
                    self.grid_obj.start = tuple(agent['coord'])
                    self.grid_obj.goal = target

                    path = astar(self.grid_obj)

                    self.grid_obj.start = orig_start
                    self.grid_obj.goal = orig_goal

                    if path and len(path) > 1:
                        # Next step in path
                        agent['coord'] = list(path[1])
                        agent['path_cache'] = path

            # Win/Loss conditions: any agent touching player -> LOST
            for agent in self.ai_agents:
                if tuple(self.player_coord) == tuple(agent['coord']):
                    self.mode2_status = "LOST"
                    # clear paths for clarity
                    for a in self.ai_agents:
                        a['path_cache'] = []
                    break

            # Win condition: player reached goal and collected fruits
            if tuple(self.player_coord) == self.grid_obj.goal and not self.grid_obj.fruits:
                self.mode2_status = "WON"
                for a in self.ai_agents:
                    a['path_cache'] = []

        # Smooth Interpolation
        p_target_px = self.player_coord[0] * CELL_SIZE + CELL_SIZE//2
        p_target_py = self.player_coord[1] * CELL_SIZE + CELL_SIZE//2
        self.p_px, self.p_py = self.move_smooth((self.p_px, self.p_py), (p_target_px, p_target_py), 8)

        # Smoothly update visual positions for each AI and collect path caches to render
        visual_ai_speed = 8 if self.mode2_status != "PLAYING" else 4
        path_union = []
        for agent in self.ai_agents:
            a_target_px = agent['coord'][0] * CELL_SIZE + CELL_SIZE//2
            a_target_py = agent['coord'][1] * CELL_SIZE + CELL_SIZE//2
            agent['a_px'], agent['a_py'] = self.move_smooth((agent['a_px'], agent['a_py']), (a_target_px, a_target_py), visual_ai_speed)
            if self.mode2_status == "PLAYING" and agent.get('path_cache'):
                path_union.extend(agent['path_cache'])

        # Draw combined AI path hints (if any)
        self.draw_grid_render(current_paths=path_union if path_union else None, px=self.p_px, py=self.p_py)

        # Draw each AI on top of the grid
        for idx, agent in enumerate(self.ai_agents):
            shade = AI_COLOR
            pygame.draw.circle(self.screen, shade, (int(agent['a_px']), int(agent['a_py'])), CELL_SIZE//2 - 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(agent['a_px']), int(agent['a_py'])), CELL_SIZE//2 - 2, 2)
            pygame.draw.circle(self.screen, (50, 100 + ((idx*30)%100), 200), (int(agent['a_px']), int(agent['a_py'])), CELL_SIZE//4)
        self.draw_sidebar()

        sb_x = GRID_W * CELL_SIZE + 20
        self.draw_text("Keys: Arrows to Move", self.small_font, PLAYER_COLOR, sb_x, 160)
        self.draw_text(f"Level: {self.mode2_level}", self.font, TEXT_COLOR, sb_x, 190)
        self.draw_text(f"Highest Level: {self.highest_level}", self.font, START_COLOR, sb_x, 220)
        
        if self.mode2_status == "WON":
            self.draw_text("LEVEL BEATEN!", self.title_font, START_COLOR, sb_x, 270)
            self.draw_text("Press SPACE for Next Level", self.small_font, TEXT_COLOR, sb_x, 310)
        elif self.mode2_status == "LOST":
            self.draw_text("AI CAUGHT YOU!", self.title_font, GOAL_COLOR, sb_x, 270)
            self.draw_text("Press SPACE for Menu", self.small_font, TEXT_COLOR, sb_x, 310)

    def run(self):
        while True:
            if self.state == "MENU":
                self.run_menu()
            elif self.state == "EDITOR":
                self.run_editor()
            elif self.state == "MODE1":
                self.run_mode1()
            elif self.state == "MODE2":
                self.run_mode2()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()

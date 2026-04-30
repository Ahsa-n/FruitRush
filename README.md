# FRUIT RUSH 🍓

![Python](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-CE%202.5.x-1c8c73?logo=pygame)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-ffb000?logo=scikitlearn)
![Status](https://img.shields.io/badge/Project-Pathfinding%20%26%20ML-7c5cff)

**FRUIT RUSH** is a colorful AI/ML pathfinding game built with Python, Pygame, and Scikit-learn. It combines classic **A*** search, **constraint-based pathfinding**, and **machine learning** to predict maze complexity in real time.

## ✨ Highlights

- 🧭 **A* Pathfinding** with Manhattan distance heuristic
- 🍓 **Constraint Mode** where the agent must collect all fruits before reaching the goal
- 🧠 **Machine Learning classifier** that predicts whether a map is **Simple** or **Complex**
- 👤 **AI Survival Chase** mode where one or more AI agents chase the player using dynamic A*
- 🧱 **Custom Map Editor** to draw walls, set start/goal, and place fruits manually
- 🎨 **Modern neon UI** with animated menu visuals and smooth path animation
- 📈 **Level scaling** with increasing challenge and additional AI agents over time

## 🎮 Game Modes

### 1) Constraint-Based A* Mode
The AI explores the maze, shows search progress, then follows the final optimal route after it is found. The agent must collect every fruit before reaching the goal.

### 2) AI Survival Chase Mode
The player must collect all fruits and reach the goal while AI agents chase dynamically using A*. Additional agents appear every 6 levels, and the AI speed increases until it reaches the player's movement speed cap.

### 3) Custom Map Editor
Create your own maze by:
- Left-clicking to add walls
- Right-clicking to remove walls
- Pressing `S` on a tile to set the start
- Pressing `G` on a tile to set the goal
- Pressing `F` on a tile to toggle a fruit
- Pressing `SPACE` to launch Mode 1
- Pressing `ENTER` to launch Mode 2

## 🖥️ Preview

The interface features:
- a dark neon-themed menu
- animated floating particles
- glowing buttons
- smooth agent movement
- visible grid lines during path visualization

## 🚀 Setup

### 1. Install dependencies
This project was built for Python 3.14+ and uses `pygame-ce` for compatibility.

```bash
python -m pip install pygame-ce numpy pandas scikit-learn joblib python-docx
```

### 2. Run the game

```bash
python src/main.py
```

## 🧪 Generate the report
A Word report can be generated with the included script:

```bash
python src/generate_report.py
```

This creates a `.docx` report in the project root.

## 🎯 Controls

### Menu
- `Mouse click` select a mode

### Mode 1
- `ESC` return to menu

### Mode 2
- `Arrow keys` move the player
- `SPACE` continue to the next level after winning
- `ESC` return to menu

### Editor
- `L-Click` add wall
- `R-Click` remove wall
- `S` set start on hovered tile
- `G` set goal on hovered tile
- `F` toggle fruit on hovered tile
- `C` clear map
- `SPACE` start Mode 1
- `ENTER` start Mode 2

## 📁 Project Structure

```text
src/
├── ai/
│   └── astar.py
├── core/
│   └── grid.py
├── ml/
│   ├── dataset_generator.py
│   └── train_model.py
├── ui/
│   └── game.py
├── generate_report.py
├── generate_project_proposal.py
└── main.py
```

## 🤖 Machine Learning Details

- **Task:** Binary classification
- **Classes:** Simple / Complex
- **Features:** obstacle density, Euclidean distance, turning points
- **Model:** Decision Tree Classifier
- **Training split:** 80/20
- **Target accuracy:** 80%+

## 🧩 Notes

- The game uses `pygame-ce` because it supports Python 3.14 more reliably than the legacy `pygame` package.
- The ML model is loaded from `data/model.pkl`.
- The generated dataset is stored in `data/dataset.csv`.

## 👨‍💻 Developers

- **Ahsan Faizan** — 23k-0615
- **Ahzam Hassan** — 23k-0695

## 📜 License

This project is created for academic purposes.

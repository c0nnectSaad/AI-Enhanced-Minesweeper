# AI-Enhanced Minesweeper

An advanced implementation of the classic Minesweeper game featuring AI-driven dynamic environment modifications.

## Features

- **Hint System**: AI-powered suggestions based on probability analysis
- **Smart Mine Placement**: Dynamic mine repositioning
- **Expanding Danger Zones**: Adaptive difficulty through mine density changes
- **AI-Driven Tile Manipulation**: Intelligent board layout adaptation
- **Tile Transformation**: Dynamic tile state changes

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

Run the game:
```bash
python main.py
```

### Game Rules
- Click tiles to uncover them
- Numbers indicate adjacent mines
- The board updates dynamically based on your actions
- Use AI hints to guide your moves
- Win by uncovering all safe tiles
- Lose by clicking on a mine

## Technical Details

- Built with Python and Pygame
- Uses NumPy for calculations
- Implements advanced AI algorithms for dynamic gameplay
- Real-time board updates and probability calculations 
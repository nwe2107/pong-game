# Pong Game
Single-player Pong clone built with Pygame.

## Requirements
- Python 3.10+ (developed with Python 3.13)
- pip
- (Optional) `python -m venv` for an isolated environment

## Get the code
- Clone: `git clone <repo-url> && cd Pong_Game`
- Or download the ZIP from your hosting service and extract it into a folder.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
python pong.py
```

## Build a standalone executable (PyInstaller)
- Activate your virtual env and install the builder: `pip install pyinstaller`
- Build (macOS/Linux): `python -m PyInstaller --windowed --onefile --name PongGame pong.py`
- Build (Windows): `pyinstaller --noconsole --onefile --name PongGame pong.py`
- The executable lives in `dist/` (`PongGame.app` on macOS, `PongGame.exe` on Windows). Double-click it to play.
- Build on the same OS you intend to ship for; cross-compiling is not supported out of the box.

## Controls
- `W` / `S` to move
- `P` to pause
- `R` to reset scores
- `Esc` to quit

## Gameplay notes
- First to 7 points wins.
- The ball speeds up slightly on paddle hits; your paddle adds spin based on contact point and movement.

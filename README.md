# Wild West Duel Game

A realistic dueling game where you face off against an NPC in a classic Wild West shootout with realistic ballistic physics.

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed on your system.
2. Install Pygame if you don't have it already:
   ```
   pip install pygame
   ```

## How to Play

1. Run the game:
   ```
   python duel_game.py
   ```

2. Game Controls:
   - **UP/DOWN Arrow Keys**: Adjust your aim angle
   - **LEFT/RIGHT Arrow Keys**: Adjust your shot power
   - **SPACE**: Confirm your aim and start the countdown
   - **R**: Restart the game after a duel ends
   - **Q**: Quit the game

## Gameplay

1. **Aiming Phase**: 
   - Use UP/DOWN arrow keys to adjust your aim angle
   - Use LEFT/RIGHT arrow keys to adjust your shot power
   - Watch the trajectory prediction to help you aim
   - Press SPACE when ready

2. **Countdown**: Wait for the countdown (3, 2, 1).

3. **Duel**: Both duelists will shoot automatically. The player shoots immediately, while the NPC has a random reaction time.

4. **Results**: The first one to hit their opponent wins! If both miss, it's a draw.

## Game Features

- Realistic ballistic physics with gravity affecting bullet trajectories
- Adjustable aim angle and shot power
- Trajectory prediction to help with aiming
- Bullet trails for visual effect
- Automatic shooting after countdown
- Random NPC reaction time, aim angle, and power
- Health bars for both duelists
- Simple restart option

## Physics Elements

- **Gravity**: Bullets are affected by gravity and follow a parabolic trajectory
- **Power**: Controls the initial velocity of the bullet
- **Angle**: Determines the launch angle of the bullet
- **Trajectory Prediction**: Shows the expected path of your bullet

## Future Improvements

- Sound effects for countdown and shooting
- Background music
- More detailed character sprites
- Multiple difficulty levels
- Wind effects that influence bullet trajectories
- Different weapons with unique ballistic properties

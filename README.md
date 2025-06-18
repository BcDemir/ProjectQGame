# Wild West Duel Game

A realistic dueling game where you face off against an NPC in a classic Wild West shootout with a reticle-based aiming system, simultaneous firing, realistic ballistic physics, and a health system.

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
   - **UP/DOWN Arrow Keys**: Adjust your aim angle (moves the reticle up/down)
     - Press and hold for continuous adjustment
     - Fine-tuned control with 0.10 degree increments
   - **LEFT/RIGHT Arrow Keys**: Adjust your shot power (moves the reticle closer/further)
     - Press and hold for continuous adjustment
   - **SPACE**: Start the countdown when you're ready
   - **R**: Restart the game after it ends
   - **Q**: Quit the game

## Gameplay

1. **Aiming Phase**:
   - Use UP/DOWN arrow keys to precisely adjust your aim angle
   - Use LEFT/RIGHT arrow keys to adjust your shot power
   - A red crosshair reticle shows where you're aiming
   - The NPC will also be adjusting their aim
   - Press SPACE when you're ready to start the countdown

2. **Countdown**:
   - A 3-second countdown will begin (3, 2, 1)
   - Both duelists will fire automatically when the countdown reaches zero

3. **Simultaneous Shooting**:
   - Both you and the NPC fire at the same time
   - Watch as both bullets travel through the air
   - See if either shot hits its target

4. **Damage System**:
   - Each duelist has 100 health points
   - Headshots deal 40 damage
   - Body shots deal 20 damage
   - Missed shots deal no damage

5. **Results**:
   - After each round, damage is calculated and health is updated
   - The game continues with another round until someone's health reaches zero
   - The first duelist to reduce their opponent's health to zero wins

## Game Features

- Precise aiming with 0.10 degree increments for fine control
- Continuous adjustment when keys are held down
- Compact reticle-based aiming system for intuitive targeting
- Simultaneous shooting after a tense countdown
- Multiple rounds with persistent health between rounds
- Health system with different damage based on hit location
- Long-distance dueling with small characters
- Realistic ballistic physics with gravity affecting bullet trajectories
- Power meter and angle display to help with aiming
- Adjustable aim angle and shot power
- Bullet trails for visual effect
- Hit messages showing damage dealt
- Health bars and numerical health display

## Physics Elements

- **Gravity**: Bullets are affected by gravity and follow a parabolic trajectory
- **Power**: Controls the initial velocity of the bullet (higher power needed for longer distances)
- **Angle**: Determines the launch angle of the bullet with precise 0.10 degree control
- **Reticle**: Shows where you're aiming, positioned closer to the player for better control

## Strategy Tips

- Use the fine angle control to precisely aim for headshots
- Hold down the arrow keys for smooth, continuous adjustments
- Try to predict where your opponent will be aiming
- Adjust your aim based on previous misses
- Consider both angle and power for the perfect shot
- Watch the trajectory of your opponent's shots to improve your own aim

## Future Improvements

- Sound effects for countdown and shooting
- Background music
- More detailed character sprites
- Multiple difficulty levels
- Wind effects that influence bullet trajectories
- Different weapons with unique ballistic properties

### Physics
- **Improve Puck Physics**  
  *Puck should go in the direction it was hit, and inertia should be applied based on where it's hit from*

`"The ball typically moves at a given velocity along the x axis, and can have "english", or more y-velocity applied depending on what part of a paddle the ball strikes, or in other versions, how much y velocity the paddle currently has."` - [Pong | Game Mechanics Wiki](https://gamemechanics.fandom.com/wiki/Pong)

<img src="https://github.com/nintanuki/pygame-air-hockey/blob/main/english.png" width="200">

- **Inertia is not working properly, no matter what value I set the ball either never slows down or stops completely**

### Issues
- **On slower speeds...**
  *Opponent "corners" the puck in the top corners of the screen*
  *Puck still gets stuck "inside" opponent, find better solution than a cooldown timer*
- **Puck speed and physics needs tweaking, buggy**
- **Player can get "stuck" on the side of the screen**
- **Puck can get "stuck" on the side of the screen**
- **Prevent opponent from hanging out in the center, limit how far down they can go**

### Game Logic
- **Improve opponent AI**  
  *AI should not just chase the puck, it should try to get above it and hit it toward the player goal*
  *AI should stop chasing the puck when it is too far so it doesn't hang out in the center when the puck is on the player side*
- **Add Pause function**
- **Add high score?**
- **Add countdown timer after each goal**

### Code Improvements
- **Implement Delta Time**
- **Separate into classes, files and implement sprites**  
  *Too many functions just for the puck right now...*

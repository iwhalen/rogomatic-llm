# Claude plays Rogue

The goal of this repo is to enable Claude to play the classic game Rogue.

It uses a modified version of the Rogue Collection that can be found here: [https://github.com/iwhalen/Rogue-Collection](https://github.com/iwhalen/Rogue-Collection)

## TODO

- Get "human mode" working that pipes commands from the terminal to the Rogue executable.
- Get "AI mode" working that has Claude generate one action per frame.
- Implement other AI modes:
    - Planning, supervisor 
    - Notepads with summaries of past actions that can be grepped
    - Outputting sequences of actions rather than one at a time

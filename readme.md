# _Anteater_

Anteater is a tool for creating drawings and animations in the terminal. Anteater is written in python using curses and has no external dependencies. Anteater was built with linux in mind, but it should work on other *unix* systems.

# Features:
- Live drawing with mouse
- Custom brushes (with various sizes)
- Multiple colors
- Selection, copying and pasting
- Undo system
- Multiple frames
- Simple to export as an animation
- Fill

# Planned Features:
- Installation options:
    - pypi
    - AUR
    - COPR
    - Nix (?)
- Different color modes (including true color)
- Gradient drawing
- Customizable character selection menus
- Unicode support
- "Magic Wand" style selection
- Optimized fill
- Configurable keyboard shortcuts
- Easier way of creating your own brushes

# Running:
Note that in order to use Anteater, it is *highly* recommended to set your "term" environment variable to xterm-1003. For example, ```export TERM=xterm-1003```. This allows your mouse movement to update real time, making the drawing experience much better. (This could also be done by making an alias for this program.)


# Current Keybinds:
(Note that these may change at any point)
- right arrow: next frame
- left arrow: last frame
- d: enter draw mode (lets you actually draw stuff)
- e: erase (enter erase mode)
- r: reset mode
- l: clear current frame
- o: export/render the animation
- z: undo
- Shift + z (Z): redo
- c: change the current character you're drawing with
- s: change the current color you're drawing with
- space: play
- o: export file (render)
- s: save file
- i: import file
- Drag with right click: select
- y: copy
- p: paste
- Ctrl + a: select all
- Shift + d (D): deselect
- Escape: quit program

# Contributing
Any sort of help is very welcome :)

# svg-pipes

Some cute, silly python code that draws pipes in SVG format made for plotting on a pen plotter.  You can change the number of tiles and the size of the SVG in the code near the top of the file(s).  It should be self-explanatory.

If the number of tiles is high (30+) in either dimension, let the computer grind for a while.  I did 80x100 or so and it took > 10 minutes for it to compute all of the connection pieces (this is the longest part - calculating how the pipes actually fit together).  That part was written by claude code.  I wrote the rest by-hand.
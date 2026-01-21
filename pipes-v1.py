#!/usr/bin/env python
# coding: utf-8

# In[1]:


import drawsvg as draw
import random
import math
stroke_width = 1
max_x_boxes=10
max_y_boxes=13

d = draw.Drawing(1500, 1500, origin='center', displayInline=False)

l_corner = draw.Group(id='l_corner', fill='white')
#l_corner.append(draw.Rectangle(-50,-50,100,100, fill='#eeeeee', stroke='red', stroke_width=stroke_width))
# pipe corner
mask = draw.Mask()
box = draw.Circle(40, 40, 10, fill='green')
mask.append(box)
# large arc
l_corner.append(draw.Arc(40,40,70,180,270,cw=True, stroke='black', stroke_width=stroke_width, fill='white'))
l_corner.append(draw.Lines(40, -30, -30, 40, 30, 40, 40, 30, fill='white', stroke='none', mask=not mask))
# small arc
l_corner.append(draw.Circle(40, 40, 10, fill='white'))  # fill in the space inside the small curve
l_corner.append(draw.Arc(40,40,10,180,270,cw=True, stroke='black', stroke_width=stroke_width, fill='none'))
#l_corner.append(draw.Arc(40,40,15,200,250, cw=True, fill='none', stroke='black', stroke_width=stroke_width))  # accent
# right rectangle
l_corner.append(draw.Rectangle(40,-35,5,70, fill='white', stroke='black', stroke_width=stroke_width))
# bottom rectangle
l_corner.append(draw.Rectangle(-35,40,70,5, fill='white', stroke='black', stroke_width=stroke_width))
# right lines
l_corner.append(draw.Rectangle(46, -29,5,58, fill='white', stroke='none'))
l_corner.append(draw.Line(45,30,50,30, fill='none', stroke='black', stroke_width=stroke_width))
l_corner.append(draw.Line(45,-30,50,-30, fill='none', stroke='black', stroke_width=stroke_width))
# bottom lines
l_corner.append(draw.Rectangle(-29, 46 ,58, 5, fill='white', stroke='none'))
l_corner.append(draw.Line(30,45,30,50, fill='none', stroke='black', stroke_width=stroke_width))
l_corner.append(draw.Line(-30,45,-30,50, fill='none', stroke='black', stroke_width=stroke_width))

# center dot
#l_corner.append(draw.Circle(0,0,3, fill='none', stroke='black', stroke_width=stroke_width)) #temp center spot

l_tube = draw.Group(id='l_tube', fill='none')
l_tube.append(draw.Rectangle(-30,-50,60,100, fill='white', stroke='none'))
l_tube.append(draw.Line(-30,-50,-30,50, fill='none', stroke='black', stroke_width=stroke_width))
l_tube.append(draw.Line(30,-50,30,50, fill='none', stroke='black', stroke_width=stroke_width))

def sdraw(ch,x,y):
    global d
    xloc = x * 100
    yloc = y * 100
    trans_string = "translate("+str(xloc)+","+str(yloc)+")"
    match ch:
        case "r":
            d.append(draw.Use(l_corner, 0,0, transform=trans_string))
        case "7":
            d.append(draw.Use(l_corner, 0,0, transform=trans_string+" rotate(90)"))
        case "j":
            d.append(draw.Use(l_corner, 0,0, transform=trans_string+" rotate(180)"))
        case "L":
            d.append(draw.Use(l_corner, 0,0, transform=trans_string+" rotate(270)")) 
        case "|":
            d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(0)"))
        case "-":
            d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(90)"))  
        case "+":
            k = random.randint(0, 1)
            if (k == 0):
                d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(0)"))
                d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(90)"))              
            else:
                d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(90)"))              
                d.append(draw.Use(l_tube, 0,0, transform=trans_string+" rotate(0)"))

# ============================================================================
# PIPE CONNECTION LOGIC
# ============================================================================

# Define which directions each pipe piece has openings
# r = down-right corner, 7 = down-left, j = up-left, L = up-right
# | = vertical, - = horizontal, + = crossover (all directions)
OPENINGS = {
    'r': {'S', 'E'},      # down and right
    '7': {'S', 'W'},      # down and left  
    'j': {'N', 'W'},      # up and left
    'L': {'N', 'E'},      # up and right
    '|': {'N', 'S'},      # vertical
    '-': {'E', 'W'},      # horizontal
    '+': {'N', 'S', 'E', 'W'},  # all directions (crossover)
}

ALL_CHARS = set(OPENINGS.keys())

def has_opening(ch, direction):
    """Check if a pipe piece has an opening in the given direction (N/S/E/W)"""
    return direction in OPENINGS.get(ch, set())

def get_compatible_neighbors(ch, direction):
    """Get all pieces that can be placed in the given direction from ch.

    For pipes to connect: if ch has an opening toward neighbor, 
    neighbor must have an opening back toward ch.
    If ch has NO opening toward neighbor, neighbor must have NO opening toward ch.
    """
    opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    opp_dir = opposite[direction]

    ch_has_opening = has_opening(ch, direction)

    compatible = set()
    for candidate in ALL_CHARS:
        candidate_has_opening = has_opening(candidate, opp_dir)
        # Both must have openings facing each other, or neither
        if ch_has_opening == candidate_has_opening:
            compatible.add(candidate)
    return compatible

def find_n(ch):
    """Characters that can be north (above) of ch"""
    return get_compatible_neighbors(ch, 'N')

def find_s(ch):
    """Characters that can be south (below) of ch"""
    return get_compatible_neighbors(ch, 'S')

def find_e(ch):
    """Characters that can be east (right) of ch"""
    return get_compatible_neighbors(ch, 'E')

def find_w(ch):
    """Characters that can be west (left) of ch"""
    return get_compatible_neighbors(ch, 'W')

# ============================================================================
# WAVE FUNCTION COLLAPSE ALGORITHM
# ============================================================================

# Define the tight 2x2 circle pattern to avoid
# Pattern: r 7
#          L j
TIGHT_CIRCLE = {
    (0, 0): 'r',  # top-left
    (1, 0): '7',  # top-right
    (0, 1): 'L',  # bottom-left
    (1, 1): 'j',  # bottom-right
}

def would_complete_tight_circle(poss_grid, x, y, ch, width, height):
    """Check if placing ch at (x,y) would complete a tight 2x2 circle.

    We check all four 2x2 squares that include position (x,y):
    - (x,y) as top-left
    - (x-1,y) as top-right
    - (x,y-1) as bottom-left
    - (x-1,y-1) as bottom-right
    """
    # Check each 2x2 square that (x,y) could be part of
    checks = [
        # (x,y) is top-left of the 2x2
        ((x, y, 'r'), (x+1, y, '7'), (x, y+1, 'L'), (x+1, y+1, 'j')),
        # (x,y) is top-right of the 2x2
        ((x-1, y, 'r'), (x, y, '7'), (x-1, y+1, 'L'), (x, y+1, 'j')),
        # (x,y) is bottom-left of the 2x2
        ((x, y-1, 'r'), (x+1, y-1, '7'), (x, y, 'L'), (x+1, y, 'j')),
        # (x,y) is bottom-right of the 2x2
        ((x-1, y-1, 'r'), (x, y-1, '7'), (x-1, y, 'L'), (x, y, 'j')),
    ]

    for square in checks:
        # Find which position in this square is (x,y)
        my_pos = None
        for (px, py, expected) in square:
            if px == x and py == y:
                my_pos = (px, py, expected)
                break

        if my_pos is None:
            continue

        # Check if ch matches what would be needed for a tight circle
        _, _, expected_ch = my_pos
        if ch != expected_ch:
            continue

        # ch matches - now check if the other 3 positions are already fixed to circle pattern
        all_fixed = True
        for (px, py, expected) in square:
            if px == x and py == y:
                continue  # skip our position
            if px < 0 or px >= width or py < 0 or py >= height:
                all_fixed = False
                break
            cell_poss = poss_grid[px][py]
            # If this cell is collapsed to the expected circle piece, it's a problem
            if len(cell_poss) == 1 and expected in cell_poss:
                continue
            # If this cell could still be something else, no tight circle yet
            all_fixed = False
            break

        if all_fixed:
            return True

    return False

def remove_tight_circle_possibilities(poss_grid, width, height):
    """Remove possibilities that would complete a tight 2x2 circle.
    Returns True if any changes were made."""
    any_changes = False
    changed = True
    while changed:
        changed = False
        for x in range(width):
            for y in range(height):
                if len(poss_grid[x][y]) <= 1:
                    continue

                to_remove = set()
                for ch in poss_grid[x][y]:
                    if would_complete_tight_circle(poss_grid, x, y, ch, width, height):
                        to_remove.add(ch)

                if to_remove and len(poss_grid[x][y] - to_remove) > 0:
                    poss_grid[x][y] -= to_remove
                    changed = True
                    any_changes = True
    return any_changes

def create_possibility_grid(width, height):
    """Create a grid where each cell contains all possible pipe pieces"""
    return [[ALL_CHARS.copy() for _ in range(height)] for _ in range(width)]

def get_constrained_possibilities(possibilities, x, y, width, height):
    """Given border constraints, return valid possibilities for a cell"""
    valid = possibilities.copy()

    # Border constraints: edges can't have openings pointing outward
    # (unless you want pipes going off-screen - set allow_edge_openings=True)
    allow_edge_openings = False

    if not allow_edge_openings:
        if x == 0:  # Left edge - no west openings
            valid = {ch for ch in valid if not has_opening(ch, 'W')}
        if x == width - 1:  # Right edge - no east openings
            valid = {ch for ch in valid if not has_opening(ch, 'E')}
        if y == 0:  # Top edge - no north openings
            valid = {ch for ch in valid if not has_opening(ch, 'N')}
        if y == height - 1:  # Bottom edge - no south openings
            valid = {ch for ch in valid if not has_opening(ch, 'S')}

    return valid

def propagate_constraints(poss_grid, width, height):
    """Propagate constraints through the grid until stable"""
    changed = True
    while changed:
        changed = False
        for x in range(width):
            for y in range(height):
                if len(poss_grid[x][y]) <= 1:
                    continue

                current = poss_grid[x][y].copy()

                # Apply border constraints
                current = get_constrained_possibilities(current, x, y, width, height)

                # Constrain based on neighbors
                # North neighbor (y-1)
                if y > 0:
                    north_possibilities = poss_grid[x][y-1]
                    valid_from_north = set()
                    for n_ch in north_possibilities:
                        valid_from_north |= find_s(n_ch)
                    current &= valid_from_north

                # South neighbor (y+1)
                if y < height - 1:
                    south_possibilities = poss_grid[x][y+1]
                    valid_from_south = set()
                    for s_ch in south_possibilities:
                        valid_from_south |= find_n(s_ch)
                    current &= valid_from_south

                # West neighbor (x-1)
                if x > 0:
                    west_possibilities = poss_grid[x-1][y]
                    valid_from_west = set()
                    for w_ch in west_possibilities:
                        valid_from_west |= find_e(w_ch)
                    current &= valid_from_west

                # East neighbor (x+1)
                if x < width - 1:
                    east_possibilities = poss_grid[x+1][y]
                    valid_from_east = set()
                    for e_ch in east_possibilities:
                        valid_from_east |= find_w(e_ch)
                    current &= valid_from_east

                if current != poss_grid[x][y]:
                    poss_grid[x][y] = current
                    changed = True

        # Also check for tight circle patterns
        if remove_tight_circle_possibilities(poss_grid, width, height):
            changed = True

def find_min_entropy_cell(poss_grid, width, height):
    """Find the cell with fewest possibilities > 1 (lowest entropy)"""
    min_entropy = float('inf')
    min_cells = []

    for x in range(width):
        for y in range(height):
            entropy = len(poss_grid[x][y])
            if 1 < entropy < min_entropy:
                min_entropy = entropy
                min_cells = [(x, y)]
            elif entropy == min_entropy:
                min_cells.append((x, y))

    if min_cells:
        return random.choice(min_cells)
    return None

def collapse_cell(poss_grid, x, y):
    """Collapse a cell to a single random possibility"""
    possibilities = list(poss_grid[x][y])
    if possibilities:
        # Weight towards more interesting pieces (corners and crosses)
        weights = []
        for ch in possibilities:
            if ch == '+':
                weights.append(2)  # Slightly favor crossovers for complexity
            elif ch in 'r7jL':
                weights.append(3)  # Favor corners for interesting paths
            else:
                weights.append(1)

        chosen = random.choices(possibilities, weights=weights, k=1)[0]
        poss_grid[x][y] = {chosen}
        return True
    return False

def wave_function_collapse(width, height, max_iterations=10000):
    """Main WFC algorithm to generate a valid pipe grid"""
    poss_grid = create_possibility_grid(width, height)

    # Apply initial border constraints
    for x in range(width):
        for y in range(height):
            poss_grid[x][y] = get_constrained_possibilities(
                poss_grid[x][y], x, y, width, height
            )

    propagate_constraints(poss_grid, width, height)

    iterations = 0
    while iterations < max_iterations:
        iterations += 1

        # Find cell with minimum entropy
        cell = find_min_entropy_cell(poss_grid, width, height)

        if cell is None:
            # All cells are collapsed or have 0 possibilities
            break

        x, y = cell

        # Collapse this cell
        if not collapse_cell(poss_grid, x, y):
            print(f"Failed to collapse cell ({x}, {y}) - contradiction!")
            return None

        # Propagate constraints
        propagate_constraints(poss_grid, width, height)

        # Check for contradictions (cells with 0 possibilities)
        contradiction = False
        for cx in range(width):
            for cy in range(height):
                if len(poss_grid[cx][cy]) == 0:
                    contradiction = True
                    break
            if contradiction:
                break

        if contradiction:
            # Restart with new random seed
            return wave_function_collapse(width, height, max_iterations)

    # Convert possibility grid to final grid
    final_grid = [['' for _ in range(height)] for _ in range(width)]
    for x in range(width):
        for y in range(height):
            if len(poss_grid[x][y]) == 1:
                final_grid[x][y] = list(poss_grid[x][y])[0]
            else:
                print(f"Warning: Cell ({x}, {y}) not fully collapsed: {poss_grid[x][y]}")
                final_grid[x][y] = random.choice(list(poss_grid[x][y])) if poss_grid[x][y] else '+'

    return final_grid

# ============================================================================
# GENERATE AND DRAW
# ============================================================================

# Generate connected pipe network using Wave Function Collapse
grid = wave_function_collapse(max_x_boxes, max_y_boxes)

if grid:
    for x in range(max_x_boxes):
        for y in range(max_y_boxes):
            sdraw(grid[x][y], x - (math.floor(max_x_boxes / 2)), y - (math.floor(max_y_boxes / 2)))

d.save_svg('pipes.svg')
d  # Display as SVG


# In[ ]:





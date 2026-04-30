import heapq

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_turning_points(path):
    if not path or len(path) < 3:
        return 0
    turns = 0
    for i in range(2, len(path)):
        p1, p2, p3 = path[i-2], path[i-1], path[i]
        dx1 = p2[0] - p1[0]
        dy1 = p2[1] - p1[1]
        dx2 = p3[0] - p2[0]
        dy2 = p3[1] - p2[1]
        if dx1 != dx2 or dy1 != dy2:
            turns += 1
    return turns

def astar(grid_obj):
    start = grid_obj.start
    goal = grid_obj.goal
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = dict()
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    
    # Keeping track of visited nodes to avoid infinite loops if stuck
    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        closed_set.add(current)
        
        for neighbor in grid_obj.get_neighbors(*current):
            if neighbor in closed_set:
                continue
                
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f = tentative_g_score + manhattan_distance(neighbor, goal)
                f_score[neighbor] = f
                
                # if not in open_set, push
                if not any(neighbor == item[1] for item in open_set):
                    heapq.heappush(open_set, (f, neighbor))

    return None

def constraint_astar(grid_obj):
    """
    Solves A* with constraints to pick up all fruits.
    State representation: (x, y, frozenset(collected_fruits))
    """
    start = grid_obj.start
    goal = grid_obj.goal
    required_items = tuple(sorted(list(grid_obj.fruits)))
    
    start_state = (start[0], start[1], tuple())
    
    # We calculate distance to uncollected nearest fruits + goal?
    # Simple heuristic: dist(current, goal) + sum(dist(current, uncollected)) - but can overestimate.
    # Safe heuristic: sum min distance to uncollected + distance to goal. We can just use manhattan to nearest fruit if uncollected, else to goal.
    def heuristic(state):
        current_pos = (state[0], state[1])
        collected = set(state[2])
        uncollected = set(required_items) - collected
        if not uncollected:
            return manhattan_distance(current_pos, goal)
            
        # Very simple heuristic: distance to closest uncollected fruit
        min_fruit_dist = min(manhattan_distance(current_pos, fruit) for fruit in uncollected)
        return min_fruit_dist # Admissible, as it must at least travel to nearest fruit.
        
    open_set = []
    heapq.heappush(open_set, (0, start_state))
    came_from = dict()
    g_score = {start_state: 0}
    
    f_score = {start_state: heuristic(start_state)}

    closed_set = set()
    search_history = []

    while open_set:
        current_state = heapq.heappop(open_set)[1]
        current_pos = (current_state[0], current_state[1])
        collected = set(current_state[2])
        
        search_history.append(current_pos)

        if current_pos == goal and set(required_items) == collected:
            # Reconstruct sequence of points
            path = []
            curr = current_state
            while current_state in came_from:
                path.append((current_state[0], current_state[1]))
                current_state = came_from[current_state]
            path.append((start_state[0], start_state[1]))
            path.reverse()
            return path, search_history
            
        closed_set.add(current_state)

        for neighbor in grid_obj.get_neighbors(*current_pos):
            new_collected = set(collected)
            if neighbor in required_items:
                new_collected.add(neighbor)
                
            neighbor_state = (neighbor[0], neighbor[1], tuple(sorted(list(new_collected))))
            
            if neighbor_state in closed_set:
                continue
                
            tentative_g_score = g_score[current_state] + 1
            if tentative_g_score < g_score.get(neighbor_state, float('inf')):
                came_from[neighbor_state] = current_state
                g_score[neighbor_state] = tentative_g_score
                f = tentative_g_score + heuristic(neighbor_state)
                f_score[neighbor_state] = f
                
                # Check directly in heapq list for performance? (Slow for tuples, but fine for small mazes) # TODO: could use dictionary
                in_open = False
                for item in open_set:
                    if item[1] == neighbor_state:
                         in_open = True
                         break
                         
                if not in_open:
                    heapq.heappush(open_set, (f, neighbor_state))

    return None, search_history


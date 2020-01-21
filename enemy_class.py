import pygame
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()

    def update(self):
        self.target = self.set_target()
        if self.target is not self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def set_speed(self):
        if self.personality in ["speedyBFS_R", "speedyBFS_L"]:
            speed = 1.25
        else:
            speed = 1
        return speed

    def set_target(self):
        return self.app.player.grid_pos

    def time_to_move(self):
        # It is time to move when the enemy is in the centre of a cell
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.get_BFS_path_direction(self.target)

    def get_BFS_path_direction(self, target):
        next_cell = self.find_next_cell_in_path_BFS(target)
        x_direction = next_cell[0] - self.grid_pos[0]
        y_direction = next_cell[1] - self.grid_pos[1]
        return vec(x_direction, y_direction)

    def find_next_cell_in_path_BFS(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [int(target[0]), int(target[1])])
        # Return first position after the current position
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                # Create different favorable directions for different enemies
                if self.personality in ["speedyBFS_R", "slowBFS_R"]:
                    neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]] #Right-Down-Left-Up
                else:
                    neighbours = [[0, 1], [-1, 0], [0, -1], [1, 0]] #Left-Up-Right-Down
                for neighbour in neighbours:
                    # Check if the neighbour is in the grid
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                # Check if the next_cell is not a wall
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.app.cell_height//2)

    def set_colour(self):
        if self.number == 0:
            return ENEMY_BLUE
        if self.number == 1:
            return ENEMY_PURPLE
        if self.number == 2:
            return ENEMY_RED
        if self.number == 3:
            return ENEMY_GREEN

    def set_personality(self):
        if self.number == 0:
            return "speedyBFS_R"
        elif self.number == 1:
            return "slowBFS_R"
        elif self.number == 2:
            return "speedyBFS_L"
        else:
            return "slowBFS_L"

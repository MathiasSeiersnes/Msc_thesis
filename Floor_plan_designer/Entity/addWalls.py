from Entity.Wall import Wall

class addWalls:
    def __init__(self, file, rooms):
        self.file = file
        self.rooms = rooms
        self.common = []

    def create(self):
        overlaps = self.check(self.rooms)
        walls = []
        wall_centers = []

        for wall in overlaps:
            if wall is not None:
                # Calculate wall center
                x1, y1 = wall[0]
                x2, y2 = wall[1]
                wall_center = ((x1 + x2) / 2, (y1 + y2) / 2)
                
                # Calculate wall length (Euclidean distance)
                wall_length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
                if wall_length < 200:
                    continue  # Skip if wall is too short

                # Check if wall with similar center already exists
                duplicate = False
                for center in wall_centers:
                    if abs(center[0] - wall_center[0]) <= 500 and abs(center[1] - wall_center[1]) <= 500:
                        duplicate = True
                        break

                if not duplicate:
                    walls.append(wall)
                    wall_centers.append(wall_center)

        for wall in walls:
            self.file = Wall(self.file, wall[0], wall[1]).create()
        return self.file

    def walls(self, room):
        x, y, lX, lY = room[:4]
        walls = []
        for i in range(4):
            x1 = [x, x, x, x+lX]
            y1 = [y, y, y+lY, y]
            l = [lX, lY, lX, lY]
            walls.append([x1[i], y1[i], i % 2, l[i]])
        return walls

    def check(self, rooms):
        overlaps = []
        for i in range(len(rooms)):
            walls = self.walls(rooms[i])
            for j in range(len(rooms)):
                if i != j:
                    check = self.walls(rooms[j])
                    for k in range(len(walls)):
                        overlaps.append(self.overlap(walls[k], check[k % 2]))
                        overlaps.append(self.overlap(walls[k], check[k % 2 + 2]))
        return overlaps

    def overlap(self, edge1, edge2):
        direction = edge1[2]
        if abs(edge1[1 - direction] - edge2[1 - direction]) > 500:
            return
        elif (edge1[direction] >= (edge2[direction] + edge2[3])) or (edge2[direction] >= (edge1[direction] + edge1[3])):
            return
        else:
            start = max(edge1[direction], edge2[direction])
            stop = min(edge1[direction] + edge1[3], edge2[direction] + edge2[3])
            if direction == 0:
                return [[start, edge1[1]], [stop, edge1[1]]]
            else:
                return [[edge1[0], start], [edge1[0], stop]]

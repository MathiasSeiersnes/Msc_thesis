class KBE:
    def __init__(self, num_rooms, boundary):
        self.num_rooms = num_rooms
        self.boundary = boundary

    def run(self):    
        top = (self.num_rooms-1)//2
        bottom = self.num_rooms - top -1
        
        height = float(self.boundary[3]-500)
        width_top = (self.boundary[2]-self.boundary[0])/top
        width_bottom = (self.boundary[2]-self.boundary[0])/bottom
        
        rooms = [[float(self.boundary[0]), -500.0, float(self.boundary[2]-self.boundary[0]), 1000.0]]
        
        for i in range(top):
            x = float(i*width_top+self.boundary[0])
            y = 500.0
            room = [x, y, float(width_top), height]
            rooms.append(room)
            
        for i in range(bottom):
            x = float(i*width_bottom+self.boundary[0])
            y = float(self.boundary[1])
            room = [x, y, float(width_bottom), height]
            rooms.append(room)
        
        
        for i, room in enumerate(rooms):
            prov = room
            if room[1] == self.boundary[1]:
                prov.append(1)
                prov.append(room[2]/2-500.0+room[0]-self.boundary[0])
                prov.append(3)
                prov.append(room[2]/2-250.0+room[0])
            elif room[1] + room[3] == self.boundary[3]:
                prov.append(3)
                prov.append(room[2]/2-500.0+room[0]-self.boundary[0])
                prov.append(1)
                prov.append(room[2]/2-750.0+room[0])
            else:
                prov.append(0)
                prov.append(0.0)
                prov.append(0)
                prov.append(0.0)
            rooms[i] = prov
    
        return rooms


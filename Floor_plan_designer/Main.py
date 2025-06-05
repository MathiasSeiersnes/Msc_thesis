import ifcopenshell

from Entity.Window import Window
from Entity.Room import Room
from Entity.addWalls import addWalls
from Entity.Door import Door

from Control.NSGA_3 import NSGA_3
from Control.KBE import KBE


#FOUR IFC TEMPLATES ARE USED FOR TESTING: 5x13, 7x5, 8x9, 11x7, all in meters

num_rooms = 4
building = [11, 7] #selecting which template to use
path = 'YOURPATHHERE' #Path to this folder
pop_size, n_gen = 500, 1000

IFC_str = "IFC_Template\\" + str(building[0]) + "x" + str(building[1]) + ".ifc"
ifc_file = ifcopenshell.open(path+IFC_str)

boundary = [-building[0]*500, -building[1]*500, building[0]*500, building[1]*500]


rooms = KBE(num_rooms, boundary).run()
before = rooms #defining a variable as the rooms created by the KBE system,
#due to windows not being optimized in the proof of concept algorithm

#Restructuring the room data to fit as a sample for the NSGA-3 algorithm 
sample = []
for i, room in enumerate(rooms):
    for item in room:
        if isinstance(item, float):
            sample.append(item)
     
algo = NSGA_3(sample, boundary, pop_size, n_gen)
res = algo.run()

F = res.F
X = res.X

idx_0 = min(enumerate(F), key=lambda x: x[1][0])[0]
idx_1 = min(enumerate(F), key=lambda x: x[1][1])[0]
idx_2 = min(enumerate(F), key=lambda x: x[1][2])[0]

result0 = X[idx_0].reshape(-1, 6)
midt = int(len(X)/2)
result1 = X[idx_1].reshape(-1, 6)
result2 = X[idx_2].reshape(-1, 6)

results_all = [result0, result1, result2]


for j, results in enumerate(results_all):
    ifc_file = ifcopenshell.open(path+IFC_str)

    # Find and print all objects
    for obj in ifc_file.by_type("IfcProduct"):
        if obj.is_a() == "IfcRoof": 
            ifc_file.remove(obj) #Removing the roof for the floor plan to be visible
        elif obj.is_a() == "IfcWall":
            outer_wall = obj
    rooms = []
    for i, result in enumerate(results):
        room = []
        for num in result:
            room.append(float(num))
        room.append(float(num))
        room.append(float(num))
        room[5] = room[4]
        room[4] = before[i][4]
        room[6] = before[i][6]
        rooms.append(room)
    
    
    for room in rooms:
        ifc_file = Room(ifc_file, room).create()
        if room[4] != 0:   
            ifc_file = Window(ifc_file, outer_wall, room[4], room[5], boundary).create()
    
    
    ifc_file = addWalls(ifc_file, rooms).create()
    
    
    for room in rooms:
        x = room[7]
        if room[6] == 1:
            y = room[1]
        else:
            y = room[1] + room[3]
        diff = 10**6
        for obj in ifc_file.by_type("IfcProduct"):
            if obj.is_a() == "IfcWall":
                placement = obj.ObjectPlacement
                # Get the coordinates of the wall origin
                location = placement.RelativePlacement.Location.Coordinates
                xw, yw = location[0], location[1]
                
                check = abs(x-xw) + abs(y-yw)
                if check < diff:
                    diff = check
                    wall = obj
        ifc_file = Door(ifc_file, wall, [0.0, 0.0]).create()
                    
    ifc_file.write(path+"Floor_plan_" +  str(j+1) + ".ifc")

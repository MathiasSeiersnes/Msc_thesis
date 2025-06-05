import numpy as np

from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling


class NSGA_3:
    def __init__(self, kbe_plan, boundary, pop_size=500, n_gen=500):
        self.kbe_plan = kbe_plan
        self.pop_size = pop_size
        self.n_gen = n_gen
        self.boundary = boundary
        
    def run(self):
        ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)
        algorithm = NSGA3(pop_size=self.pop_size, ref_dirs=ref_dirs, sampling=Sampling(self.kbe_plan))
        
        res = minimize(
            FloorPlanProblem(int(len(self.kbe_plan)/6), self.boundary),
            algorithm,
            termination=('n_gen', self.n_gen),
            verbose=False,# Run for 200 generations
    
        )
        
        return res
        
        
class Sampling(Sampling):
    def __init__(self, initial_solution):
        super().__init__()
        self.initial_solution = initial_solution

    def _do(self, problem, n_samples, **kwargs):
        # Repeat the initial solution to match population size if needed
        return np.tile(self.initial_solution, (n_samples, 1))



class FloorPlanProblem(Problem):
    def __init__(self, num, boundary):
        self.num_rooms = num
        self.boundary = boundary
        self.room_vars = 6 * num
        
        super().__init__(
            n_var=self.room_vars,            # Number of decision variables
            n_obj=3,            # Number of objectives
            n_constr=2,         # No constraints
            xl=[boundary[0], boundary[1], 1, 1, 0, boundary[0]] * num,   # Lower bounds
            xu=[boundary[2], boundary[3], - boundary[0] + boundary[2], - boundary[1] + boundary[3], boundary[2]-boundary[0], boundary[2]] * num    # Upper bounds
        )

    def _evaluate(self, X, out, *args, **kwargs):
        labels = [0, 1, 2, 3, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]*5
        
        rooms = X.reshape(-1, self.num_rooms, 6)
        
        tot_area = (self.boundary[2]-self.boundary[0])*(self.boundary[3]-self.boundary[1])
        tot_room_area = np.zeros(len(rooms))
        
        smallest = np.zeros(len(rooms))
        largest = np.zeros(len(rooms))
        room_info = np.zeros((len(rooms), self.num_rooms, 2))
        for i, plan in enumerate(rooms):
            smallest[i] = 10**10
            for j, room in enumerate(plan):
                area = room[2]*room[3]
                tot_room_area[i] += area
                if area < smallest[i]:
                    smallest[i] = area
                elif area > largest[i]:
                    largest[i] = area
                room_info[i][j][0] = area
                room_info[i][j][1] = labels[j]
        
        overlaps = []
        for i in range(self.num_rooms):
            for j in range(i + 1, self.num_rooms):
                overlaps.append(self.calculate_overlap(rooms[:, i], rooms[:, j]))
        
        f1 = abs(tot_area - tot_room_area)
        f2 = np.sum(overlaps, axis=0)/100
        
        feil = np.zeros(len(room_info))
        for i, plan in enumerate(room_info):
            for j, room in enumerate(plan):
                if room[1] == 0:
                    if room[0] < largest[i]:
                        feil[i] += 100
                elif room[1] == 1:
                    if room[0] > 8*10**6:
                        feil[i] += 100
                elif room[1] == 2:
                    if (rooms[i][j][2] or rooms[i][j][3]) < 2000:
                        feil[i] += 100
                if rooms[i][j][2] < 1500 or rooms[i][j][3] < 1500:
                    feil[i] += 100
        
        f3 = feil*100
        
        g1 = self.check_out_of_bounds(rooms)  # Rooms must fit inside the boundary
        
        min_area = 1000*2000
        g2 = min_area-smallest
        
        out["F"] = np.column_stack([f1, f2, f3])
        out["G"] = np.column_stack([g1, g2])  # Combine constraints
        
    def calculate_overlap(self, room1, room2):
        # Calculate overlap between two rooms
        x_overlap = np.maximum(0, np.minimum(room1[:, 0] + room1[:, 2], room2[:, 0] + room2[:, 2]) -
                               np.maximum(room1[:, 0], room2[:, 0]))
        y_overlap = np.maximum(0, np.minimum(room1[:, 1] + room1[:, 3], room2[:, 1] + room2[:, 3]) -
                               np.maximum(room1[:, 1], room2[:, 1]))
        return x_overlap * y_overlap  # Overlap area

    def check_out_of_bounds(self, rooms):
        # Check if any room exceeds the boundary
        x_min_violation = np.maximum(0, self.boundary[0] - rooms[:, :, 0])
        y_min_violation = np.maximum(0, self.boundary[1] - rooms[:, :, 1])
        x_max_violation = np.maximum(0, rooms[:, :, 0] + rooms[:, :, 2] - (self.boundary[2]))
        y_max_violation = np.maximum(0, rooms[:, :, 1] + rooms[:, :, 3] - (self.boundary[3]))
        return np.sum(x_min_violation + y_min_violation + x_max_violation + y_max_violation, axis=1)
        
        

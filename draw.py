from Tkinter import *
import random as rand


class App:

    def __init__(self, master):

        canvas_size = (400, 150)
        car_size = 10                                # height & width of car square
        lane_buffer = 2                              # space between car and white lines
        lane_width = car_size + lane_buffer * 2        # width of each lane
        lane_count = (2, 2)                          # lanes in each direction
        road_width = lane_width * sum(lane_count) + (1 * (sum(lane_count) - 1))  # total road width, +1 to account for lines between lanes
        c_h_mid = canvas_size[0] / 2
        c_v_mid = canvas_size[1] / 2
        road_bottom = c_v_mid - ((road_width / 2) + 1)  # +1 for lines between lanes
        road_top = c_v_mid + ((road_width / 2) + 1)  # +1 for lines between lanes
        spawn_locs = []

        self.master = master
        self.canvas_size = canvas_size
        self.c = Canvas(self.master, width=self.canvas_size[0], height=self.canvas_size[1], background="palegreen1", highlightthickness=0)
        self.c.create_rectangle(0, road_bottom, self.canvas_size[0], road_top, fill="dark gray", width=0, tags="road")  # road

        # lanes
        for i in range(1, sum(lane_count) + 1):
            v_loc = road_bottom + ((lane_width + 1) * i) - (lane_width / 2)
            if i <= lane_count[0]:
                direction = 1
                h_loc = car_size / 2
            else:
                direction = -1
                h_loc = canvas_size[0] - (car_size / 2)

            spawn_locs.append({
                'loc': (h_loc, v_loc),
                'dir': direction,
                'ovl': (h_loc - ((car_size / 2) * direction), v_loc - car_size / 2, h_loc + (((car_size / 2) + car_size) * direction), v_loc + car_size / 2)
            })
        self.spawn_locs = spawn_locs

        # lane dividers
        for i in range(1, sum(lane_count)):
            v_loc = road_bottom + (lane_width + 1) * i
            fill_color = "yellow" if (i == lane_count[0]) else "white smoke"
            self.c.create_line(0, v_loc, self.canvas_size[0], v_loc, fill=fill_color, dash=(4, 4), tags="road")

        self.cars = {}

        self.c.pack()
        self.animate()

    def move(self):
        for i, car in self.cars.iteritems():
            coo = self.c.coords(i)

            # delete the car if moves out of canvas
            if coo[2] > self.canvas_size[0]+10 or coo[0] < -10:
                self.c.delete(i)
                del self.cars[i]
                return

            # slow the car down if it's approaching a slower car (remove the road objects)
            car_in_front_id = set(self.c.find_overlapping(coo[0]+11*car['dir'], coo[1], coo[2]+11*car['dir'], coo[3])) - set(self.c.find_withtag("road"))
            if len(car_in_front_id) > 0:
                car['speed'] = self.cars[car_in_front_id.pop()]['speed']
                self.c.itemconfig(i, fill="red")

            self.c.move(i, car['speed'] * car['dir'], 0)

    def spawn(self):
        for l in self.spawn_locs:
            bound = l['ovl']
            if len(self.c.find_overlapping(bound[0], bound[1], bound[2], bound[3])) == 1:
                if rand.gammavariate(1, 1) > 3.2:
                    car_id = self.c.create_rectangle(l['loc'][0]-5, l['loc'][1]-5, l['loc'][0]+5, l['loc'][1]+5, fill="blue")
                    self.cars[car_id] = {
                        'speed': rand.uniform(0.7, 1.3),
                        'dir': l['dir']
                    }

    def animate(self):
        self.spawn()
        self.move()
        self.master.after(10, self.animate)


root = Tk()
app = App(root)
root.mainloop()
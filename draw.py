from Tkinter import *
import random as rand


class App:

    def __init__(self, master):

        # initializing variables
        self.canvas_size = (410, 200)
        self.car_size = 10                                # height & width of car square
        self.lane_buffer = 2                              # space between car and white lines
        self.lane_count = (2, 2)                               # lanes in each direction

        # calculated variables
        self.lane_width = self.car_size + self.lane_buffer * 2  # width of each lane
        self.road_width = self.lane_width * sum(self.lane_count) + (1 * (sum(self.lane_count) - 1))  # total road width, +1 to account for lines between lanes
        self.c_v_mid = self.canvas_size[1] / 2
        self.road_bottom = self.c_v_mid - ((self.road_width / 2) + 1)  # +1 for lines between lanes
        self.spawn_locs = []

        self.master = master
        self.c = Canvas(self.master, width=self.canvas_size[0], height=self.canvas_size[1], background="palegreen1", highlightthickness=0)

        # lanes
        lane_locs = self._find_lane_locs()

        for i, loc_bottom in enumerate(lane_locs[:-1]):
            fill_color = "yellow" if i == self.lane_count[0] else "white smoke"
            self.c.create_rectangle(0, loc_bottom, self.canvas_size[0], loc_bottom + self.lane_width + 1, fill="dark gray", width=0, tags="road")
            if i > 0:
                self.c.create_line(0, loc_bottom, self.canvas_size[0], loc_bottom, fill=fill_color, dash=(8, 8), tags="road")

            v_loc = loc_bottom + 1 + (self.lane_width / 2)
            if i < self.lane_count[0]:
                direction = -1
                h_loc = self.canvas_size[0] - (self.car_size / 2)
            else:
                direction = 1
                h_loc = self.car_size / 2

            self.spawn_locs.append({
                'loc': (h_loc, v_loc),
                'dir': direction,
                'ovl': (
                    h_loc - ((self.car_size / 2) * direction),
                    v_loc - self.car_size / 2,
                    h_loc + (((self.car_size / 2) + self.car_size) * direction),
                    v_loc + self.car_size / 2
                )})

        self.cars = {}

        self.c.pack()
        self.c.bind("<Motion>", self.halt)
        self.c.bind("<Leave>", self.resume)

        self.infobox = self.c.create_text(5, 5, anchor="nw")
        self.animate()

    def _find_lane_locs(self):
        width = self.car_size + (self.lane_buffer * 2) + 1
        count = sum(self.lane_count)
        bottom = (self.canvas_size[1] / 2) - ((width * count) + 1) / 2  # extra +1 is for the top border... each lane
                                                                        # has a bottom border, the very top lane has a
                                                                        # top border as well
        return range(bottom, bottom + (width * count) + 1, width)

    def halt(self, e):
        self.c.after_cancel(self.after_id)
        items = self.c.find_overlapping(e.x, e.y, e.x + 1, e.y + 1)
        found = 0
        for item in items:
            if "car" in self.c.gettags(item):
                found = 1
                self.show_stats(item)
        if found == 0:
            self.clear_stats()

    def resume(self, e):
        self.animate()

    def show_stats(self, car_id):
        self.c.itemconfig(self.infobox, text="speed: " + ("%1.2f" % self.cars[car_id]['speed']) + "\ndir: " + ("%1d" % self.cars[car_id]['dir']))

    def clear_stats(self):
        self.c.itemconfig(self.infobox, text="")

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
                    car_id = self.c.create_rectangle(l['loc'][0] - 5, l['loc'][1] - 5, l['loc'][0] + 5, l['loc'][1] + 5, fill="blue", activefill="yellow", tags="car")
                    self.cars[car_id] = {
                        'speed': rand.uniform(0.7, 1.3),
                        'dir': l['dir']
                    }

    def animate(self):
        self.spawn()
        self.move()
        self.after_id = self.master.after(15, self.animate)


root = Tk()
app = App(root)
root.mainloop()
# -*- coding: utf-8 -*-

from builtins import map, range, object
from tkinter import *
import random as rand
import math


class App(object):

    def __init__(self, master):

        # initializing variables
        self.canvas_size = (810, 200)
        self.car_size = 10                              # height & width of car square
        self.lane_buffer = 2                            # space between car and white lines
        self.lane_count = (2, 2)                        # lanes in each direction
        self.spawn_freq = 4.0                           # how often cars come around
        self.car_colors = {
            'normal': 'blue',
            'grumpy': 'red',
        }
        self.cars = {}

        # calculated variables
        self.lane_width = self.car_size + self.lane_buffer * 2  # width of each lane
        self.road_width = self.lane_width * sum(self.lane_count) + (1 * (sum(self.lane_count) - 1))  # total road width, +1 to account for lines between lanes
        self.c_v_mid = self.canvas_size[1] // 2
        self.road_bottom = self.c_v_mid - ((self.road_width // 2) + 1)  # +1 for lines between lanes
        self.spawn_locs = []

        self.master = master
        self.c = Canvas(self.master, width=self.canvas_size[0], height=self.canvas_size[1], background="palegreen1", highlightthickness=0)

        # lanes
        lane_locs = self._find_lane_locs()
        lane_tags = self._find_lane_tags()

        for i, loc_bottom in enumerate(lane_locs[:-1]):
            fill_color = "yellow" if i == self.lane_count[0] else "white smoke"
            self.c.create_rectangle(0, loc_bottom, self.canvas_size[0], loc_bottom + self.lane_width + 1, fill="dark gray", width=0, tags="road %s" % (lane_tags[i]))
            if i > 0:
                self.c.create_line(0, loc_bottom, self.canvas_size[0], loc_bottom, fill=fill_color, dash=(8, 8), tags="road")

            v_loc = loc_bottom + 1 + (self.lane_width // 2)
            if i < self.lane_count[0]:
                direction = -1
                h_loc = self.canvas_size[0] - (self.car_size // 2)
            else:
                direction = 1
                h_loc = self.car_size // 2

            self.spawn_locs.append({
                'loc': (h_loc, v_loc),
                'dir': direction,
                'ovl': (
                    h_loc - ((self.car_size // 2) * direction),
                    v_loc - self.car_size // 2,
                    h_loc + (((self.car_size // 2) + self.car_size) * direction),
                    v_loc + self.car_size // 2
                )})

        self.c.pack()                                   # resize window to fit our widgets
        self.c.bind("<Motion>", self.halt)
        self.c.bind("<Leave>", self.resume)
        self.infobox = self.c.create_text(5, 5, anchor="nw")
        self.animate()

    def _find_lane_locs(self):
        # helper function to identify lane coordinates on the canvas. Specifically, find the lower bound of each lane
        width = self.car_size + (self.lane_buffer * 2) + 1
        count = sum(self.lane_count)
        bottom = (self.canvas_size[1] // 2) - ((width * count) + 1) // 2  # extra +1 is for the top border... each lane
                                                                        # has a bottom border, the very top lane has a
                                                                        # top border as well
        return list(range(bottom, bottom + (width * count) + 1, width))

    def _find_lane_tags(self):
        # helper function to create the tags to be assigned to each lane
        lc = self.lane_count
        t = []
        for l in range(0, sum(lc)):
            l1 = 1 if l < lc[0] else 2
            l2 = l+1 if l < lc[0] else sum(lc) - l
            t.append('%i_%i' % (l1, l2))
        return t

    def _get_lane_tags(self, car_id):
        # logic for getting current lanes. First subtract sets, then convert to tuple (gettags needs tuple input), then
        # remove the "road" set
        coo = self.c.coords(car_id)
        l = set(self.c.find_overlapping(coo[0], coo[1], coo[2], coo[3])) - set(self.c.find_withtag("car"))
        l = self.c.gettags(tuple(l))
        return tuple(set(l) - {'road', })

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
        speed = self.cars[car_id]['speed']
        dir = math.degrees(math.acos(self.cars[car_id]['dir']))
        lane = ', '.join(self._get_lane_tags(car_id))
        self.c.itemconfig(
            self.infobox,
            text="id: " + ("%d" % car_id) + "\n" +
                 "speed: " + ("%1.2f" % speed) + "\n" +
                 "dir: " + ("%1d" % dir) + "°" + "\n" +
                 "lane: " + ("%s" % lane))

    def clear_stats(self):
        self.c.itemconfig(self.infobox, text="")

    def move(self):
        for i, car in list(self.cars.items()):
            coo = self.c.coords(i)

            # delete the car if moves out of canvas
            if coo[2] > self.canvas_size[0]+10 or coo[0] < -10:
                self.c.delete(i)
                del self.cars[i]
                return

            # slow the car down if it's approaching a slower car (remove the road objects)
            car_in_front_id = set(self.c.find_overlapping(coo[0] + (self.car_size + 1) * car['dir'],
                                                          coo[1],
                                                          coo[2] + (self.car_size + 1) * car['dir'],
                                                          coo[3])
                                  ) - set(self.c.find_withtag("road"))
            if len(car_in_front_id) > 0:
                car['speed'] = self.cars[car_in_front_id.pop()]['speed']
                self.c.itemconfig(i, fill=self.car_colors['grumpy'])

            # if car is slowed down, chance to change lanes... first try pass on left, then try pass on right
            if car['speed'] != car['happy_speed'] and (car['mdir'] in (0, math.pi)):
                l = list(map(int, self._get_lane_tags(i)[0].split('_')))
                # does lane exist?
                next_lane = '%i_%i' % (l[0], l[1] + 1)
                if self.c.gettags(next_lane):
                    # bounding box for lane changes not being drawn correctly. Steps I should code in:
                    #  1. find the direction car moving (i.e., front of car)
                    #  2. find the lane I'm moving to (left or right)
                    #  3. draw the box based on those (from front of car + buffer to 3x car behind)
                    # is a car there now?
                    # box in car back = 2x car width + buffer, front of car = car buffer (1x car length)
                    coo_new = []
                    coo_new.append(coo[0] - self.car_size if car['dir'] == -1 else coo[0] - self.car_size * 1.5)
                    coo_new.append(coo[1] + self.lane_width * (-1 if car['dir'] == 1 else 1))
                    coo_new.append(coo[2] + self.car_size if car['dir'] == 1 else coo[2] + self.car_size * 1.5)
                    coo_new.append(coo[3] + self.lane_width * (-1 if car['dir'] == 1 else 1))
                    cars_in_the_way = set(self.c.find_overlapping(coo_new[0], coo_new[1], coo_new[2], coo_new[3])) - set(self.c.find_withtag("road"))
                    if not(cars_in_the_way):
                        car['moving_to_lane'] = next_lane
                        car['mdir'] = car['mdir'] - math.pi//6

            # if finished changing lanes, reset direction
            if car['speed'] != car['happy_speed']\
                    and car['mdir'] not in (0, math.pi)\
                    and (self._get_lane_tags(i) == (car['moving_to_lane'],)):
                car['mdir'] = math.acos(car['dir'])
                car['moving_to_lane'] = ''
                car['speed'] = car['happy_speed']
                self.c.itemconfig(i, fill=self.car_colors['normal'])

            self.c.move(i, round(car['speed'] * math.cos(car['mdir']), 4), round(car['speed'] * math.sin(car['mdir']), 4))

    def spawn(self):
        # function to create new cars
        for l in self.spawn_locs:
            bound = l['ovl']
            # only create a new car if I didn't just create one (i.e., if a car isn't already in the spawn location)
            if len(self.c.find_overlapping(bound[0], bound[1], bound[2], bound[3])) == 1:
                if rand.gammavariate(1, 1) > self.spawn_freq:
                    car_id = self.c.create_rectangle(l['loc'][0] - 5, l['loc'][1] - 5, l['loc'][0] + 5, l['loc'][1] + 5, fill=self.car_colors.get('normal'), activefill="yellow", tags="car")
                    speed = rand.uniform(0.7, 1.3)
                    self.cars[car_id] = {
                        'speed': speed,
                        'happy_speed': speed,
                        'dir': l['dir'],
                        'mdir': math.acos(l['dir']),
                        'modified': False,
                        'moving_to_lane': '',
                    }

    def animate(self):
        self.spawn()
        self.move()
        self.after_id = self.master.after(15, self.animate)


root = Tk()
app = App(root)
root.mainloop()

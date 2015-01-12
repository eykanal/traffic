from Tkinter import *
import random as rand


class App:

    def __init__(self, master):

        self.master = master
        self.canvasSize = (300, 100)
        self.c = Canvas(self.master, width=self.canvasSize[0], height=self.canvasSize[1], background="palegreen1", highlightthickness=0)
        self.c.create_rectangle(0, 36, self.canvasSize[0], 64, fill="dark gray", width=0, tags="road")  # road
        self.c.create_line(0, 50, self.canvasSize[0], 50, fill="white smoke", dash=(4, 4), tags="road")  # dotted line in road
        self.c.pack()

        self.spawnlocs = (
            {
                'loc': (5, 43),
                'dir': 1,
                'ovl': (0, 38, 20, 48)
            }, {
                'loc': (self.canvasSize[0]-6, 57),
                'dir': -1,
                'ovl': (self.canvasSize[0]-20, 52, self.canvasSize[0], 62)})
        self.cars = {}

        self.animate()

    def move(self):
        for i, car in self.cars.iteritems():
            coo = self.c.coords(i)

            # delete the car if moves out of canvas
            if coo[2] > self.canvasSize[0]+10 or coo[0] < -10:
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
        for l in self.spawnlocs:
            bound = l['ovl']
            if len(self.c.find_overlapping(bound[0], bound[1], bound[2], bound[3])) == 1:
                if rand.gammavariate(1, 1) > 3.2:
                    car_id = self.c.create_rectangle(l['loc'][0]-5, l['loc'][1]-5, l['loc'][0]+5, l['loc'][1]+5, fill="blue")
                    self.cars[car_id] = {
                        'speed': rand.uniform(0.7, 1.3),
                        'dir': l['dir']}

    def animate(self):
        self.spawn()
        self.move()
        self.master.after(10, self.animate)


root = Tk()
app = App(root)
root.mainloop()
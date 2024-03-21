from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')


class Plotter:

    def __init__(self, canvas):
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = canvas.TKCanvas
        self.max_t = 5*60
        self.i_min = 0

    def draw_figure(self, canvas, figure):
        tkcanvas = FigureCanvasTkAgg(figure, canvas)
        tkcanvas.draw()
        tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        return tkcanvas

    def first_draw(self, probsCount):
        self.axis = self.fig.add_subplot(111)
        self.lines = []
        for i in range(probsCount):
            line, = self.axis.plot([], [], label="Sens. {}".format(i+1))
            self.lines.append(line)
        self.tkcanvas = self.draw_figure(self.canvas, self.fig)

        self.axis.set_xlim(- self.max_t, 0)
        self.axis.set_xlabel("Time [s]")
        self.axis.legend(loc='upper left')

    def update_data(self, data):

        current_t = datetime.now().timestamp()
        times = np.array([d[0].timestamp() - current_t for d in data])
        i_max = len(times)
        i_min = max(self.i_min, np.min(np.where(times > -self.max_t)[0]))

        for i in range(len(self.lines)):
            self.lines[i].set_data(
                [times[i_min:i_max], [d[i*2+1] for d in data[i_min:i_max]]])  # update data

        # print("Plotting {} data".format(i_max-i_min))

        self.axis.relim()  # scale the y scale
        self.axis.autoscale_view()  # scale the y scale
        self.tkcanvas.draw()

    def reset(self, data):
        self.i_min = len(data)

# class Plotter():
#     def __init__(self, canvas) -> None:
#         self.fig_agg = None
#         self.figure = None
#         self.canvas = canvas.TKCanvas

#         # plt.ioff()

#     def draw_figure(self):
#         print("Drawing")
#         self.figure_canvas_agg = FigureCanvasTkAgg(self.figure, self.canvas)
#         self.figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
#         self.figure_canvas_agg.draw()
#         return self.figure_canvas_agg


#     def first_plot(self):
#         self.fig = matplotlib.figure.Figure()
#         self.axis = self.fig.add_subplot(111)
#         # ax.set_xlabel("X axis")
#         # ax.set_ylabel("Y axis")
#         # ax.grid()
#         self.line = self.axis.plot( [1,2,3], [4,5,6] )[0]
#         self.fig_agg = self.draw_figure()

#     def update_data(self, data):
#         self.line.set_data( *self.parse_data( data ) )
#         self.fig_agg.draw()

#     # def plot(self, data):
#     #     self.figure_controller( *self.parse_data( data ) )
#     #     self.figure_drawer()

#     def parse_data( self, data ):
#         current_t = datetime.now().timestamp()
#         return [ d[0].timestamp() - current_t for d in data ], [ d[1] for d in data ]

#     #put all of your normal matplotlib stuff in here
#     def figure_controller(self, xs, ys ):
#         #first run....
#         if self.figure is None:
#             self.figure = plt.figure()
#             self.axes = self.figure.add_subplot(111)
#             self.line, = self.axes.plot( xs, ys )
#             self.axes.set_xlim( -5*60, 0 )
#         #all other runs
#         else:
#             self.line.set_data(xs, ys)#update data
#             self.axes.relim() #scale the y scale
#             self.axes.autoscale_view() #scale the y scale

#     #finally draw the figure on a canvas
#     def figure_drawer(self):
#         if self.fig_agg is not None: self.fig_agg.get_tk_widget().forget()
#         self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas.TKCanvas)
#         self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
#         self.fig_agg.draw_idle()

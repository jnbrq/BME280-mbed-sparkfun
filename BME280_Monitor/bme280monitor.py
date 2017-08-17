#!/usr/bin/env python3

# Author: Canberk Sönmez <canberk.sonmez@metu.edu.tr>

import wx
import wx.lib.newevent
import serial
import serial.threaded
import time
import re

import numpy as np
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure


class PlotCanvas(wx.Panel):
    MAX_VALUES = 500

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.temp_axes = self.figure.add_subplot(111)

        if False:
            self.pressure_axes = self.figure.add_subplot(211)
            self.humidity_axes = self.figure.add_subplot(311)

        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        self.time_values = np.array([])
        self.temp_values = np.array([])
        self.pressure_values = np.array([])
        self.humidity_values = np.array([])
        self.temp_plot, = self.temp_axes.plot(
            self.time_values,
            self.temp_values,
            color="red",
            linewidth=2,
            label="Temperature (celsius)")
        if False:
            self.pressure_plot, = self.pressure_axes.plot(
                self.time_values,
                self.pressure_values,
                color="green",
                linewidth=2,
                label="Pressure (hPa)")
            self.humidity_plot, = self.humidity_axes.plot(
                self.time_values,
                self.humidity_values,
                color="blue",
                linewidth=2,
                label="Humidity")
        self.navBar = NavigationToolbar2Wx(self.canvas)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.navBar, 0, wx.EXPAND)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

    def _trim_values(self):
        sz = self.time_values.size
        if sz >= self.MAX_VALUES:
            self.time_values = self.time_values[(sz - self.MAX_VALUES):]
            self.temp_values = self.temp_values[(sz - self.MAX_VALUES):]
            self.pressure_values = self.pressure_values[(sz - self.MAX_VALUES):]
            self.humidity_values = self.humidity_values[(sz - self.MAX_VALUES):]

    def _refresh_plots(self):
        self.temp_plot.set_xdata(self.time_values)
        self.temp_plot.set_ydata(self.temp_values)
        if False:
            self.pressure_plot.set_xdata(self.time_values)
            self.pressure_plot.set_ydata(self.pressure_values)
            self.humidity_plot.set_xdata(self.time_values)
            self.humidity_plot.set_ydata(self.humidity_values)
        self.temp_axes.relim()
        self.temp_axes.autoscale_view()
        if False:
            self.humidity_axes.relim()
            self.humidity_axes.autoscale_view()
            self.pressure_axes.relim()
            self.pressure_axes.autoscale_view()
        self.canvas.draw()
        self.Refresh()

    def push_values(self, time_values, temp_values, pressure_values, humidity_values):
        self.time_values = np.concatenate((self.time_values, time_values))
        self.temp_values =  np.concatenate((self.temp_values,temp_values))
        self.pressure_values = np.concatenate((self.pressure_values, pressure_values))
        self.humidity_values = np.concatenate((self.humidity_values, humidity_values))
        self._trim_values()
        self._refresh_plots()


DataArrivedEvent, EVT_DATA_ARRIVED = wx.lib.newevent.NewEvent()

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"BME280 Plotter", pos=wx.DefaultPosition,
                          size=wx.Size(680, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel1 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(self.m_panel1, wx.ID_ANY, u"Temperature (celcius):", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        bSizer3.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.m_stTemp = wx.StaticText(self.m_panel1, wx.ID_ANY, u"<temp>", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_stTemp.Wrap(-1)
        bSizer3.Add(self.m_stTemp, 1, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(self.m_panel1, wx.ID_ANY, u"Relative Humidity (%):", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        bSizer3.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.m_stHumidity = wx.StaticText(self.m_panel1, wx.ID_ANY, u"<humidity>", wx.DefaultPosition, wx.DefaultSize,
                                          0)
        self.m_stHumidity.Wrap(-1)
        bSizer3.Add(self.m_stHumidity, 1, wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(self.m_panel1, wx.ID_ANY, u"Pressure (hPa):", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        bSizer3.Add(self.m_staticText5, 0, wx.ALL, 5)

        self.m_stPressure = wx.StaticText(self.m_panel1, wx.ID_ANY, u"<pressure>", wx.DefaultPosition, wx.DefaultSize,
                                          0)
        self.m_stPressure.Wrap(-1)
        bSizer3.Add(self.m_stPressure, 1, wx.ALL, 5)

        bSizer2.Add(bSizer3, 0, wx.EXPAND, 5)

        self.m_plottedData = PlotCanvas(self.m_panel1)
        bSizer2.Add(self.m_plottedData, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel1.SetSizer(bSizer2)
        self.m_panel1.Layout()
        bSizer2.Fit(self.m_panel1)
        bSizer1.Add(self.m_panel1, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        self.Bind(EVT_DATA_ARRIVED, self.OnDataArrived)

    def OnDataArrived(self, event):
        if event.data is None:
            self.Close()
        else:
            self.m_stTemp.SetLabel(str(event.data[1][-1]))
            self.m_stPressure.SetLabel(str(event.data[2][-1]))
            self.m_stHumidity.SetLabel(str(event.data[3][-1]))
            self.m_plottedData.push_values(event.data[0], event.data[1], event.data[2], event.data[3])


programEpoch = time.time()

class ProcessLine(serial.threaded.LineReader):
    TERMINATOR = b"\n"
    ENCODING = 'ascii'
    BUFFER_LIMIT = 5

    def __init__(self, frame):
        super(self.__class__, self).__init__()
        self.frame = frame
        self.n = 0
        self.time_values = []
        self.temp_values = []
        self.humidity_values = []
        self.pressure_values = []

    def connect_made(self, transport):
        pass

    def handle_line(self, line):
        global programEpoch
        print(line)
        try:
            t = time.time() - programEpoch
            temp, pressure, humidity = re.findall(r"\d+(?:\.\d+)?", line)
            self.time_values.append(float(t))
            self.temp_values.append(float(temp))
            self.pressure_values.append(float(pressure))
            self.humidity_values.append(float(humidity))
            self.n = self.n + 1
            if self.n >= self.BUFFER_LIMIT:
                evt = DataArrivedEvent(data=[
                    self.time_values[:],
                    self.temp_values[:],
                    self.pressure_values[:],
                    self.humidity_values[:]])
                wx.PostEvent(self.frame, evt)
                self.n = 0
                self.time_values = []
                self.temp_values = []
                self.humidity_values = []
                self.pressure_values = []
        except Exception as ex:
            print(ex)

    def connection_lost(self, exc):
        print(exc)
        try:
            evt = DataArrivedEvent(data=None)
            wx.PostEvent(self.frame, evt)
        except Exception as e:
            print(e)


def main():
    ser = serial.Serial("/dev/ttyACM0", 9600)
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    with serial.threaded.ReaderThread(ser, lambda: ProcessLine(frame)) as protocol:
        app.MainLoop()


if __name__ == "__main__":
    main()
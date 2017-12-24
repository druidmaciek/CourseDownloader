from threading import Thread
import wx
import time


def test1():
    for i in range(10):
        print (i)
        time.sleep(1)

class TestFrame(wx.Frame):
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, "Test") 
        panel = wx.Panel(self, -1) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        panel.SetSizer(sizer) 

        self.button = wx.Button(panel, 0, "Start")
        sizer.Add(self.button, 0, wx.ALIGN_LEFT) 
        self.button.Bind(wx.EVT_BUTTON, self.OnButton)

        self.text = wx.StaticText(panel, 0, "No test is running")
        sizer.Add(self.text, 0, wx.ALIGN_LEFT) 

        self.timer = wx.Timer(self)

    def OnButton(self, event):
        self.testThread = Thread(target=test1)
        self.testThread.start()
        self.text.SetLabel("Running")
        self.button.Disable()
        self.Bind(wx.EVT_TIMER, self.PollThread)
        self.timer.Start(20, oneShot=True)
        event.Skip()

    def PollThread(self, event):
        if self.testThread.isAlive():
            self.Bind(wx.EVT_TIMER, self.PollThread)
            self.timer.Start(200, oneShot=True)
            self.text.SetLabel(self.text.GetLabel() + ".")
        else:
            self.button.Enable()
            self.text.SetLabel("Test completed")


app = wx.App()
TestFrame().Show()
app.MainLoop()
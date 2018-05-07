"""
GUI for Seagul Reading Project

- SeagulFrame: Start up GUI
"""

import wx
from model import Model

class SeagulFrame(wx.Frame):

  def __init__(self):
    wx.Frame.__init__(self, None, wx.ID_ANY, "Seagul Reading") 
    self.panel = wx.Panel(self)
    self.Bind(wx.EVT_CLOSE, self.on_close)
    self.rest_btn = wx.Button(self.panel, label="Start 5-minute Resting")
    self.read_btn = wx.Button(self.panel, label="Start Reading")
    ### GUI ###
    self.title = wx.StaticText(self.panel, label="Seagul Reading")
    font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.BOLD)
    self.title.SetFont(font)
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.title, 1, wx.ALL | wx.ALIGN_CENTER, 5)
    hbox = wx.BoxSizer(wx.HORIZONTAL) 
    hbox.Add(self.rest_btn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
    hbox.Add(self.read_btn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
    sizer.Add(hbox, 1, wx.ALL | wx.ALIGN_CENTER, 5)
    self.panel.SetSizer(sizer) 
    # listener
    self.rest_btn.Bind(wx.EVT_BUTTON, self.on_start_rest)
    self.read_btn.Bind(wx.EVT_BUTTON, self.on_start_read)

    ### Software Model ###
    self.model = Model()

  def on_start_rest(self, event):
    """
    Start information recording window
    """
    info_window = StartWindow(self.model)
    info_window.Show()
   
  def on_start_read():
    pass

  def on_close(self, event):
    self.Destroy()


class StartWindow(wx.Frame):

  def __init__(self, model):
    wx.Frame.__init__(self, None, wx.ID_ANY, "Please enter your information:") 
    self.model = model
    self.panel = wx.Panel(self)
    self.Bind(wx.EVT_CLOSE, self.on_close)
    # Subject recording
    self.name_txt = wx.TextCtrl(self.panel, -1, style=wx.TE_CENTRE, size=(250, -1))
    self.name_txt.SetValue("Your name (Last, First): ") 
    self.name_txt.Bind(wx.EVT_KEY_DOWN, self.toggle_name)
    self.exp_txt = wx.TextCtrl(self.panel, -1, style=wx.TE_CENTRE, size=(250, -1)) 
    self.exp_txt.SetValue("Your experiment number: ")   
    self.exp_txt.Bind(wx.EVT_KEY_DOWN, self.toggle_exp)
    # boxer
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.name_txt, 1, wx.ALL|wx.ALIGN_CENTER, 5)
    sizer.Add(self.exp_txt, 1, wx.ALL|wx.ALIGN_CENTER, 5)
    self.panel.SetSizer(sizer)
    # button
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    self.submit_btn = wx.Button(self.panel, label="Submit")
    self.cancel_btn = wx.Button(self.panel, label="Cancel")
    hbox.Add(self.submit_btn)
    hbox.Add(self.cancel_btn)
    sizer.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)
    # bind buttons
    self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
    self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

  def toggle_name(self, event):
    if self.name_txt.GetValue() == "Your name (Last, First): ":
      self.name_txt.SetValue("")
    event.Skip()

  def toggle_exp(self, event):
    if self.exp_txt.GetValue() == "Your experiment number: ":
      self.exp_txt.SetValue("")
    event.Skip()

  def on_submit(self, event):
    """
    Record subject info, and start a 5-minute recording session
    """
    self.model.get_info(self.name_txt.GetValue(), self.exp_txt.GetValue())

    
  def on_close(self, event):
    self.Destroy()
 
  def on_cancel(self, event):
    self.on_close(event) 

if __name__ == "__main__":
  app = wx.App(False)
  frame = SeagulFrame()
  frame.Show()

  app.MainLoop()

"""
GUI for Seagul Reading Project

- SeagulFrame: Start up GUI
"""

import winsound
import wx
import time
from model import Model


class SeagullFrame(wx.Frame):

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
        self.model = Model(self, 1)

    def on_start_rest(self, event):
        """
        Start resting recording window
        """
        if self.model.is_rested():
            wx.MessageBox('Resting data already recorded', 'Warning', wx.OK | wx.ICON_INFORMATION)
        else:
            info_window = StartWindow(self.model)
            info_window.Show()
   
    def on_start_read(self, event):
        """
        Start reading
        """
        if not self.model.is_rested():
            wx.MessageBox('Need to record resting data first!', 'Warning', wx.OK | wx.ICON_INFORMATION)
        else:
            read_window = ReadingWindow(self.model, 1)
            read_window.Show()
            # start detection
            self.model.start_reading()

    def get_pinged(self, question):
        dlg = wx.TextEntryDialog(self.panel, question, defaultValue="Answer: ")
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def on_close(self, event):
        self.Destroy()


class ReadingWindow(wx.Frame):

    def __init__(self, model, text_num):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Please enter your information:", size=(650, 300))
        self.model = model
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # text panel
        self._shown_text_idx = 0
        self._shown_text = wx.StaticText(self.panel, label=self.model.get_text(self._shown_text_idx))
        self._shown_text.Wrap(500)
        font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD)
        self._shown_text.SetFont(font)
        # next button
        self._next_button = wx.Button(self.panel, label="Next line")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._shown_text, 10, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self._next_button, 0, wx.RIGHT | wx.ALL, border=10)
        self.panel.SetSizer(sizer)
        # button listener
        self._next_button.Bind(wx.EVT_BUTTON, self.on_next_line)

    def on_next_line(self, event):
        self._shown_text_idx += 1
        try:
            self._shown_text.SetLabel(self.model.get_text(self._shown_text_idx))
            self._shown_text.Wrap(500)
        except ValueError as e:
            print(e)
            wx.MessageBox("This is the last line! You are done", "Warning", wx.OK | wx.ICON_INFORMATION)

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
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.name_txt, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        self.sizer.Add(self.exp_txt, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        self.panel.SetSizer(self.sizer)
        # button
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.submit_btn = wx.Button(self.panel, label="Submit")
        self.cancel_btn = wx.Button(self.panel, label="Cancel")
        hbox.Add(self.submit_btn)
        hbox.Add(self.cancel_btn)
        self.sizer.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        # bind buttons
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        # timer used for count down
        self._start_rest_time = None

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
        # start a recording session
        self.model.start_resting()
        # clear screen
        for child in self.panel.GetChildren():
            child.Destroy()
        # start timer
        wait_txt = wx.StaticText(self.panel, label="Please wait for resting data collection to be done...")
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD)
        wait_txt.SetFont(font)
        # timing for 5 min
        while time.time() - self.model.get_start_rest_time() <= 10:
            pass
        # finish resting
        self.model.finish_resting()
        # then close window, pop up line number
        wx.MessageBox('Resting data finished recording. Total line: %d' % (self.model.get_total_line_count()),
                      'Resting Finished', wx.OK | wx.ICON_INFORMATION)
        self.on_close(event)

    def on_close(self, event):
        self.Destroy()
 
    def on_cancel(self, event):
        self.on_close(event)


def play_beep(frequency=2500, duration=1000):
    winsound.Beep(frequency, duration)


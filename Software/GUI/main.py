import wx
from view import SeagullFrame, play_beep


def main():
    """
    Start the GUI
    """
    app = wx.App(False)
    frame = SeagullFrame()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()

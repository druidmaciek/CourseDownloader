"""
    TO DO:
        - Load urls from txt/csv file
        - Select which vids to download
        - Add reset app data button
"""
from threading import Thread
from validators import url
from course_sites.lynda import Lynda
from course_sites.pluralsight import Pluralsight
from course_sites.skillshare import Skillshare
from data.datahandler import DataReader
import wx, wx.html
import sys

aboutText = """<p>Course Downloader is a application 
for downloading whole video courses from premium and free sites
with one click<br>Supported Sites: </p>
<ul>
<li><a href="https://lynda.com">Lynda.com</a></li>
<li><a href="https://pluralsight.com">Pluralsight.com</a></li>
</ul>
<br>
<p>Version: 1.0.0<br>The program is running version
 %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.</p>"""

class DataDialog(wx.Dialog):
    """Data dialog. Edit login data"""
    def __init__(self):
        self.reader = DataReader()
        self.load_passwords()
        wx.Dialog.__init__(self, None, title='Login Data', size=(300,300))
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)


        row_1Lbl = wx.StaticText(self, label='Lynda:')
        self.row_1_userTxt = wx.TextCtrl(self, value=self.lynda[0])
        self.row_1_pwdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD, value=self.lynda[1])
        self.addWidgets(row_1Lbl, self.row_1_userTxt, self.row_1_pwdTxt)

        row_2Lbl = wx.StaticText(self, label='Pluralsight:')
        self.row_2_userTxt = wx.TextCtrl(self)
        self.row_2_pwdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.addWidgets(row_2Lbl, self.row_2_userTxt, self.row_2_pwdTxt)

        row_3Lbl = wx.StaticText(self, label='Skillshare:')
        self.row_3_userTxt = wx.TextCtrl(self)
        self.row_3_pwdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.addWidgets(row_3Lbl, self.row_3_userTxt, self.row_3_pwdTxt)

        row_4Lbl = wx.StaticText(self, label='Udemy:')
        self.row_4_userTxt = wx.TextCtrl(self)
        self.row_4_pwdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.addWidgets(row_4Lbl, self.row_4_userTxt, self.row_4_pwdTxt)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        okBtn = wx.Button(self, wx.ID_OK)
        btnSizer.Add(okBtn, 0, wx.CENTER | wx.ALL, 5)
        okBtn = wx.Button(self, label='Save')
        okBtn.Bind(wx.EVT_BUTTON, self.onSave)
        btnSizer.Add(okBtn, 0, wx.CENTER | wx.ALL, 5)
        #cancelBtn = wx.Button(self, wx.ID_CANCEL)
        #btnSizer.Add(cancelBtn, 0, wx.CENTER | wx.ALL, 5)
        self.mainSizer.Add(btnSizer, 0, wx.CENTER)

        self.SetSizer(self.mainSizer)

    def addWidgets(self, lbl, txt1, txt2):
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(lbl, 0, wx.ALL, 5)
        sizer2.Add(txt1, 1, wx.EXPAND | wx.ALL, 5)
        sizer2.Add(txt2, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(sizer1, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.mainSizer.Add(sizer2, 0, wx.EXPAND)

    def load_passwords(self):
        self.lynda = self.reader.load_login('lynda')

    def onSave(self, event):
        self.reader.save_login('lynda', self.row_1_userTxt.GetValue(), self.row_1_pwdTxt.GetValue())
        self.reader.save_login('pluralsight', self.row_2_userTxt.GetValue(), self.row_2_pwdTxt.GetValue())
        self.reader.save_login('skillshare', self.row_3_userTxt.GetValue(), self.row_3_pwdTxt.GetValue())


        dlg = wx.MessageDialog(self, "All fields   saved",
                               "", wx.OK | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()



class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600, 400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About Course Downloader",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER |
                                 wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


class Frame(wx.Frame):

    def __init__(self, title):
        self.reader = DataReader()
        self.save_dir = self.reader.load_last_dir()
        self.username = None
        self.pwd = None
        self.course_site = None

        wx.Frame.__init__(self, None, title=title, pos=(150, 150), size=(350, 235))
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnQuit, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        # Top Row: Login | Set Directory |  Quit Buttons
        top_box = wx.BoxSizer(wx.HORIZONTAL)

        b_data = wx.Button(panel, label="App Data")
        b_data.Bind(wx.EVT_BUTTON, self.onData)
        top_box.Add(b_data, 1, wx.ALL, 5)
        """b_login = wx.Button(panel, label="Login")
        b_login.Bind(wx.EVT_BUTTON, self.OnLogin)
        top_box.Add(b_login, 1, wx.ALL, 5)"""


        b_set_dir= wx.Button(panel, label="Set Directory")
        b_set_dir.Bind(wx.EVT_BUTTON, self.OnDir)
        top_box.Add(b_set_dir, 1, wx.ALL, 5)
        b_load = wx.Button(panel, label="Load file")
        b_load.Bind(wx.EVT_BUTTON, self.OnQuit)     # !!! Create OnLoad fuction
        top_box.Add(b_load, 1, wx.ALL, 5)
        box.Add(top_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        # Middle Rows: Dir Info | URL Input Box + Label | Text Info Log | Progress Bar
        self.dir_text = wx.StaticText(panel, 0, "Download Directory: {0}".format(self.save_dir))
        box.Add(self.dir_text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        box.AddSpacer(5)
        sbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(panel, -1, "URL:")
        sbox1.Add(label, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        # URL input box
        self.t1 = wx.TextCtrl(panel, size=(300, -1))
        sbox1.Add(self.t1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        box.Add(sbox1)
        sbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.StaticText(panel, 0, "No process is running")
        sbox3.Add(self.text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        box.Add(sbox3, 1, wx.ALIGN_LEFT)
        box.AddSpacer(8)
        # Progress bar
        self.gauge = wx.Gauge(panel, range=20, size=(300, 2), style=wx.GA_HORIZONTAL)
        box.Add(self.gauge, proportion=1, flag=wx.ALIGN_CENTER)
        box.AddSpacer(8)

        # Bottom Row: Start | Quit Buttons
        bottom_box = wx.BoxSizer(wx.HORIZONTAL)
        self.b_start = wx.Button(panel, label="Start")
        self.Bind(wx.EVT_BUTTON, self.OnStart, self.b_start)
        bottom_box.Add(self.b_start, 1, wx.ALL, 5)
        self.b_close = wx.Button(panel, label="Quit")
        self.Bind(wx.EVT_BUTTON, self.OnQuit, self.b_close)
        bottom_box.Add(self.b_close, 1, wx.ALL, 5)
        box.Add(bottom_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(box)
        panel.Layout()

    def onData(self, event):
        """
        Show login credentials window
        """
        dlg = DataDialog()
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnQuit(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def OnDir(self, event):
        dialog = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.save_dir = dialog.GetPath()
            self.reader.save_last_dir(self.save_dir)
            self.dir_text.SetLabel("Download Directory: {0}".format(self.save_dir))
        dialog.Destroy()

    def OnStart(self, event):
        """
        -check if the save_dir is set
        -check if the url is present & valid
        -identify site and check if the credentials are passed or saved in data
        -run the check_site on seperate thread
        -show appropriate messages
        """

        if self.save_dir is None:
            dlg = wx.MessageDialog(self,
                                   "",
                                   "Download location is not set", wx.OK | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        text_url = self.t1.GetValue()
        # Validate url
        if url(text_url):
            dlg = wx.MessageDialog(self,
                                   "Do you really want to download the course from {}?".format(text_url),
                                   "Confirm Download?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:

                if '.lynda' in text_url:
                    usr, pwd = self.reader.load_login('lynda')
                    logged = self.notLoggedMessage(usr, pwd, 'Lynda')
                    if logged:
                        self.username, self.pwd = usr, pwd
                    else:
                        return
                elif '.pluralsight' in text_url:
                    usr, pwd = self.reader.load_login('pluralsight')
                    if self.notLoggedMessage(usr, pwd, 'Pluralsight'):
                        self.username, self.pwd = usr, pwd
                elif '.skillshare' in text_url:
                    usr, pwd = self.reader.load_login('skillshare')
                    if self.notLoggedMessage(usr, pwd, 'Skillshare'):
                        self.username, self.pwd = usr, pwd


                # Run the check_site function on separate thread
                self.testThread = Thread(target=self.check_site)
                self.testThread.start()
                self.text.SetLabel("Running")
                self.b_start.Disable()
                self.t1.Disable()
                self.Bind(wx.EVT_TIMER, self.PollThread)

            else:
                self.t1.SetValue('')
        else:
            self.t1.SetValue('')
            dlg = wx.MessageDialog(self,
                                   "This is not a correctly formatted URL.",
                                   "Enter an url.", wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
        event.Skip()

    def notLoggedMessage(self, usr, pwd, site):
        if not usr or not pwd:
            dlg = wx.MessageDialog(self, "Please login into your {} account.".format(site),
                                   "User not logged in", wx.OK | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def PollThread(self, event):
        if self.testThread.isAlive():
            self.Bind(wx.EVT_TIMER, self.PollThread)
            self.text.SetLabel(self.text.GetLabel() + ".")
        else:
            self.b_start.Enable()
            self.t1.Enable()
            self.text.SetLabel("Completed")

    def check_site(self):
        """
        - Identify site and initialize course_site value with a Class of website
        - Enable Disabled areas
        - Update Log Label
        :return:
        """
        url_val = self.t1.GetValue()
        self.t1.SetValue('')
        self.gauge.Pulse()
        if '.lynda.' in url_val:
            self.course_site = Lynda(url_val, self.username, self.pwd, self.gauge, self.text, self.save_dir)
        elif '.pluralsight.' in url_val:
            self.course_site = Pluralsight(url_val, self.username, self.pwd, self.gauge, self.text, self.save_dir)
        elif '.skillshare.' in url_val:
            self.course_site = Skillshare(url_val, self.username, self.pwd, self.gauge, self.text, self.save_dir)
        dlg = wx.MessageDialog(self, "All Files Downloaded.", "", wx.OK | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        # dlg.Destroy()
        self.course_site = object
        self.gauge.SetValue(0)
        self.b_start.Enable()
        self.t1.Enable()
        self.text.SetLabel("Completed")


app = wx.App(redirect=True)
top = Frame("Course Downloader")
top.Show()
app.MainLoop()

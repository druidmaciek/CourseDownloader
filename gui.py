"""
     __author__ = "Druidmaciek"
    __version__ = "1.0.1"
    __maintainer__ = "Druidmaciek"
    TODO:
    - Add Groove3, Udemy, Youtube
"""
import urllib
import wx
import wx.html
import sys
from validators import url
from data.datahandler import DataReader
from data.scrapers import *
from threading import Thread
import wx.lib.mixins.listctrl as listmix


aboutText = """<p>Course Downloader is a application 
for downloading whole video courses from premium(if you have an account) and free sites
with one click<br>Supported Sites: </p>
<ul>
<li><a href="https://lynda.com">Lynda.com</a></li>
<li><a href="https://pluralsight.com">Pluralsight.com</a></li>
<li><a href="https://skillshare.com">Skillshare.com</a>(Not Tested)</li>
</ul>
<br>
<p>Version: 1.0.1<br>The program is running version
 %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.</p>"""


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


class MainFrame(wx.Frame):

    def __init__(self):
        self.count = 0
        self.course_site = None
        self.vid_data = None
        self.username = ''
        self.pwd = ''
        self.reader = DataReader()
        self.save_dir = self.reader.load_last_dir()
        wx.Frame.__init__(self, None, title="Course Downloader", pos=(150, 150), size=(350, 450))
        self.Bind(wx.EVT_CLOSE, self.onQuit)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.onQuit, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        self.statusbar = self.CreateStatusBar()

        self.panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        # Top Row
        top_box = wx.BoxSizer(wx.HORIZONTAL)
        b_login = wx.Button(self.panel, label="Edit accounts")
        self.Bind(wx.EVT_BUTTON, self.onLogin, b_login)
        top_box.Add(b_login, 1, wx.ALL, 5)
        b_set_dir = wx.Button(self.panel, label="Set Directory")
        b_set_dir.Bind(wx.EVT_BUTTON, self.OnDir)
        top_box.Add(b_set_dir, 1, wx.ALL, 5)
        box.Add(top_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        # Middle Rows: Dir Info | URL Input Box + Label | Text Info Log | Progress Bar
        self.dir_text = wx.StaticText(self.panel, 0, "Download Directory: {0}".format(self.save_dir))
        box.Add(self.dir_text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        box.AddSpacer(5)
        sbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self.panel, -1, "URL:")
        sbox1.Add(label, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        # URL input box
        self.t1 = wx.TextCtrl(self.panel, size=(300, -1))
        sbox1.Add(self.t1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        box.Add(sbox1)
        sbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.StaticText(self.panel, 0, "No process is running")
        sbox3.Add(self.text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        box.Add(sbox3, 1, wx.ALIGN_LEFT)
        # Progress bar
        self.gauge = wx.Gauge(self.panel, range=20, size=(300, 1), style=wx.GA_HORIZONTAL)
        box.Add(self.gauge, proportion=1, flag=wx.ALIGN_CENTER)

        # Bottom Row: Start | Download | Quit Buttons
        bottom_box = wx.BoxSizer(wx.HORIZONTAL)
        self.b_start = wx.Button(self.panel, label="Start")
        self.Bind(wx.EVT_BUTTON, self.onStart, self.b_start)
        bottom_box.Add(self.b_start, 1, wx.ALL, 5)
        self.b_down = wx.Button(self.panel, label="Download")
        self.b_down.Disable()
        self.Bind(wx.EVT_BUTTON, self.onDownload, self.b_down)
        bottom_box.Add(self.b_down, 1, wx.ALL, 5)
        self.b_close= wx.Button(self.panel, label="Quit")
        self.Bind(wx.EVT_BUTTON, self.onQuit, self.b_close)
        bottom_box.Add(self.b_close, 1, wx.ALL, 5)
        box.Add(bottom_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        list_box = wx.BoxSizer(wx.HORIZONTAL)
        self.b_sall = wx.Button(self.panel, label="Select All")
        self.Bind(wx.EVT_BUTTON, self.onSall, self.b_sall)
        list_box.Add(self.b_sall, 1, wx.ALL, 5)
        self.b_uall = wx.Button(self.panel, label="Unselect All")
        self.Bind(wx.EVT_BUTTON, self.onUall, self.b_uall)
        list_box.Add(self.b_uall, 1, wx.ALL, 5)
        box.Add(list_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        select_box = wx.BoxSizer(wx.HORIZONTAL)
        self.list = TestListCtrl(self.panel, style=wx.LC_REPORT)
        self.list.InsertColumn(0, "Name")
        self.list.InsertColumn(1, "Chapter")
        self.list.InsertColumn(2, "Source")
        self.list.InsertColumn(3, "Path")
        self.list.Arrange()
        select_box.Add(self.list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)#Add(self.list, 1, wx.ALL, 5)

        box.Add(select_box, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel.SetSizerAndFit(box)
        #self.panel.SetSizer(box)
        self.panel.Layout()

    def onSall(self, event):
        for i in range(self.list.GetItemCount()):
            self.list.CheckItem(i)

    def onUall(self, event):
        for i in range(self.list.GetItemCount()):
            self.list.CheckItem(i, False)


    def onDownload(self, event):
        self.gauge.Pulse()
        self.testThread = Thread(target=self.download)
        self.testThread.start()
        self.b_down.Disable()
        self.Bind(wx.EVT_TIMER, self.PollThread)
        event.Skip()



    def download(self):
        self.b_start.Disable()
        num = 0
        count = self.list.GetItemCount()
        data = self.list.getChecker()
        for row in range(count):
            if data[row]:
                num += 1
        self.text.SetLabel("Downloading: 0/{}".format(num))


        prog = 0
        for row in range(count):
            if data[row]:
                path = self.list.GetItem(row, 3).GetText()
                source = self.list.GetItem(row, 2).GetText()
                self.count += 1
                sleep(1)
                urllib.request.urlretrieve(source, path)
                prog += 1
                self.text.SetLabel("Downloading: {}/{}".format(prog, num))

        self.list.DeleteAllItems()
        self.b_down.Disable()
        self.text.SetLabel('Done...')
        self.b_down.Disable()
        self.b_start.Enable()
        dlg = wx.MessageDialog(self,
                               "All selected videos downloaded...",
                               "Downloading complete", wx.OK | wx.ICON_QUESTION)
        dlg.ShowModal()
        dlg.Destroy()
        self.gauge.SetValue(0)

    def onStart(self, event):
        """
                -check if the save_dir is set
                -check if the url is present & valid
                -identify site and check if the credentials are passed or saved in data
                -run the check_site on seperate thread
                -show appropriate messages
        """
        self.b_down.Disable()
        self.list.DeleteAllItems()
        if not self.save_dir:
            dlg = wx.MessageDialog(self,
                                   "",
                                   "Download location is not set", wx.OK | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        text_url = self.t1.GetValue()
        # Validate url
        if not url(text_url):
            self.t1.SetValue('')
            dlg = wx.MessageDialog(self,
                                   "This is not a correctly formatted URL.",
                                   "Enter an url.", wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if url(text_url):
            dlg = wx.MessageDialog(self,
                                   "Do you really want to download the course from {}?".format(text_url),
                                   "Confirm Download?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:

                site = text_url[text_url.find('.') + 1:]
                site = site[:site.find('.') + 1]
                sites = {'lynda.': 'Lynda', 'pluralsight.': 'Pluralsight',
                         'skillshare.': 'Skillshare', 'udemy.': 'Udemy'}
                sleep(1)
                username, pwd = self.reader.load_login(sites[site])
                if self.notLoggedMessage(username, pwd, sites[site]):
                    self.username, self.pwd = username, pwd
                else:
                    return


                self.course_site = sites[site]

                self.testThread = Thread(target=self.run_scraper, args=[text_url])
                self.testThread.start()
                self.text.SetLabel("Running")
                self.b_start.Disable()
                self.t1.Disable()
                self.Bind(wx.EVT_TIMER, self.PollThread)
            else:
                self.t1.SetValue('')

        event.Skip()

    def run_scraper(self, text_url):
        url_val = self.t1.GetValue()
        self.t1.SetValue('')
        self.gauge.Pulse()
        if self.course_site == 'Lynda':
            scraper = Lynda(text_url, self.username, self.pwd, self.text, self.save_dir)
        elif self.course_site == 'Pluralsight':
            scraper = Pluralsight(text_url, self.username, self.pwd, self.text, self.save_dir)
        elif self.course_site == 'Skillshare':
            scraper = Skillshare(text_url, self.username, self.pwd, self.text, self.save_dir)
        self.vid_data = scraper.vid_data
        self.b_down.Enable()
        for i in enumerate(self.vid_data, 1):
            self.list.Append([i[1]['name'], i[1]['chapter'], i[1]['source'], i[1]['path']])

        for i in range(0, self.list.GetItemCount()):
            self.list.CheckItem(i)
        dlg = wx.MessageDialog(self,
                               "All video sources gathered...",
                               "Press Download to continue", wx.OK | wx.ICON_QUESTION)
        dlg.ShowModal()
        dlg.Destroy()
        self.course_site = None
        self.b_start.Enable()
        self.t1.Enable()

    def PollThread(self, event):
        if self.testThread.isAlive():
            self.Bind(wx.EVT_TIMER, self.PollThread)
            self.text.SetLabel(self.text.GetLabel() + ".")
        else:
            self.b_start.Enable()
            self.t1.Enable()
            self.text.SetLabel("Completed")

    def onLogin(self, event):
        dlg = LoginDialog()
        dlg.ShowModal()
        dlg.Destroy()


    def onAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()


    def notLoggedMessage(self, usr, pwd, site):
        if not usr or not pwd:
            dlg = wx.MessageDialog(self, "Please login into your {} account.".format(site),
                                   "User not logged in", wx.OK | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def onQuit(self, event):
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


class LoginDialog(wx.Dialog):
    """Edit login data"""

    def __init__(self):
        self.reader = DataReader()
        wx.Dialog.__init__(self, None, title='Login Data', size=(240, 125))
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Top row with combobox and resest button
        sites = ['Select...', 'Lynda', 'Pluralsight', 'Skillshare']
        top_box = wx.BoxSizer(wx.HORIZONTAL)
        self.combo = wx.ComboBox(self, -1, choices=sites, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        top_box.Add(self.combo, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        b_reset = wx.Button(self, label='Clear Data')
        b_reset.Bind(wx.EVT_BUTTON, self.onClear)
        top_box.Add(b_reset, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        mainSizer.Add(top_box, 0, wx.ALIGN_CENTER)

        # Middle row with inputs
        mid_box = wx.BoxSizer(wx.HORIZONTAL)
        self.userTxt = wx.TextCtrl(self)
        mid_box.Add(self.userTxt, 1, wx.ALL | wx.ALIGN_CENTER)
        mid_box.AddSpacer(15)
        self.pwdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        mid_box.Add(self.pwdTxt, 1, wx.ALL | wx.ALIGN_CENTER)
        mainSizer.Add(mid_box, 0, wx.ALIGN_CENTER)

        # Bottom row with save, close buttons
        bottom_box = wx.BoxSizer(wx.HORIZONTAL)
        b_save = wx.Button(self, label="Save")
        b_save.Bind(wx.EVT_BUTTON, self.onSave)
        bottom_box.Add(b_save, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        okBtn = wx.Button(self, wx.ID_CANCEL, label="Close")
        bottom_box.Add(okBtn, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        mainSizer.Add(bottom_box, 0, wx.ALIGN_CENTER)
        self.SetSizer(mainSizer)

    def OnSelect(self, event):
        site = self.combo.GetValue()
        if site == 'Select...':
            self.userTxt.SetValue('')
            self.pwdTxt.SetValue('')
        else:
            creds = self.reader.load_login(site)
            self.userTxt.SetValue(creds[0])
            self.pwdTxt.SetValue(creds[1])

    def onSave(self, event):
        site = self.combo.GetValue()
        if site == 'Select...':
            return
        self.reader.save_login(self.combo.GetValue(), self.userTxt.GetValue(), self.pwdTxt.GetValue())
        dlg = wx.MessageDialog(self, "{} username and password saved".format(site),
                               "", wx.OK | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()

    def onClear(self, event):
        self.reader.reset_data()
        self.userTxt.SetValue('')
        self.pwdTxt.SetValue('')
        dlg = wx.MessageDialog(self, "All data erased...",
                               "", wx.OK | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()

    def onClose(self, event):
        self.Destroy()


class TestListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(1)
        self.checker = {}

    def OnCheckItem(self, index, flag):
        self.checker[index] = flag

    def getChecker(self):
        return self.checker
app = wx.App(redirect=True)
frame = MainFrame()
frame.Show()
app.MainLoop()

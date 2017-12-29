"""
    TO-DO:
        - Download Exercise Files
        - select which vids to download
        - Path URL support
"""
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import os
import urllib.request


class Lynda(object):

    def __init__(self, course_url, user, pwd, gauge, label, dir):
        """
        :param course_url: URL of a course from Lynda.com | Example: https://www.lynda.com/Leadership-Management-tutorials/Managing-Technical-Professionals/628686-2.html
        :param user: username or email associated with Lynda.com Account
        :param pwd: password associated with Lynda.com Account
        :param gauge: wxPython Gauge object
        :param label: wxPython Label object
        :param dir: path for downloading files
        """
        self.dir = dir
        self.course_url = course_url
        self.user = user
        self.pwd = pwd
        self.gauge = gauge
        self.label = label

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome('{}/data/chromedriver'.format(os.getcwd()), chrome_options=options)
        self.driver.set_window_size(2000, 2000)
        self.driver.get(self.course_url)
        self.label.SetLabel("Logging in...")
        self.login()
        self.course_title = self.get_title()
        if self.course_title is not None:
            self.label.SetLabel("Course: {}".format(self.course_title))
            try:
                os.makedirs("{}/{}".format(self.dir, self.course_title))
            except FileExistsError:
                pass

            self.vid_data = self.get_vid_data()
            self.label.SetLabel("Downloading...")
            self.download_vids()

    def login(self):
        """
        Login into Lynda.com

        """
        self.driver.find_element_by_xpath('//*[@id="submenu-login"]/li[1]/a').click()
        sleep(2)
        self.driver.find_element_by_id("email-address").send_keys(self.user)
        self.driver.find_element_by_id("username-submit").click()
        sleep(3)
        self.driver.find_element_by_id("password-input").send_keys(self.pwd)
        self.driver.find_element_by_id("password-submit").click()
        sleep(2)

    def get_title(self):
        """
        set self.soup with BeautifulSoup obj
        :return: string with course title
        """
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            title = self.soup.find('h1', {'class': 'default-title', 'itemprop': 'name'}).text.strip().replace('/', '|')
        except AttributeError:
            self.label.SetLabel("It's not a course url...")
            title = None
        return title

    def get_vid_data(self):
        """
        Iterate over all videos gathering urls and titles of videos and chapters, creating folders
        :return: List of dictionarys where dict['source'] is url to video and dict['path']
        string with path to save file to
        """
        chapters = self.soup.find('ul', {'class': 'course-toc toc-container autoscroll'})\
            .findAll('li',{'role': 'presentation'})

        videos_data = []
        for chapter in chapters:
            try:
                chapter_title = chapter.find('div', {'class': 'row chapter-row'})\
                    .find('h4').text.strip().replace('/', '|')
            except AttributeError:
                continue
            self.label.SetLabel(chapter_title)
            try:
                os.makedirs("{}/{}/{}".format(self.dir, self.course_title, chapter_title))
            except FileExistsError:
                pass
            vids = chapter.findAll('a', {'class': 'item-name video-name ga'})
            vids = [x['href'] for x in vids]

            for vid in enumerate(vids, 1):
                self.driver.get(vid[1])
                sleep(1)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                vid_title = soup.find('h1', {'itemprop': 'name'})['data-video'].strip().replace('/', '|')
                self.label.SetLabel(vid_title)
                video = soup.find('video', {'class': 'player'})['data-src']
                videos_data.append(
                    {"path": "{}/{}/{}/{}. {}.mp4".format(self.dir, self.course_title, chapter_title, vid[0], vid_title),
                     "source": video})
        # Close chromedriver
        self.driver.quit()

        return videos_data

    @staticmethod
    def download_vid(data):
        urllib.request.urlretrieve(data['source'], data['path'])
        

    def download_vids(self):
        pool = Pool(cpu_count() * 4)
        results = pool.map(self.download_vid, self.vid_data)

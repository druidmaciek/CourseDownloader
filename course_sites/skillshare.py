"""
    To-Do
        - TEST IT
"""
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import os
import urllib.request


class Skillshare(object):

    def __init__(self, course_url, user, pwd, gauge, label, loc):
        """
                :param course_url: URL of a course from Skillshare.com | Example:
                :param user: username or email associated with Skillshare.com Account
                :param pwd: password associated with Skillshare.com Account
                :param gauge: wxPython Gauge object
                :param label: wxPython Label object
                :param loc: path for downloading files
                """
        self.loc = loc
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
        #self.label.SetLabel("Logging in...")
        self.login()
        self.course_title = self.get_title()
        if self.course_title is not None:
            #self.label.SetLabel("Course: {}".format(self.course_title))
            try:
                os.makedirs("{}/{}".format(self.dir, self.course_title))
            except FileExistsError:
                pass

            self.vid_data = self.get_vid_data()
            #self.label.SetLabel("Downloading...")
            self.download_vids()

    def login(self):
        """
        Login into Skillshare.com
        """
        self.driver.find_element_by_xpath('//*[@id="site-content"]/div[3]/div[3]/div[1]/a').click()
        sleep(2)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/fieldset[1]/div/input').send_keys(self.user)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/fieldset[2]/div/input').send_keys(self.pwd)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/input[2]').click()
        sleep(2)

    def get_title(self):
        """
        set self.soup with BeautifulSoup obj
        :return: string with course title
        """
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            title = self.soup.find('div', {'class': 'class-details-header-title'}).text.strip().replace('/', '|')
        except AttributeError:
            #self.label.SetLabel("It's not a course url...")
            title = None
        return title

    def get_vid_data(self):
        """
        Iterate over all videos gathering urls and titles of videos and chapters, creating folders
        :return: List of dictionarys where dict['source'] is url to video and dict['path']
        string with path to save file to
        """
        vids = self.driver.find_elements_by_xpath('//*[@id="video-region"]/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul/li')
        videos_data = []
        for vid in enumerate(vids, 1):
            vid[1].click()
            html = BeautifulSoup(self.driver.page_source, 'html.parser')
            vid_title = vid[0] + '.' + html.find('p', {'class': 'session-item-title'}).text.strip()
            video = html.find('video')['src']
            videos_data.append(
                {"path": "{}/{}/{}.mp4".format(self.dir, self.course_title, vid_title),
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
"""
    To-Do
"""
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from selenium import webdriver
import os
from time import sleep
from bs4 import BeautifulSoup
import urllib.request


class Pluralsight(object):

    def __init__(self, course_url, user, pwd, gauge, label, loc):
        """
        :param course_url: URL of a course from Pluralsight.com | Example: https://app.pluralsight.com/library/courses/understanding-machine-learning/table-of-contents
        :param user: username or email associated with Pluralsight.com Account
        :param pwd: password associated with Pluralsight.com Account
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
        self.label.SetLabel("Logging in...")
        self.login()
        sleep(4)
        self.course_title = self.get_title()
        if self.course_title is not None:
            self.label.SetLabel("Course: {}".format(self.course_title))
            try:
                os.makedirs("{}/{}".format(self.loc, self.course_title))
            except FileExistsError:
                pass

        self.vid_data = self.get_vid_data()
        self.label.SetLabel("Downloading...")
        self.download_vids()

    def login(self):
        """
        Login into pluralsight.com
        """
        self.driver.find_element_by_xpath('/html/body/div[1]/div/noindex[1]/div/header/div[2]/a').click()
        sleep(2)
        self.driver.find_element_by_id("Username").send_keys(self.user)
        self.driver.find_element_by_id("Password").send_keys(self.pwd)
        self.driver.find_element_by_id("login").click()
        sleep(2)

    def get_title(self):
        """
                set self.soup with BeautifulSoup obj
                :return: string with course title
                """
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            title = self.soup.find('h1', {'class': 'course-hero__title'}).text.strip().replace('/', '|')
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
        chapters = self.soup.find('div', {'class': 'l-course-page__content'}) \
            .find('ul', {'class': 'accordian'}).findAll('li', {'class': 'accordian__section'})

        videos_data = []
        for chapter in enumerate(chapters, 1):
            chapter_title = chapter[0]+". "+chapter[1].find('h3').text.strip().replace('/', '|')
            print(chapter_title)

            self.label.SetLabel(chapter_title)
            try:
                os.makedirs("{}/{}/{}".format(self.loc, self.course_title, chapter_title))
            except FileExistsError:
                pass
            vids = chapter.find('ul', {'class': 'table-of-contents__clip-list'}).findAll('li')

            vids = [("https://app.pluralsight.com" + x.find('a')['href'], x.find('a').text.strip()) for x in vids]

            for vid in enumerate(vids, 1):
                self.driver.get(vid[1][0])
                sleep(2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                vid_title = vid[1][1].replace('/', '|')
                self.label.SetLabel(vid_title)
                try:
                    video = soup.find('video')['src']
                except KeyError:
                    self.driver.quit()
                videos_data.append(
                    {"path": "{}/{}/{}/{}. {}.mp4".format(self.loc, self.course_title, chapter_title, vid[0], vid_title),
                     "source": video})

        # Close chromedriver
        self.driver.quit()
        return videos_data

    @staticmethod
    def download_vid(data):
        urllib.request.urlretrieve(data['source'], data['path'])

    def download_vids(self):
        pool = Pool(cpu_count() * 2)
        results = pool.map(self.download_vid, self.vid_data)

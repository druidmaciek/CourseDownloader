"""
                                                                                                                                                                            __author__ = "Druidmaciek"
                                                                                                                                                                            __version__ = "1.0.1"
                                                                                                                                                                            __maintainer__ = "Druidmaciek"

    TODO:
     - Test Skillshare
     - Finish Udemy & Groove3
     - Add more classes
"""
from selenium import webdriver
import os
from time import sleep
from bs4 import BeautifulSoup


class Scraper(object):

    def __init__(self, url, user, pwd, label, save_dir):
        self.course_url = url.strip()
        self.user = user
        self.pwd = pwd
        self.label = label
        self.save_dir = save_dir
        self.error_message = "It's not a course url or login/password is wrong..."
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome()#webdriver.Chrome('{}/data/chromedriver'.format(os.getcwd()), chrome_options=options)
        self.driver.set_window_size(2000, 2000)
        self.driver.get(self.course_url)
        self.label.SetLabel("Logging in...")
        self.login()
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.get_title()
        self.vid_data = []

        if self.course_title is not None:
            self.label.SetLabel("Course: {}".format(self.course_title))
            self.create_folder(self.save_dir, self.course_title)
            self.get_vid_data()
            self.driver.quit()



    def create_folder(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

    def getVidData(self):
        return self.vid_data


class Lynda(Scraper):


    def login(self):
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
        :return: string with course title
        """
        try:
            self.course_title = self.soup.find('h1', {'class': 'default-title', 'itemprop': 'name'}).text.strip().replace('/', '|')
        except AttributeError:
            self.label.SetLabel(self.error_message)
            self.course_title = None


    def get_vid_data(self):
        """
        Iterate over all videos gathering urls and titles of videos and chapters, creating folders
        :return: List of dictionarys where dict['source'] is url to video and dict['path']
        string with path to save file to
        """
        chapters = self.soup.find('ul', {'class': 'course-toc toc-container autoscroll'}) \
            .findAll('li', {'role': 'presentation'})

        vid_index = 1
        for chapter in chapters:
            try:
                chapter_title = chapter.find('div', {'class': 'row chapter-row'}) \
                    .find('h4').text.strip().replace('/', '|')
            except AttributeError:
                continue
            self.label.SetLabel(chapter_title)
            self.create_folder("{}/{}/{}".format(self.save_dir, self.course_title, chapter_title))
            """try:
                os.makedirs("{}/{}/{}".format(self.save_dir, self.course_title, chapter_title))
            except FileExistsError:
                pass"""
            vids = chapter.findAll('a', {'class': 'item-name video-name ga'})
            vids = [x['href'] for x in vids]

            for vid in vids:
                self.driver.get(vid)
                sleep(1)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                vid_title = soup.find('h1', {'itemprop': 'name'})['data-video'].strip().replace('/', '|')
                self.label.SetLabel(vid_title)
                video = soup.find('video', {'class': 'player'})['data-src']

                self.vid_data.append({"path": "{}/{}/{}/{}. {}.mp4".format(self.save_dir, self.course_title,
                                                                           chapter_title, vid_index, vid_title),
                                      'course': self.course_title, 'chapter': chapter_title, 'source': video,
                                      'name': "{}. {}.mp4".format(vid_index, vid_title)})
                vid_index += 1


class Pluralsight(Scraper):

    def login(self):
        self.driver.find_element_by_xpath('/html/body/div[1]/div/noindex[1]/div/header/div[2]/a').click()
        sleep(2)
        self.driver.find_element_by_id("Username").send_keys(self.user)
        self.driver.find_element_by_id("Password").send_keys(self.pwd)
        self.driver.find_element_by_id("login").click()
        sleep(2)

    def get_title(self):
        """
        :return: string with course title
        """
        try:
            self.course_title = self.soup.find('h1', {'class': 'course-hero__title'}).text.strip().replace('/', '|')
        except AttributeError:
            self.label.SetLabel(self.error_message)
            self.course_title = None


    def get_vid_data(self):
        """
        Iterate over all videos gathering urls and titles of videos and chapters, creating folders
        :return: List of dictionarys where dict['source'] is url to video and dict['path']
        string with path to save file to
        """
        chapters = self.soup.find('div', {'class': 'l-course-page__content'}) \
            .find('ul', {'class': 'accordian'}).findAll('li', {'class': 'accordian__section'})

        vid_index = 1
        for chapter in enumerate(chapters, 1):
            chapter_title = chapter[0] + ". " + chapter[1].find('h3').text.strip().replace('/', '|')

            self.label.SetLabel(chapter_title)
            self.create_folder("{}/{}/{}".format(self.save_dir, self.course_title, chapter_title))
            """try:
                os.makedirs("{}/{}/{}".format(self.save_dir, self.course_title, chapter_title))
            except FileExistsError:
                pass"""
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

                self.vid_data.append({"path": "{}/{}/{}/{}. {}.mp4".format(self.save_dir, self.course_title,
                                        chapter_title, vid_index, vid_title),
                                      'course': self.course_title, 'chapter': chapter_title, 'source': video,
                                      'name': "{}. {}.mp4".format(vid_index, vid_title)})
                vid_index += 1


class Skillshare(Scraper):

    def login(self):
        self.driver.find_element_by_xpath('//*[@id="site-content"]/div[3]/div[3]/div[1]/a').click()
        sleep(2)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/fieldset[1]/div/input').send_keys(self.user)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/fieldset[2]/div/input').send_keys(self.pwd)
        self.driver.find_element_by_xpath('//*[@id="abstract-popup-view"]/div/div[2]/div[2]/div[1]/form/input[2]').click()
        sleep(2)

    def get_title(self):
        """
        :return: string with course title
        """
        try:
            self.course_title = self.soup.find('div', {'class': 'class-details-header-title'}).text.strip().replace('/', '|')
        except AttributeError:
            self.label.SetLabel(self.error_message)
            self.course_title = None


    def get_vid_data(self):
        """
        Iterate over all videos gathering urls and titles of videos and chapters, creating folders
        :return: List of dictionarys where dict['source'] is url to video and dict['path']
        string with path to save file to
        """
        vids = self.driver.find_elements_by_xpath('//*[@id="video-region"]/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul/li')

        for vid in enumerate(vids, 1):
            vid[1].click()
            html = BeautifulSoup(self.driver.page_source, 'html.parser')
            vid_title = vid[0] + '.' + html.find('p', {'class': 'session-item-title'}).text.strip()
            video = html.find('video')['src']
            self.vid_data.append(
                {"course": self.course_title, 'chapter': None, "path": "{}/{}/{}.mp4".format(self.dir, self.course_title, vid_title),
                 "source": video})

class Groove(Scraper):

    def login(self):
        self.driver.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[1]/li[6]/a').click()
        sleep(2)
        self.driver.find_element_by_id('inputUsername').send_keys(self.user)
        self.driver.find_element_by_id('inputPassword').send_keys(self.pwd)
        self.driver.find_element_by_xpath('//*[@id="main"]/div/div/form/input').click()
        sleep(2)

    def get_title(self):
        """
        :return: string with course title
        """
        try:
            self.course_title = self.soup.find('h1', {'itemprop': 'name'}).text.strip().replace('/', '|')
        except AttributeError:
            self.label.SetLabel(self.error_message)
            self.course_title = None

    def getVidData(self):
        pass




class Udemy(Scraper):
    pass

class Bob(object):
    def __init__(self):
        self.b = 'b'
    def SetLabel(self, e):
        w = e
test = Groove('https://www.groove3.com/tutorials/Creating-Epic-Cinematic-Compositions', 'Noelsis', 'groove453973', Bob(), None)
"""
    TO-DO:
        - Finish projcet
"""
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import os
import urllib.request


class Udemy(object):

    def __init__(self, course_url, user, pwd, gauge, label, loc):
        """
        :param course_url: URL of a course from Udemy.com | Example:
        :param user: username or email associated with Udemy.com Account
        :param pwd: password associated with Udemy.com Account
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
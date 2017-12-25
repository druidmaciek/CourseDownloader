"""
    To-Do
"""


class Skillshare(object):

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
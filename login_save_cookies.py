#!/usr/bin/env python
#################################################################
# Python Script to retrieve 1 online Data file of 'ds083.2',
# total 18.7M. This script uses 'requests' to download data.
#
# Highlight this script by Select All, Copy and Paste it into a file;
# make the file executable and run it on command line.
#
# You need pass in your password as a parameter to execute
# this script; or you can set an environment variable RDAPSWD
# if your Operating System supports it.
#
# Contact rpconroy@ucar.edu (Riley Conroy) for further assistance.
##########
# login the website:  https://rda.ucar.edu/ use existed cookies
# if not success, use account and password, and save cookies
# and then download FNL reanalysis data
#                   20th, April, 2019
#                       Wang Shi
#################################################################
import http.cookiejar as cookielib
import requests
import os,sys
class fnl_log(object):
    def __init__(self):
        self.fnlSession = requests.session()
        self.cookie_filename = 'FNLCookies.txt'
        self.fnlSession.cookies = cookielib.LWPCookieJar(filename = self.cookie_filename)
        self.url = 'https://rda.ucar.edu/cgi-bin/login'
        self.pswd = 'JvmXNdCQ'
        self.values = {'email' : 'robin_ouc@163.com', 'passwd' : self.pswd, 'action' : 'login'}
    def fnl_login(self):
        # Authenticate
        # ret = requests.post(url,data=values)
        self.ret = self.fnlSession.post(url = self.url,data=self.values)
        if self.ret.status_code != 200:
            print('Bad Authentication')
            print(self.ret.text)
            exit(1)
        else:
            self.fnlSession.cookies.save()
            print('Login success. \nCookie saved!')
    def log_status(self):
        # self.url_test = 'https://rda.ucar.edu/datasets/ds083.2/index.html#sfol-wl-/data/ds083.2?g=2'
        self.url_test = 'https://rda.ucar.edu/datasets/ds083.2/index.html#sfol-wl-/data/ds083.2?g=22019'
        self.res_test = self.fnlSession.get(self.url_test, cookies=self.fnlSession.cookies,  allow_redirects=False)
        print(f'log status is {self.res_test.status_code}')
        if self.res_test.status_code != 200:
            return False
        else:
            return True

    def check_file_status(self, filepath, filesize):
        sys.stdout.write('\r')
        sys.stdout.flush()
        size = int(os.stat(filepath).st_size)
        percent_complete = (size / filesize) * 100
        sys.stdout.write('%.1f %s' % (percent_complete, '% Completed'))
        sys.stdout.flush()
    def download_file(self):
        filename =  'http://rda.ucar.edu/data/ds083.2/grib2/2019/2019.04/fnl_20190429_12_00.grib2'
        file_base = os.path.basename(filename)
        req_file = requests.get(filename, cookies=self.fnlSession.cookies, allow_redirects=True, stream=True)
        path_grib = r'C:\Python_learn\pycharm\download_FNL\grib_file'
        # print(req_file.headers)
        filesize = int(req_file.headers['Content-length'])
        if not os.path.exists(file_base):
            print(f'downloading {file_base} ...')
            with open(os.path.join(path_grib,file_base), 'wb') as outfile:
                chunk_size = 1048576
                for chunk in req_file.iter_content(chunk_size=chunk_size):

                    outfile.write(chunk)
                    if chunk_size < filesize:
                        self.check_file_status(os.path.join(path_grib,file_base), filesize)
            self.check_file_status(os.path.join(path_grib,file_base), filesize)
            print()
        else:
            print(f'{file_base} already exists.')

if __name__ == '__main__':
    f1 = fnl_log()
    if os.path.exists(f1.cookie_filename):
        f1.fnlSession.cookies.load()
    else:
        print('cookie file not exists!')
        f1.fnl_login()

    try:
        f1.download_file()
    except:
        print('cookies invalid,login again ...')
        f1.fnl_login()
        f1.download_file()
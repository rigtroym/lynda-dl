#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time

from ._colorized import *
from ._extract import Lynda
from ._shared import (
        LyndaCourse, 
        LyndaChapters, 
        LyndaLectures, 
        LyndaLectureStream, 
        LyndaLectureAssets, 
        LyndaLectureSubtitles
    )

class InternLyndaCourse(LyndaCourse, Lynda):
    def __init__(self, *args, **kwargs):
        self._info    = ''
        super(InternLyndaCourse, self).__init__(*args, **kwargs)

    def _fetch_course(self):
        if self._have_basic:
            return
        if not self._cookies:
            auth = self._login(username=self._username, password=self._password, organization=self._organization)
        if self._cookies:
            auth = self._login(cookies=self._cookies)
        if auth.get('login') == 'successful':
            sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged in successfully.\n")
            sys.stdout.write('\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. \r")
            self._info              =       self._real_extract(self._url)
            sys.stdout.write('\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloaded course information .. (done)\r\n")
            self._id                =       self._info['course_id']
            self._title             =       self._info['course_title']
            self._chapters_count    =       self._info['total_chapters']
            self._total_lectures    =       self._info['total_lectures']
            self._description       =       self._info['description']
            self._short_description =       self._info['short_description']
            self._assets_count      =       self._info['assets_count']
            self._chapters          =       [InternLyndaChapter(z) for z in self._info['chapters']]
            sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Trying to logout now...\n")
            if not self._cookies:
                self._logout()
            sys.stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sb + "Logged out successfully.\n")
            self._have_basic = True
        if auth.get('login') == 'failed':
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Lynda Says : The username or password is invalid ..\n")
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Failed to login ..\n")
            sys.exit(0)

    def _process_assets(self):
        assets  =   [InternLyndaLectureAssets(z, self) for z in self._info['assets']] if self._assets_count > 0 else []#InternLyndaLectureAssets(self._info['asset'], self) if self._info['asset'].get('file_size') else {}
        self._assets = assets

class InternLyndaChapter(LyndaChapters):
    
    def __init__(self, chapter):
        super(InternLyndaChapter, self).__init__()

        self._chapter_id        = chapter['chapter_id']
        self._chapter_title     = chapter['chapter_title']
        self._chapter_index     = chapter['chapter_index']
        self._lectures_count    = chapter['lectures_count']
        self._lectures          = [InternLyndaLecture(z) for z in chapter['lectures']]


class InternLyndaLecture(LyndaLectures):

    def __init__(self, lectures):
        super(InternLyndaLecture, self).__init__()
        self._info              = lectures

        self._lecture_id        = self._info['lecture_id']
        self._lecture_title     = self._info['lecture_title']
        self._lecture_index     = self._info['lecture_index']
        
        self._sources_count     = self._info['sources_count']
        self._extension         = self._info.get('extension') or None
        self._duration          = self._info.get('duration') or None
        if self._duration:
            duration = int(self._duration)
            (mins, secs) = divmod(duration, 60)
            (hours, mins) = divmod(mins, 60)
            if hours == 0:
                self._duration = "%02d:%02d" % (mins, secs)
            else:
                self._duration = "%02d:%02d:%02d" % (hours, mins, secs)


    def _process_streams(self):
        streams = [InternLyndaLectureStream(z, self) for z in self._info['sources']] if self._sources_count > 0 else []
        self._streams = streams

    def _process_subtitles(self):
        subtitles = InternLyndaLectureSubtitles(self._info['subtitles'], self) if self._info['subtitles'].get('subtitle_data') else {}
        self._subtitles = subtitles


class InternLyndaLectureStream(LyndaLectureStream):

    def __init__(self, sources, parent):
        super(InternLyndaLectureStream, self).__init__(parent)

        self._mediatype = sources.get('type')
        self._extension = sources.get('extension')
        height = sources.get('height') or 0
        width = sources.get('width') or 0
        self._resolution = '%sx%s' % (width, height)
        self._dimention = width, height
        self._quality = self._resolution
        self._url = sources.get('download_url')


class InternLyndaLectureAssets(LyndaLectureAssets):

    def __init__(self, assets, parent):
        super(InternLyndaLectureAssets, self).__init__(parent)

        self._mediatype = assets.get('type')
        self._extension = assets.get('extension')
        self._filename = assets.get('filename')
        self._url = assets.get('download_url')
        self._fsize = assets.get('file_size')


class InternLyndaLectureSubtitles(LyndaLectureSubtitles):

    def __init__(self, subtitles, parent):
        super(InternLyndaLectureSubtitles, self).__init__(parent)

        self._mediatype = subtitles.get('type')
        self._extension = subtitles.get('extension')
        self._language = subtitles.get('language')
        self._data = subtitles.get('subtitle_data')
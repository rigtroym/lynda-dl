#!/usr/bin/python
from ._compat import (
                re,
                os,
                sys,
                time,
                pyver,
                requests,
                conn_error,
                compat_urlerr,
                compat_opener,
                compat_request,
                compat_urlopen,
                compat_httperr,
                HEADERS,
    )
early_py_version = sys.version_info[:2] < (2, 7)

class LyndaCourse(object):
    
    def __init__(self, url, username='', password='', organization='', cookies='', basic=True, callback=None):

        self._url = url
        self._username = username
        self._password = password
        self._cookies  = cookies 
        self._organization = organization
        self._callback = callback or (lambda x: None)
        self._have_basic = False

        self._id = None
        self._title = None
        self._chapters_count = 0
        self._total_lectures = 0
        self._description = None
        self._short_description = None
        self._assets_count = 0

        self._chapters = []
        self._assets = {}

        if basic:
            self._fetch_course()

    def _fetch_course(self):
        raise NotImplementedError

    @property
    def id(self):
        if not self._id:
            self._fetch_course()
        return self._id

    @property
    def title(self):
        if not self._title:
            self._fetch_course()
        return self._title

    @property
    def assets(self):
        if not self._assets:
            self._process_assets()
        return self._assets

    @property
    def chapters(self):
        if not self._chapters_count:
            self._fetch_course()
        return self._chapters_count

    @property
    def lectures(self):
        if not self._total_lectures:
            self._fetch_course()
        return self._total_lectures

    @property
    def description(self):
        return self._description

    @property
    def short_description(self):
        return self._short_description
    

    def get_chapters(self):
        if not self._chapters:
            self._fetch_course()
        return self._chapters

    def _write_to_file(self, data, filename):
        with open(filename, 'wb') as f:
            try:
                f.write(data)
            except Exception as e:
                retVal = {'status' : 'False', 'msg' : 'Python3 Exception : {}'.format(e)}
            else:
                retVal = {'status' : 'True', 'msg' : 'download'}
        f.close()

    def course_description(self, filepath):
        self.create_chapter(filepath=filepath)
        description_path = "%s\\%s-description.txt" % (filepath, self.title) if os.name == 'nt' else "%s/%s-description.txt" % (filepath, self.title)
        data = '''-------------------------------
  - Description
-------------------------------
 %s

------------------------------
  - Short Description
------------------------------
 %s''' % (self.description.encode('utf-8'), self.short_description.encode('utf-8'))
        return self._write_to_file(data, description_path)

    def create_chapter(self, filepath=''):
        try:
            os.makedirs(filepath)
        except Exception as e:
            return {'msg' : 'exists'}
        else:
            return {'msg' : 'created'}

class LyndaChapters(object):
    
    def __init__(self):

        self._chapter_id = None
        self._chapter_index = None
        self._chapter_title = None
        self._lectures_count = None

        self._lectures = []

    def __repr__(self):
        chapter = "{title}".format(title=self.title)
        return chapter

    @property
    def id(self):
        return self._chapter_id

    @property
    def index(self):
        return self._chapter_index

    @property
    def title(self):
        return self._chapter_title
    
    @property
    def lectures(self):
        return self._lectures_count

    def get_lectures(self):
        return self._lectures

class LyndaLectures(object):
    
    def __init__(self):

        self._best = None
        self._duration = None
        self._extension = None
        self._lecture_id = None
        self._lecture_title  = None
        self._lecture_index = None
        self._sources_count = 0

        self._streams = []
        self._subtitles = []

    def __repr__(self):
        lecture = "{title}".format(title=self.title)
        return lecture
    
    @property
    def id(self):
        return self._lecture_id

    @property
    def index(self):
        return self._lecture_index

    @property
    def title(self):
        return self._lecture_title
    
    @property
    def duration(self):
        return self._duration

    @property
    def extension(self):
        return self._extension

    @property
    def streams(self):
        if not self._streams:
            self._process_streams()
        return self._streams

    @property
    def subtitles(self):
        if not self._subtitles:
            self._process_subtitles()
        return self._subtitles

    def _getbest(self):
        streams = self.streams
        if not streams:
            return None
        def _sortkey(x, keyres=0, keyftype=0):
            keyres = int(x.resolution.split('x')[0])
            keyftype = x.extension
            st = (keyftype, keyres)
            return st
        
        self._best = max(streams, key=_sortkey)
        return self._best

    def getbest(self):
        return self._getbest()

    def get_quality(self, best_quality='', streams='', requested=''):
        best = best_quality
        if requested:
            index = 0
            while index < len(streams):
                dimension = int(streams[index].dimention[1])
                if dimension == requested:
                    best = streams[index]
                    break
                index += 1
        return best

class LyndaLectureStream(object):
    
    def __init__(self, parent):

        self._mediatype = None
        self._quality = None
        self._resolution = None
        self._dimention = None
        self._extension = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.extension, self.quality)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += "." + self.extension
        return filename

    @property
    def resolution(self):
        return self._resolution

    @property
    def quality(self):
        return self._quality

    @property
    def url(self):
        return self._url

    @property
    def id(self):
        return self._parent.id

    @property
    def dimention(self):
        return self._dimention

    @property
    def extension(self):
        return self._extension

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def title(self):
        return self._parent.title

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        if not self._fsize:
            try:
                cl = 'content-length'
                self._fsize = int(requests.get(self.url, stream=True, headers={'User-Agent': HEADERS.get('User-Agent')}).headers[cl])
            except conn_error as e:
                self._fsize = 0
        return self._fsize


    def download(self, filepath="", quiet=False, callback=lambda *x: None):
        savedir = filename = ""
        retVal  = {}

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self.filename

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename

        filepath = os.path.join(savedir, filename)

        if os.path.isfile(filepath):
            retVal = {"status" : "True", "msg" : "already downloaded"}
            return retVal
        
        temp_filepath = filepath + ".part"

        status_string = ('  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} '
                         'KB/s].  ETA: [{:.0f} secs]')


        if early_py_version:
            status_string = ('  {0:} Bytes [{1:.2%}] received. Rate:'
                             ' [{2:4.0f} KB/s].  ETA: [{3:.0f} secs]')

        try:    
            req = compat_request(self.url, headers={'User-Agent' : HEADERS.get('User-Agent')})
            response = compat_urlopen(req)
        except compat_urlerr as e:
            retVal  =   {"status" : "False", "msg" : "URLError : either your internet connection is not working or server aborted the request"}
            return retVal
        except compat_httperr as e:
            if e.code == 401:
                retVal  =   {"status" : "False", "msg" : "Udemy Says (HTTP Error 401 : Unauthorized)"}
            else:
                retVal  =   {"status" : "False", "msg" : "HTTPError-{} : direct download link is expired run the udemy-dl with '--skip-sub' option ...".format(e.code)}
            return retVal
        else:
            total = int(response.info()['Content-Length'].strip())
            chunksize, bytesdone, t0 = 16384, 0, time.time()

            fmode, offset = "wb", 0

            if os.path.exists(temp_filepath):
                if os.stat(temp_filepath).st_size < total:
                    offset = os.stat(temp_filepath).st_size
                    fmode = "ab"

            try:
                outfh = open(temp_filepath, fmode)
            except Exception as e:
                if os.name == 'nt':
                    file_length = len(temp_filepath)
                    if file_length > 255:
                        retVal  =   {"status" : "False", "msg" : "file length is too long to create. try downloading to other drive (e.g :- -o 'E:\\')"}
                        return retVal
                retVal  =   {"status" : "False", "msg" : "Reason : {}".format(e)}
                return retVal

            if offset:
                resume_opener = compat_opener()
                resume_opener.addheaders = [('User-Agent', HEADERS.get('User-Agent')),
                                            ("Range", "bytes=%s-" % offset)]
                try:
                    response = resume_opener.open(self.url)
                except compat_urlerr as e:
                    retVal  =   {"status" : "False", "msg" : "URLError : either your internet connection is not working or server aborted the request"}
                    return retVal
                except compat_httperr as e:
                    if e.code == 401:
                        retVal  =   {"status" : "False", "msg" : "Udemy Says (HTTP Error 401 : Unauthorized)"}
                    else:
                        retVal  =   {"status" : "False", "msg" : "HTTPError-{} : direct download link is expired run the udemy-dl with '--skip-sub' option ...".format(e.code)}
                    return retVal
                else:
                    bytesdone = offset

            self._active = True
            while self._active:
                chunk = response.read(chunksize)
                outfh.write(chunk)
                elapsed = time.time() - t0
                bytesdone += len(chunk)
                if elapsed:
                    try:
                        rate = ((float(bytesdone) - float(offset)) / 1024.0) / elapsed
                        eta  = (total - bytesdone) / (rate * 1024.0)
                    except ZeroDivisionError as e:
                        outfh.close()
                        try:
                            os.unlink(temp_filepath)
                        except Exception as e:
                            pass
                        retVal = {"status" : "False", "msg" : "ZeroDivisionError : it seems, lecture has malfunction or is zero byte(s) .."}
                        return retVal
                else:
                    rate = 0
                    eta = 0
                progress_stats = (bytesdone, bytesdone * 1.0 / total, rate, eta)

                if not chunk:
                    outfh.close()
                    break
                if not quiet:
                    status = status_string.format(*progress_stats)
                    sys.stdout.write("\r" + status + ' ' * 4 + "\r")
                    sys.stdout.flush()

                if callback:
                    callback(total, *progress_stats)

            if self._active:
                os.rename(temp_filepath, filepath)
                retVal = {"status" : "True", "msg" : "download"}
            else:
                outfh.close()
                retVal = {"status" : "True", "msg" : "download"}

        return retVal

class LyndaLectureSubtitles(object):
    
    def __init__(self, parent):

        self._mediatype = None
        self._extension = None
        self._language = None
        self._data = None

        self._parent = parent
        self._filename = None

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.language, self.extension)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += "-{}.{}".format(self.language, self.extension)
        return filename

    @property
    def id(self):
        return self._parent.id
    
    @property
    def data(self):
        return self._data

    @property
    def extension(self):
        return self._extension

    @property
    def language(self):
        return self._language

    @property
    def title(self):
        return self._parent.title

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def mediatype(self):
        return self._mediatype

    def download(self, filepath=""):
        savedir = filename = ""
        retVal  = {}

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self.filename

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename

        filepath = os.path.join(savedir, filename)

        if os.path.isfile(filepath):
            retVal = {"status" : "True", "msg" : "already downloaded"}
            return retVal
        
        with open(filepath, 'w') as f:
            try:
                f.write(self.data)
            except Exception as e:
                retVal = {'status' : 'False', 'msg' : '{}'.format(e)}
            else:
                retVal = {'status' : 'True', 'msg' : 'download'}
        f.close()
        return retVal

class LyndaLectureAssets(object):
    
    def __init__(self, parent):

        self._extension = None
        self._mediatype = None
        self._url = None

        self._parent = parent
        self._filename = None
        self._fsize = None
        self._active = False

    def __repr__(self):
        out = "%s:%s@%s" % (self.mediatype, self.extension, self.extension)
        return out

    def _generate_filename(self):
        ok = re.compile(r'[^\\/:*?"<>|]')
        filename = "".join(x if ok.match(x) else "_" for x in self.title)
        filename += ".{}".format(self.extension)
        return filename

    @property
    def id(self):
        return self._parent.id

    @property
    def url(self):
        return self._url

    @property
    def extension(self):
        return self._extension

    @property
    def title(self):
        return self._parent.title

    @property
    def filename(self):
        if not self._filename:
            self._filename = self._generate_filename()
        return self._filename

    @property
    def mediatype(self):
        return self._mediatype

    def get_filesize(self):
        return self._fsize


    def download(self, filepath="", quiet=False, callback=lambda *x: None):
        savedir = filename = ""
        retVal  = {}

        if filepath and os.path.isdir(filepath):
            savedir, filename = filepath, self.filename

        elif filepath:
            savedir, filename = os.path.split(filepath)

        else:
            filename = self.filename

        filepath = os.path.join(savedir, filename)

        if os.path.isfile(filepath):
            retVal = {"status" : "True", "msg" : "already downloaded"}
            return retVal
        
        temp_filepath = filepath + ".part"

        status_string = ('  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} '
                         'KB/s].  ETA: [{:.0f} secs]')


        if early_py_version:
            status_string = ('  {0:} Bytes [{1:.2%}] received. Rate:'
                             ' [{2:4.0f} KB/s].  ETA: [{3:.0f} secs]')

        try:    
            req = compat_request(self.url, headers={'User-Agent' : HEADERS.get('User-Agent')})
            response = compat_urlopen(req)
        except compat_urlerr as e:
            retVal  =   {"status" : "False", "msg" : "URLError : either your internet connection is not working or server aborted the request"}
            return retVal
        except compat_httperr as e:
            if e.code == 401:
                retVal  =   {"status" : "False", "msg" : "Udemy Says (HTTP Error 401 : Unauthorized)"}
            else:
                retVal  =   {"status" : "False", "msg" : "HTTPError-{} : direct download link is expired run the udemy-dl with '--skip-sub' option ...".format(e.code)}
            return retVal
        else:
            total = int(response.info()['Content-Length'].strip())
            chunksize, bytesdone, t0 = 16384, 0, time.time()

            fmode, offset = "wb", 0

            if os.path.exists(temp_filepath):
                if os.stat(temp_filepath).st_size < total:
                    offset = os.stat(temp_filepath).st_size
                    fmode = "ab"

            try:
                outfh = open(temp_filepath, fmode)
            except Exception as e:
                if os.name == 'nt':
                    file_length = len(temp_filepath)
                    if file_length > 255:
                        retVal  =   {"status" : "False", "msg" : "file length is too long to create. try downloading to other drive (e.g :- -o 'E:\\')"}
                        return retVal
                retVal  =   {"status" : "False", "msg" : "Reason : {}".format(e)}
                return retVal

            if offset:
                resume_opener = compat_opener()
                resume_opener.addheaders = [('User-Agent', HEADERS.get('User-Agent')),
                                            ("Range", "bytes=%s-" % offset)]
                try:
                    response = resume_opener.open(self.url)
                except compat_urlerr as e:
                    retVal  =   {"status" : "False", "msg" : "URLError : either your internet connection is not working or server aborted the request"}
                    return retVal
                except compat_httperr as e:
                    if e.code == 401:
                        retVal  =   {"status" : "False", "msg" : "Udemy Says (HTTP Error 401 : Unauthorized)"}
                    else:
                        retVal  =   {"status" : "False", "msg" : "HTTPError-{} : direct download link is expired run the udemy-dl with '--skip-sub' option ...".format(e.code)}
                    return retVal
                else:
                    bytesdone = offset

            self._active = True
            while self._active:
                chunk = response.read(chunksize)
                outfh.write(chunk)
                elapsed = time.time() - t0
                bytesdone += len(chunk)
                if elapsed:
                    try:
                        rate = ((float(bytesdone) - float(offset)) / 1024.0) / elapsed
                        eta  = (total - bytesdone) / (rate * 1024.0)
                    except ZeroDivisionError as e:
                        outfh.close()
                        try:
                            os.unlink(temp_filepath)
                        except Exception as e:
                            pass
                        retVal = {"status" : "False", "msg" : "ZeroDivisionError : it seems, lecture has malfunction or is zero byte(s) .."}
                        return retVal
                else:
                    rate = 0
                    eta = 0
                progress_stats = (bytesdone, bytesdone * 1.0 / total, rate, eta)

                if not chunk:
                    outfh.close()
                    break
                if not quiet:
                    status = status_string.format(*progress_stats)
                    sys.stdout.write("\r" + status + ' ' * 4 + "\r")
                    sys.stdout.flush()

                if callback:
                    callback(total, *progress_stats)

            if self._active:
                os.rename(temp_filepath, filepath)
                retVal = {"status" : "True", "msg" : "download"}
            else:
                outfh.close()
                retVal = {"status" : "True", "msg" : "download"}

        return retVal
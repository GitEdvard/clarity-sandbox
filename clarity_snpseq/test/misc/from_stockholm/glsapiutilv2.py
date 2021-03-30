import urllib.request, urllib.error, urllib.parse
import re
import sys

DEBUG = 0


class glsapiutil:

    def __init__(self):
        if DEBUG > 0: print(self.__module__ + " init called")
        self.hostname = ""
        self.auth_handler = ""

    def setHostname(self, hostname):
        if DEBUG > 0: print(self.__module__ + " setHostname called")
        self.hostname = hostname

    def setup(self, user, password):

        if DEBUG > 0: print(self.__module__ + " setup called")

        ## setup up API plumbing
        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, self.hostname + '/api/v2', user, password)
        self.auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
        opener = urllib.request.build_opener(self.auth_handler)
        urllib.request.install_opener(opener)

    def createObject(self, xmlObject, url):

        if DEBUG > 0: print(self.__module__ + " createObject called")

        global auth_handler

        opener = urllib.request.build_opener(self.auth_handler)

        req = urllib.request.Request(url)
        req.add_data(xmlObject)
        req.get_method = lambda: 'POST'
        req.add_header('Accept', 'application/xml')
        req.add_header('Content-Type', 'application/xml')
        req.add_header('User-Agent', 'Python-urllib2/2.4')

        responseText = "EMPTY"

        try:
            response = opener.open(req)
            responseText = response.read()
        except urllib.error.HTTPError as e:
            responseText = e.read()
        except:
            responseText = str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])

        return responseText

    def updateObject(self, xmlObject, url):

        if DEBUG > 0: print(self.__module__ + " updateObject called")

        global auth_handler

        opener = urllib.request.build_opener(self.auth_handler)

        req = urllib.request.Request(url)
        req.add_data(xmlObject)
        req.get_method = lambda: 'PUT'
        req.add_header('Accept', 'application/xml')
        req.add_header('Content-Type', 'application/xml')
        req.add_header('User-Agent', 'Python-urllib2/2.4')

        responseText = "EMPTY"

        try:
            response = opener.open(req)
            responseText = response.read()
        except urllib.error.HTTPError as e:
            responseText = e.read()
        except:
            responseText = str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])

        return responseText

    def getResourceByURI(self, url):

        if DEBUG > 0: print(self.__module__ + " getResourceByURI called")

        responseText = ""
        xml = ""

        try:
            xml = urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as e:
            responseText = e.read()
            if responseText.startswith("<?xml"):
                xml = responseText
                responseText = ""
        except:
            responseText = str(sys.exc_info()[0]) + str(sys.exc_info()[1])

        if len(responseText) > 0:
            print("Error trying to access " + url)
            print(responseText)

        return xml

    def getInnerXml(self, xml, tag):
        tagname = '<' + tag + '.*?>'
        inXml = re.sub(tagname, '', xml)

        tagname = '</' + tag + '>'
        inXml = inXml.replace(tagname, '')

        return inXml

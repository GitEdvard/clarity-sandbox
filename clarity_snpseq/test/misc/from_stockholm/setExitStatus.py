import sys
import getopt
import glsapiutilv2
import re
from genologics.config import BASEURI, USERNAME, PASSWORD

def setFinalStatus(uri, status, message):
    newuri = uri + '/programstatus'
    XML = api.getResourceByURI(newuri)
    newXML = re.sub('(.*<status>)(.*)(<\/status>.*)', '\\1' + status + '\\3', XML)
    newXML = re.sub('(.*<\/status>)(.*)', '\\1' + '<message>' + message + '</message>' + '\\2', newXML)
    response = api.updateObject(newXML, newuri)
    return newXML, XML, response

def main():

    global api

    status = "ERROR"
    message = "This is an error message"
    pURI = "https://lims-dev.snpseq.medsci.uu.se/api/v2/steps/24-15793"

    api = glsapiutilv2.glsapiutil()
    api.setHostname( BASEURI )
    api.setup( USERNAME, PASSWORD )

    new_xml = setFinalStatus( pURI, status, message )
    return new_xml


if __name__ == "__main__":
    main()


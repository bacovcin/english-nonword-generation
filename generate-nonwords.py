import urllib.request
import zipfile

SUBTLEX_URL = "http://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus/subtlexus2.zip/at_download/file"

def init():
    zippedsubfilename, headers = urllib.request.urlretrieve(SUBTLEX_URL)
    print(zippedsubfilename)
    print(headers)
    with open(zippedsubfilename) as zippedsubfile:
        with zipfile.ZipFile(zippedsubfile) as subfile:
            print(subfile.namelist())

if __name__ == '__main__':
    init()

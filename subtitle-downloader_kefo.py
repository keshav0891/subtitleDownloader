#-------------------------------------------------------------------------------
# Name      : Subtitle downloader
# Purpose   : One step subtitle download

# Currently using SubDB and Subscene for database
#-------------------------------------------------------------------------------

import hashlib
import os
import sys
import logging
import requests,time,re,zipfile
from bs4 import BeautifulSoup
from os.path import basename
PY_VERSION = sys.version_info[0]
if PY_VERSION == 2:
    import urllib2
if PY_VERSION == 3:
    import urllib.request


def get_hash(file_path):
    read_size = 64 * 1024
    with open(file_path, 'rb') as f:
        data = f.read(read_size)
        f.seek(-read_size, os.SEEK_END)
        data += f.read(read_size)
    return hashlib.md5(data).hexdigest()


def sub_downloader(file_path):
    # Put the code in a try catch block in order to continue for other video files, if it fails during execution
    try:
        # Skip this file if it is not a video
	root, extension = os.path.splitext(file_path)
        if extension not in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
            return
	
        if not os.path.exists(root + ".srt"):
	    print "fetching from subDB for ", file_path
            headers = {'User-Agent': 'SubDB/1.0 (subtitle-downloader/1.0; http://github.com/)'}
            url = "http://api.thesubdb.com/?action=download&hash=" + get_hash(file_path) + "&language=en"
            if PY_VERSION == 3:
                req = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(req).read()
            if PY_VERSION == 2:
                req = urllib2.Request(url, '', headers)
                response = urllib2.urlopen(req).read()

            with open(root + ".srt", "wb") as subtitle:
		print "writing files at ", root
                subtitle.write(response)
              
    except:
        #print "not found on subDB"
        sub_downloader2(file_path)

def sub_downloader2(file_path):
	try:		
		
		#print "current working directory for call is ", os.getcwd() 		
		root, extension = os.path.splitext(file_path)
		if extension not in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
			return	
		if os.path.exists(root + ".srt"):
			return
		print "fetching srt from subscene for ", file_path
		r=requests.get("http://subscene.com/subtitles/release?q="+root);
		soup=BeautifulSoup(r.content,"lxml")
		atags=soup.find_all("a")
		href=""
		for i in range(0,len(atags)):
			spans=atags[i].find_all("span")
			if(len(spans)==2 and spans[0].get_text().strip()=="English"):
				href=atags[i].get("href").strip()				
		if(len(href)>0):
			r=requests.get("http://subscene.com"+href);
			soup=BeautifulSoup(r.content,"lxml")
			lin=soup.find_all('a',attrs={'id':'downloadButton'})[0].get("href")
			r=requests.get("http://subscene.com"+lin);
			soup=BeautifulSoup(r.content,"lxml")
			subfile=open(root + ".zip", 'wb')
			for chunk in r.iter_content(100000):
				subfile.write(chunk)
				subfile.close()
				time.sleep(1)
				zip=zipfile.ZipFile(root + ".zip")
				zip.extractall(root)
				zip.close()
				os.unlink(root + ".zip")		
	except:
		#Ignore exception and continue
		print "Error in fetching subtitle from subscene for " + file_path

def downloadSRT(path):
    if os.path.isdir(path):
      for root_path, dir_paths, file_names in os.walk(path):
	for filename in file_names:
          print "iterating paths in the give directory"
	  sub_downloader(os.path.join(root_path, filename))
        for dir_path in dir_paths:
          downloadSRT(os.path.join(root_path, dir_path))
    else:
      sub_downloader(path)

def main():
    if len(sys.argv) == 1:
        print("This program requires at least one parameter")
        sys.exit(1)

    path = sys.argv[1]
    downloadSRT(path)    

if __name__ == '__main__':
    main()

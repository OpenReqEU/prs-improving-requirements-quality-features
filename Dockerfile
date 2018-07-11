# python 2.7.15 (latest) on debian stretch
FROM 	python:2.7.15-stretch


# copy code and change wd
COPY	. /home/openreq
WORKDIR	/home/openreq


# install python dependencies
RUN		pip install -r requirements.txt --no-cache-dir  && \
		python2 -m spacy download en  && \
		python2 -m nltk.downloader punkt wordnet	

		
# install java and tesseract
RUN		apt-get update \
		&& apt-get install openjdk-8-jre-headless gdal-bin tesseract-ocr --no-install-recommends\
			tesseract-ocr-eng -y
	
		
# Expose port
EXPOSE	5007 


# start app
CMD	["python2", "app.py"]
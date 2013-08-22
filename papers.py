#!/usr/bin/env python

import requests
import BeautifulSoup
import time, datetime

def get_pubmed_ids():
	payload={'db':'pubmed'}
	payload['term'] = '"department of biology"  AND "georgetown university" AND 2013[pdat]'

	pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
	r = requests.get(pubmed_url, params=payload)

	soup = BeautifulSoup.BeautifulSoup(r.text)

	ids = soup.findAll('id')
	pubmed_ids = (i.contents[0] for i in ids)
	return pubmed_ids

def process_publication_info(pubmed_ids):
	id_list = ",".join(pubmed_ids)

	payload = {'db':'pubmed', 'id':id_list}
	summary_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
	r = requests.get(summary_url, params=payload)

	soup = BeautifulSoup.BeautifulSoup(r.text)
	docsums = soup.findAll('docsum')

	for doc in docsums:
		date_string = doc.find('item', attrs={'name':"PubDate"}).text

		try: 
			pub_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y %b %d")))
		except ValueError:
			try:
				pub_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y %b")))
			except ValueError: 
				pub_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y")))

		pub = {}
		pub['publication_date'] = pub_date
		pub['title'] = doc.find('item', attrs={'name':'Title'}).text
		pub['authors'] = ', '.join([x.text for x in doc.findAll(attrs={'name':'Author'})])
		pub['journal'] = doc.find('item', attrs={'name':"Source"}).text 
		pub['citation_string'] = doc.find('item', attrs={'name':"SO"}).text
		pub['pubmed_uid'] = doc.id.text
		pub['url'] = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % pub['pubmed_uid']
		print pub



if __name__ == '__main__':
	pubmed_ids = get_pubmed_ids()
	process_publication_info(pubmed_ids)




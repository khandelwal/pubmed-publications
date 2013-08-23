#!/usr/bin/env python

import requests
import BeautifulSoup
import time, datetime

def get_pubmed_ids(year):
	payload={'db':'pubmed'}
	payload['term'] = '"department of biology"  AND "georgetown university" AND %s[pdat]' % year

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

	pub_list = []
	for doc in docsums:
		date_string = doc.find('item', attrs={'name':"PubDate"}).text

		try: 
			pub_date = datetime.datetime.fromtimestamp(
				time.mktime(time.strptime(date_string, "%Y %b %d")))
		except ValueError:
			try:
				pub_date = datetime.datetime.fromtimestamp(
					time.mktime(time.strptime(date_string, "%Y %b")))
			except ValueError: 
				try:
					pub_date = datetime.datetime.fromtimestamp(
						time.mktime(time.strptime(date_string, "%Y")))
				except ValueError:
					print date_string


		pub = {}
		pub['publication_date'] = pub_date
		pub['title'] = doc.find('item', attrs={'name':'Title'}).text
		pub['authors'] = ', '.join([x.text for x in doc.findAll(attrs={'name':'Author'})])
		pub['journal'] = doc.find('item', attrs={'name':"Source"}).text 
		pub['citation_string'] = doc.find('item', attrs={'name':"SO"}).text
		pub['pubmed_uid'] = doc.id.text
		pub['url'] = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % pub['pubmed_uid']
		pub_list.append(pub)
	return pub_list

def write_html_page(pubs):
	""" Write out the publication information to a basic HTML page. """

	f = open('publications.html', 'w')
	f.write(
		"""
		<html>
		<head>
		<title>
			Georgetown Faculty Publications
		</title>
		<body>\n
		""")
	for year, pub_list in pubs:
		f.write("<h2> %s </h2>" % year)

		pub_list = sorted(pub_list, key=lambda x: x['publication_date'], reverse=True)

		for pub in pub_list:
			f.write("<p>\n")
			f.write('<a href="%s">%s</a><br />\n' % (pub['url'], pub['title'] ))
			f.write("%s <br />\n" % pub['authors'].encode('utf-8'))
			f.write("%s %s <br />\n" % (pub['journal'], pub['citation_string']))
			f.write("</p>\n")

	f.write(
		"""
		</body>
		</html>\n
		""")

if __name__ == '__main__':
	pubs = []
	years = [2013, 2012, 2011, 2010, 2009]
	for year in years:
		pubmed_ids = get_pubmed_ids(year)
		pub_list = process_publication_info(pubmed_ids)
		pubs.append((year, pub_list))
	write_html_page(pubs)

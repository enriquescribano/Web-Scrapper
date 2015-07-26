from bs4 import BeautifulSoup
import requests
import json


SO_URL = "http://stackoverflow.com"
QUESTION_LIST_URL = SO_URL + "/questions"
MAX_PAGE_COUNT = 5

global_results = []
initial_page = 1 #first page is page 1

def get_author_name(body):
	link_name = body.select(".user-details a")
	if len(link_name) == 0:
		text_name = body.select(".user-details")
		return text_name[0].text if len(text_name) > 0 else 'N/A'
	else:
		return link_name[0].text

def get_question_answers(body):
	answers = body.select(".answer")
	a_data = []
	if len(answers) == 0:
		return a_data

	for a in answers:
		data = {
			'body': a.select(".post-text")[0].get_text(),
			'author': get_author_name(a) 
		}
		a_data.append(data)
	return a_data

def get_question_data ( url ): 
	print "Getting data from question page: %s " % (url)
	resp = requests.get(url)
	if resp.status_code != 200:
		print "Error while trying to scrape url: %s" % (url)
		return
	body_soup = BeautifulSoup(resp.text)
	#define the output dict that will be turned into a JSON structue
	q_data = {
		'title': body_soup.select('#question-header .question-hyperlink')[0].text,
		'body': body_soup.select('#question .post-text')[0].get_text(),
		'author': get_author_name(body_soup.select(".post-signature.owner")[0]),
		'answers': get_question_answers(body_soup)
	}
	return q_data


def get_questions_page ( page_num, partial_results ):
	print "====================================================="
	print " Getting list of questions for page %s" % (page_num)
	print "====================================================="

	url = QUESTION_LIST_URL + "?sort=newest&page=" + str(page_num)
	resp = 	requests.get(url)
	if resp.status_code != 200:
		print "Error while trying to scrape url: %s" % (url)
		return
	body = resp.text
	main_soup = BeautifulSoup(body)

	#get the urls for each question
	questions = main_soup.select('.question-summary .question-hyperlink')
	urls = [ SO_URL + x['href'] for x in questions]
	for url in urls:
		q_data = get_question_data(url)
		partial_results.append(q_data)
	if page_num < MAX_PAGE_COUNT:
		get_questions_page(page_num + 1, partial_results)


get_questions_page(initial_page, global_results)
with open('scrapping-results.json', 'w') as outfile:
	json.dump(global_results, outfile, indent=4)

print '----------------------------------------------------'
print 'Results saved'


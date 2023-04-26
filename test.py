import csv
from bs4 import BeautifulSoup
import requests

# urlからタイトルを抽出する関数
def get_title(url):
	html = requests.get(url)
	soup = BeautifulSoup(html.content, "html.parser")
	if soup.find('title') is None:
		title='non-title'
	else:
		title=soup.find('title').text
	return title
	# except requests.exceptions.RequestException:
	# 	print('get-----non-responsed-url')
	# 	return 'non-responsed'

# f='https://www.ncctv.co.jp/'
# print(get_title(f))

csv_file = open("./all_www.ncctv.co.jp.csv", "r", encoding="ms932", errors="", newline="" )
#リスト形式
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)


all_pages = open('./new_all_pages.csv', 'w', encoding='CP932', errors='ignore')

# header=next(f)
for row in f:
	url=(row[1])
	title=get_title(url)
	print(title)
	print(url)
	all_pages.write(title + ','+url+'\n')

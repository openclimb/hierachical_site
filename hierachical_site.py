from bs4 import BeautifulSoup
import requests
import sys
import threading
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
# from urllib.request import urlretrievepyts
from os import makedirs
import os.path, time, re

# 変更前の再帰関数の実行回数の上限を表示
print("変更前の再帰関数の実行回数の上限")
print(sys.getrecursionlimit())

sys.setrecursionlimit(67108864) #64MB
threading.stack_size(1024*1024)  #2の20乗のstackを確保=メモリの確保

# 変更後の再帰関数の実行回数の上限を表示
print("変更後の再帰関数の実行回数の上限")
print(sys.getrecursionlimit())

# ターゲットのドメインを指定
target_domain = 'https://www.ncctv.co.jp/'
domain = 'www.ncctv.co.jp'
# target_domain = 'http://hmc.me.es.osaka-u.ac.jp/'
# domain = 'hmc.me.es.osaka-u.ac.jp'

# 記事の余分なデータを含まないようにするため/の最大数を定義
max_slash = 1000

# 無視する拡張子
ignore_lis = ['.jpg','.png','.pdf']


# 同じページにアクセスしないようにするグローバル変数
sugi_files = {}
sugi_html = {}
all_url=[]
non_title_list={}
non_response_list=[]

def check(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    # print(response.status_code)
    except requests.exceptions.RequestException:
        return False
    return True




# urlからタイトルを抽出する関数
def get_title(url):
	try:
		# if not check(url): return('non-title')
		html = requests.get(url)
		soup = BeautifulSoup(html.content, "html.parser")
		if soup.find('title') is None:
			title='non-title'
		else:
			title=soup.find('title').text
		return title
	except requests.exceptions.RequestException:
		print('get-----non-responsed-url')
		non_response_list.append(url)
		return 'non-responsed'

# aタグを抽出する関数
def enum_links(html, base):
	soup = BeautifulSoup(html, "html.parser")
	# links = soup.select("link[rel='stylesheet']")
	links = soup.select("a[href]")
	result = []

	for a in links:
		href = a.attrs['href']
		base2=base
		
		# hrefの最後の文字が/の時削除
		# if len(href)>0 and href[-1]=='/':
		# 	href=href[:-1]
		# if base2[-1]=='/':
		# 	base2=base2[:-1]

		# # ../といったやつがある場合の処理
		# ll=href.count('..')+1
		# base_lis = base2.split('/')
		# for i in range(ll):
		# 	base_lis[-1-i]=''
		# base2='/'.join(base_lis)

		ignore_flag = False
		# 特定の拡張子がある場合は無視
		for ignore_fac in ignore_lis:
			if ignore_fac in href:
				ignore_flag = True
				break
		if ignore_flag:
			continue


		# **************.htmlなどといった14桁の数字のhtmlは無視
		# href_lis = href.split('/')
		# if re.compile('[0-9]{14}').match(href_lis[-1]):
		# 	continue
		# # 8桁の数字のhtmlは無視
		# if re.compile('[0-9]{8}').match(href_lis[-1]): continue
		# if re.compile('[0-9]{5}').search(href_lis[-1]): continue
		# if len(href_lis)>=3:
		# 	if re.compile('[0-9]{4}').match(href_lis[-2]): continue
		# 	if re.compile('[0-9]{4}').match(href_lis[-3]): continue
		# # index.html以外でhtmlがつく奴は無視
		# # elif '.html' in href_lis[-1]: continue
		# href='/'.join(href_lis)

		# 結合
		if 'http' in href:
			url = href
		else:
			url = urljoin(base2, href)

		o=urlparse(url)
		saveurl=o.scheme+'://'+o.netloc+o.path

		# 一度テキストファイルに入れたものは再度入れないようにするif文
		if saveurl in sugi_html : continue
		# ドメイン名が違うやつは無効
		if not domain in saveurl : continue
		# 長いURLは無効https://aaa/a/33/4/5/6みたいなやつ
		# l = len(saveurl.split('/'))
		# if l > max_slash+3: continue
		result.append(saveurl)
	return result

# ネットからファイルをダウンロードする
def download_file(url):
	o = urlparse(url)
	savepath = "./" + o.netloc + o.path
	if re.search(r"/$", savepath):
		# savepath += "index.html"
		savepath += ""
	savedir = os.path.dirname(savepath)

	if os.path.exists(savepath): return savepath

	if not os.path.exists(savedir):
		print("mkdir=", savedir)
		makedirs(savedir)
		f = open(savedir+'/'+savedir.split('/')[-1]+'.csv', 'w', encoding='CP932', errors='ignore')

	try:
		print("download=", url)
		all_url.append(url)
		# urlretrieve(url, savepath)
		# time.sleep(1)

		return savepath
	except:
		print("ダウンロード失敗:", url)
		return None

# htmlファイルを解析してリンク先をダウンロードする
def analize_html(url, root_url):
	savepath = download_file(url)

	o = urlparse(url)
	savepath2 = "./" + o.netloc + o.path
	
	# o.pathに'//'があると置換
	if '//' in o.path: o.path.replace('//','/')

	savedir = os.path.dirname(savepath2)
	
	if savepath is None: return
	if savepath in sugi_files: return
	# 長いURLは無効https://aaa/a/33/4/5/6みたいなやつ
	l = len(savepath.split('/'))
	if l > max_slash: return
	sugi_files[savepath] = True
	sugi_html[o.scheme+'://'+o.netloc+o.path] = True
	print("analize_html=", url)
	# html = open(savepath, "r", encoding="utf-8").read()
	try:
		html = requests.get(url)
		# links = enum_links(html, url)
		links = enum_links(html.content, url)
		f = open(savedir+'/'+savedir.split('/')[-1]+'.csv', 'w', encoding='CP932', errors='ignore')
		output_list = list(sorted(set(links)))
		non_title_list[url]=[]
		for output in output_list:
			f.write(get_title(output)+','+output+'\n')
			if get_title(output) == 'non-title':
				non_title_list[url].append(output)
		# f.write("\n".join(output_list))
	
		for link_url in links:		
			if link_url.find(root_url) != 0:
				if not re.search(r".css$", link_url): continue
			if link_url.find(root_url) != 0:
				if not re.search(r".c$", link_url): continue
			# jpg,png,pdfは無視
			if link_url.find(root_url) != 0:
				if not re.search(r".png$", link_url): continue
			if link_url.find(root_url) != 0:
				if not re.search(r".jpg$", link_url): continue
			if link_url.find(root_url) != 0:
				if not re.search(r".pdf$", link_url): continue

				# if re.search(r".(html|htm)$", link_url):
			analize_html(link_url, root_url)
			
			# continue
			
			download_file(link_url)
	except requests.exceptions.RequestException:
		print('error response')
		non_response_list.append(url)

if __name__ == "__main__":
	url = target_domain
	analize_html(url, url)

# non-titleの遷移元urlを探す
non_title_ref = open('./non_title_'+domain+'.csv', 'w', encoding='CP932', errors='ignore')
for key in non_title_list.keys():
	value=non_title_list[key]
	if value==[]:continue
	non_title_ref.write(key+'\n')
	for i in value:
		non_title_ref.write(','+i+'\n')

# レスポンスエラーのurlを書き出す
non_response_table = open('./non_response_'+domain+'.csv', 'w', encoding='CP932', errors='ignore')
for url in non_response_list:
	non_response_table.write(url+'\n')

# 全てをひとつのファイルにする
all_file = open('./all_'+domain+'.csv', 'w', encoding='CP932', errors='ignore')
all_url=list(sorted(set(all_url)))
for u in all_url:
	all_file.write(get_title(u)+','+u+'\n')






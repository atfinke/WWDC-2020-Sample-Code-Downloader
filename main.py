from bs4 import BeautifulSoup
import urllib.request
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from queue import Queue
from threading import Thread

def article_links():
    article_links = []
    
    url = 'https://developer.apple.com/wwdc20/sample-code/'
    soup = BeautifulSoup(urllib.request.urlopen(url), features='html.parser')

    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'https://developer.apple.com/documentation/' in href:
            article_links.append(href)
    return article_links

def article_download_link(article_link):
    browser.get(article_link)
    WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button-cta")))

    soup = BeautifulSoup(browser.page_source, features='html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'https://docs-assets.developer.apple.com/published/' in href and '.zip' in href:
            return href
    return None

def start_download_task(q):
    while True:
        link = q.get()
        print('downloading: {}, remaining: {}'.format(link, q.unfinished_tasks))

        with urllib.request.urlopen(link) as f:
            contents = f.read()
            with open(path + os.path.basename(link), 'wb') as handle:
                handle.write(contents)
        q.task_done()

if __name__ == '__main__':
    path = 'Downloads/'
    if not os.path.exists(path):
        os.makedirs(path)

    queue = Queue(maxsize=0)
    links = article_links()
    print('found {} samples'.format(len(links)))
    
    browser = webdriver.Safari()
    for index, article_link in enumerate(links):
        for _ in range(4):
            download_link = article_download_link(article_link)
            if download_link:
                queue.put(download_link)
                break
    browser.quit()

    threads = 4
    for i in range(threads):
        worker = Thread(target=start_download_task, args=(queue,))
        worker.setDaemon(True)
        worker.start()
    
    queue.join()


    




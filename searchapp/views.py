from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import json




def get_realted(img_url,engine):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')



    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait=WebDriverWait(driver,10)

    def bing(img_url):
        driver.get(f'https://www.bing.com/images/searchbyimage?cbir=ssbi&imgurl={img_url}')
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, 'See related image detail.')]")))
        except:
            driver.save_screenshot('bing.png')
            return []

        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, 'See related image detail.')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link.split('&')[0]
                related_image_urls.append({'engine':'bing','url':url})
                if len(related_image_urls)==50:
                    break
            time.sleep(0.1)
        return related_image_urls

    def google_lense(img_url):
        driver.get(f'https://lens.google.com/uploadbyurl?url={img_url}')

        try:
           wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'wETe9b jFVN1')]")))
        except:
            driver.save_screenshot('lense.png')
            return []


        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'wETe9b jFVN1')]")
        
        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link
                related_image_urls.append({'engine':'google_lense','url':url})
                if len(related_image_urls)==50:
                    break
            # time.sleep(0.3)
        return related_image_urls

    def yandex(img_url):
        driver.get(f'https://yandex.com/images/search?rpt=imageview&url={img_url}')
        try:
            similar_btn = driver.find_element(By.XPATH,"//a[contains(@class, 'CbirNavigation-TabsItem CbirNavigation-TabsItem_name_similar-page')]")
            similar_btn.click()
            wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'serp-item__thumb justifier__thumb')]")))
        except:
            driver.save_screenshot('yandex.png')
            return []

        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'serp-item__thumb justifier__thumb')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link
                related_image_urls.append({'engine':'yandex','url':url})
                if len(related_image_urls)==50:
                    break
            # time.sleep(0.3)
        return related_image_urls



    def naver(img_url):
        driver.get(f'https://s.search.naver.com/p/sbi/search.naver?where=sbi&query=smartlens&orgPath={img_url}')
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, '이미지준비중')]")))
        except:
            driver.save_screenshot('naver.png')
            return []

        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, '이미지준비중')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link.split('&')[0]
                related_image_urls.append({'engine':'naver','url':url})
                if len(related_image_urls)==50:
                    break
            time.sleep(0.1)
        return related_image_urls

    if engine == 'bing':
       return bing(img_url)
    if engine == 'google_lense':
       return google_lense(img_url)
    if engine == 'yandex':
       return yandex(img_url)
    if engine == 'naver':
       return naver(img_url)

####################################################################Check Similarity
import boto3
import json
import concurrent.futures
lambda_client = boto3.client('lambda')
def main(img_url,url):
    payload = {
        'url1': img_url,
        'url2': url['url']
    }
    response = lambda_client.invoke(
        FunctionName='test',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    response_payload = json.loads(response['Payload'].read())
    print(response_payload)
    try:
        score = response_payload['similarity_score']
    except:
        score = 0
    url['score'] = score
    return url
def similarity_score(img_url, all_urls):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(main, img_url, url) for url in all_urls]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results
####################################################################################Search Engine
def search_engine(img_url, engines):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(get_realted, img_url, engine) for engine in engines]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
    return results
#####################################################################################################



@csrf_exempt
def search(request):
    if request.method == 'POST':
        img_url = request.POST.get('img_url')
        if img_url:
            all_urls = search_engine(img_url,['google_lense','bing','naver','yandex'])
            response = similarity_score(img_url,all_urls)
            # response = [{**url, 'score': 50} for url in all_urls]

            response_dict = {}
            for r in response:
                if r['score']>10:
                    if r['engine'] not in response_dict:
                        response_dict[r['engine']] = []
                    response_dict[r['engine']].append([r['url'],r['score']])

            return JsonResponse(response_dict,safe=False)
        else:
            return JsonResponse({'error': 'No image URL provided'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


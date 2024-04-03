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
import time
import json

def all(img_url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait=WebDriverWait(driver,10)

    def bing(img_url):
        driver.get(f'https://www.bing.com/images/searchbyimage?cbir=ssbi&imgurl={img_url}')
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, 'See related image detail.')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, 'See related image detail.')]")

        related_image_urls = []
        for image in related_images:
            if image.get_attribute('src').startswith('https://'):
                url = image.get_attribute('src').split('&')[0]
                related_image_urls.append(url)
                break
        return related_image_urls

    def google_lense(img_url):
        driver.get(f'https://lens.google.com/uploadbyurl?url={img_url}')
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'wETe9b jFVN1')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'wETe9b jFVN1')]")
        
        related_image_urls = []
        for image in related_images:
            if image.get_attribute('src').startswith('https://'):
                related_image_urls.append(image.get_attribute('src'))
                break
        return related_image_urls

    def yandex(img_url):
        driver.get(f'https://yandex.com/images/search?rpt=imageview&url={img_url}')
        similar_btn = driver.find_element(By.XPATH,"//a[contains(@class, 'CbirNavigation-TabsItem CbirNavigation-TabsItem_name_similar-page')]")
        similar_btn.click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'serp-item__thumb justifier__thumb')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'serp-item__thumb justifier__thumb')]")

        related_image_urls = []
        for image in related_images:
            if image.get_attribute('src').startswith('https://'):
                related_image_urls.append(image.get_attribute('src'))
                break
        return related_image_urls



    def naver(img_url):
        driver.get(f'https://s.search.naver.com/p/sbi/search.naver?where=sbi&query=smartlens&orgPath={img_url}')
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, '이미지준비중')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, '이미지준비중')]")

        related_image_urls = []
        for image in related_images:
            if image.get_attribute('src').startswith('https://'):
                url = image.get_attribute('src').split('&')[0]
                related_image_urls.append(url)
                break
        return related_image_urls

        
    return {
                'bing':bing(img_url),
                'google_lense':google_lense(img_url),
                'yandex':yandex(img_url),
                'naver':naver(img_url)
            }


@csrf_exempt
def search(request):
    if request.method == 'POST':
        img_url = request.POST.get('img_url')
        if img_url:
            response = all(img_url)
            return JsonResponse(response,safe=False)
        else:
            return JsonResponse({'error': 'No image URL provided'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


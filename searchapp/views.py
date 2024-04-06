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




def all(img_url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')



    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait=WebDriverWait(driver,30)

    def bing(img_url):
        driver.get(f'https://www.bing.com/images/searchbyimage?cbir=ssbi&imgurl={img_url}')
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, 'See related image detail.')]")))
        except:
            driver.save_screenshot('timeout_debug.png')
            raise

        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, 'See related image detail.')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link.split('&')[0]
                related_image_urls.append({'engine':'bing','url':url})
                if len(related_image_urls)==5:
                    break
            time.sleep(0.3)
        return related_image_urls

    def google_lense(img_url):
        driver.get(f'https://lens.google.com/uploadbyurl?url={img_url}')
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'wETe9b jFVN1')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'wETe9b jFVN1')]")
        
        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link
                related_image_urls.append({'engine':'google_lense','url':url})
                if len(related_image_urls)==5:
                    break
            time.sleep(0.3)
        return related_image_urls

    def yandex(img_url):
        driver.get(f'https://yandex.com/images/search?rpt=imageview&url={img_url}')
        similar_btn = driver.find_element(By.XPATH,"//a[contains(@class, 'CbirNavigation-TabsItem CbirNavigation-TabsItem_name_similar-page')]")
        similar_btn.click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'serp-item__thumb justifier__thumb')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@class, 'serp-item__thumb justifier__thumb')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link
                related_image_urls.append({'engine':'yandex','url':url})
                if len(related_image_urls)==5:
                    break
            time.sleep(0.3)
        return related_image_urls



    def naver(img_url):
        driver.get(f'https://s.search.naver.com/p/sbi/search.naver?where=sbi&query=smartlens&orgPath={img_url}')
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@alt, '이미지준비중')]")))
        related_images = driver.find_elements(By.XPATH,"//img[contains(@alt, '이미지준비중')]")

        related_image_urls = []
        for image in related_images:
            link = image.get_attribute('src')
            if link.startswith('https://'):
                url = link.split('&')[0]
                related_image_urls.append({'engine':'naver','url':url})
                if len(related_image_urls)==5:
                    break
            time.sleep(0.3)
        return related_image_urls

    all_urls = []
    # all_urls.extend(bing(img_url))
    all_urls.extend(google_lense(img_url))
    all_urls.extend(yandex(img_url))
    all_urls.extend(naver(img_url))
    return all_urls

###################################### MY
# import numpy as np
# import requests
# from skimage import io, img_as_float
# from skimage.metrics import structural_similarity as ssim
# from skimage.color import rgb2gray
# from skimage.transform import resize
# import concurrent.futures

# def main(img_url,url):
#     def download_image(url):
#         response = requests.get(url)
#         image = io.imread(response.content, plugin='imageio')
#         return img_as_float(image)
#     def compare_images(image1, image2):
#         image2_resized = resize(image2, image1.shape[:2], anti_aliasing=True)        
#         gray_image1 = rgb2gray(image1)
#         gray_image2 = rgb2gray(image2_resized)        
#         similarity_index, _ = ssim(gray_image1, gray_image2, full=True, data_range=1)
#         return similarity_index
#     url1 = img_url
#     url2 = url['url']
#     image1 = download_image(url1)
#     image2 = download_image(url2)
#     similarity = compare_images(image1, image2)
#     url['score'] = similarity * 100
#     return url

# def similarity_score(img_url, all_urls):
#     results = []
#     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#         futures = [executor.submit(main, img_url, url) for url in all_urls]
#         for future in concurrent.futures.as_completed(futures):
#             results.append(future.result())
#     return results

#############################################################SIR
# import numpy as np
# import requests
# from skimage import io, img_as_float
# from skimage.metrics import structural_similarity as ssim
# from skimage.color import rgb2gray
# from skimage.transform import resize
# from multiprocessing import Pool

# image_cache = {}

# def download_image(url):
#     if url in image_cache:
#         return image_cache[url]
#     response = requests.get(url)
#     image = io.imread(response.content, plugin='imageio')
#     image_cache[url] = img_as_float(image)
#     return image_cache[url]

# def compare_images(image_pair):
#     image1, image2 = image_pair
#     image2_resized = resize(image2, image1.shape[:2], anti_aliasing=True)
#     gray_image1 = rgb2gray(image1)
#     gray_image2 = rgb2gray(image2_resized)
#     similarity_index, _ = ssim(gray_image1, gray_image2, full=True, data_range=1)
#     return similarity_index

# def main(img_url, urls):
#     image1 = download_image(img_url)
#     image_pairs = [(image1, download_image(url['url'])) for url in urls]

#     with Pool() as pool:
#         similarities = pool.map(compare_images, image_pairs)

#     for url, similarity in zip(urls, similarities):
#         url['score'] = similarity * 100

#     return urls
#############################################################################

@csrf_exempt
def search(request):
    if request.method == 'POST':
        img_url = request.POST.get('img_url')
        if img_url:
            all_urls = all(img_url)
            # response = main(img_url,all_urls)
            response = [{**url, 'score': 50} for url in all_urls]

            response_dict = {}
            for r in response:
                if r['engine'] not in response_dict:
                    response_dict[r['engine']] = []
                response_dict[r['engine']].append([r['url'],r['score']])

            return JsonResponse(response_dict,safe=False)
        else:
            return JsonResponse({'error': 'No image URL provided'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


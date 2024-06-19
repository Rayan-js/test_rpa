import json,time,os,re, sys
import pandas as pd
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# <-------- // Ferramenta de debug // ------------->
path =r'C:\Program Files\Automacoes\0_MODULOS_PYTHON\perseu'
sys.path.insert(0,path)
from printColor import *
# <-------- // Ferramenta de debug // ------------->


# Carregar configuração
with open('config.json') as config_file:
    config = json.load(config_file)

search_phrase = config['search_phrase']
news_category = config['news_category']
months = config['months']
pCyan(months)
# Configurar o WebDriver (certifique-se de que o chromedriver está no PATH)
driver = webdriver.Chrome()

def open_site():
    driver.get("https://gothamist.com")
    

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".waimanalo-campaign.Campaign.CampaignType--popup.Campaign--css"))
    )
    popup = driver.find_element(By.CSS_SELECTOR, ".waimanalo-campaign.Campaign.CampaignType--popup.Campaign--css")
    popup.find_element(By.XPATH, '//*[@id="om-gk66zqvxcdypoosfxlyu-yesno"]/div/button').click()

    driver.maximize_window()
    pGreen('Site Aberto com sucesso!')
    time.sleep(1)

def search_news(phrase):
    driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div/div/main/header/div[1]/div[2]/div[2]/button').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(phrase)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    # search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".content")))
    pGreen("Pesquisa realizada!")


# def count_search_phrases(title, description):
#     search_phrases = ["technology", "innovation", "AI", "machine learning"]
#     count = 0
#     for phrase in search_phrases:
#         count += title.lower().count(phrase) + description.lower().count(phrase)
#     return count

# def contains_money(title, description):
#     money_terms = ["dollar", "USD", "money", "funding", "investment"]
#     combined_text = f"{title} {description}".lower()
#     return any(term in combined_text for term in money_terms)

def get_news_data(driver, months):
    pRed("Entrando em get_news_data!")
    news_data = []
    current_date = datetime.now()
    past_date = current_date - timedelta(days=30 * months)

    # time.sleep(10)  # Aguarda para garantir que a página esteja carregada
    WebDriverWait(driver, 25).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="resultList"]/div[2]/div/div')))
    time.sleep(1)
    articles = driver.find_elements(By.XPATH, '//*[@id="resultList"]/div[2]/div/div')

    
    for article in articles:

        try:
            
            title_element = article.find_element(By.CLASS_NAME, 'h2')
            # date_element = article.find_element(By.XPATH, ".views-field-created")
            description_element = article.find_element(By.CLASS_NAME, 'desc')

            imgs = article.find_elements(By.TAG_NAME,'img')

            for img in imgs:
                
                image_url = img.get_attribute('src')
                # pYellow(image_url)
                break  # Pegue apenas o primeiro link de imagem

            title = title_element.text.strip() if title_element.text.strip() else description_element.text.strip()
            pCyan(f"Title: {title}")

            if image_url:
                image_filename = download_image(image_url, title)  

            # date_str = date_element.text
            # date = datetime.strptime(date_str, "%b %d, %Y")
            description = description_element.text if description_element else ""


            # pYellow(f"Date: {date}")
            pYellow(f"Description: {description}")
            pYellow(f"Image URL: {image_url}")

            # if date >= past_date:
            news_data.append({
                "title": title,
                # "date": date.strftime("%Y-%m-%d"),
                "description": description,
                "image_filename": image_filename,
                "search_phrase_count": count_search_phrases(title, description),
                "contains_money": contains_money(title, description)
            })
        except Exception as e:
            print(f"Erro ao processar o artigo: {e}")
    return news_data

def sanitize_filename(title):
    # Remover caracteres inválidos para nomes de arquivo
    sanitized_title = re.sub(r'[\\/:"*?<>|]', '', title)
    # Pegar as primeiras três palavras do título
    words = sanitized_title.split()[:3]
    # Unir as palavras com underscore e adicionar a extensão .png
    sanitized_title = '_'.join(words) + '.png'
    return sanitized_title

def download_image(url, title):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Crie uma pasta chamada 'imgs' se ela não existir
        if not os.path.exists('imgs'):
            os.makedirs('imgs')

        # Crie um nome de arquivo baseado no título e sanitize o nome
        filename = sanitize_filename(title)
        filepath = os.path.join('imgs', filename)
        pRed(filepath)
        with open(filepath, 'wb') as file:
            file.write(response.content)
        return filepath
    except Exception as e:
        print(f"Erro ao baixar a imagem: {e}")
        return ""


def count_search_phrases(title, description):
    tit = title.lower()
    desc = description.lower()
    sear = search_phrase.lower()
    phrase_count = tit.count(sear) + desc.count(sear)
    return phrase_count

def contains_money(title, description):
    money_pattern = r'(\$\d+(,\d{3})*(\.\d{2})?)|(\d+ dollars)|(\d+ dollar)|(\d+ M)|(\d+ B)|(\d+ USD)'
    return bool(re.search(money_pattern, title + " " + description))

def save_to_excel(news_data):
    if news_data:
        df = pd.DataFrame(news_data)
        df.to_excel('news_data.xlsx', index=False)
    else:
        print("Nenhum dado de notícia foi encontrado.")

def main():
    open_site()
    search_news(search_phrase)
    news_data = get_news_data(driver=driver, months=months)
    save_to_excel(news_data)
    driver.quit()

if __name__ == "__main__":
    main()

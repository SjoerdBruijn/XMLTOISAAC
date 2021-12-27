from Bio import Entrez
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
## settings to change
safemode        = 1 #immidiately submit or not; recommended to not, leave at 1
Entrez.email    ='s.m.bruijn@gmail.com' # your email is used for pubmed to contact you if you use their api to heavily
query           ='bruijn s.m.' # search query in pubmed. Note that no comma is required
select_year     = 2021 #publications from which year should be fed to isaac

## get data from pubmed
handle = Entrez.esearch(db='pubmed', sort='year',retmax='200', retmode='xml', term=query)
results = Entrez.read(handle)
handle2 = Entrez.efetch(db='pubmed',retmode='xml', id=results['IdList'])
results2 = Entrez.read(handle2)

## parse data from pubmed into our 'papers' dictionary (leftover from XML version)
papers          = dict()
papers['paper'] = dict()
i_paper         = 0
for article in results2['PubmedArticle']:
    # print(article['MedlineCitation']['Article']['ArticleTitle'])
    papers['paper'][0, i_paper] = dict()
    papers['paper'][0, i_paper]['authors']  = dict()
    papers['paper'][0, i_paper]['title']    = article['MedlineCitation']['Article']['ArticleTitle']
    papers['paper'][0, i_paper]['journal']  = article['MedlineCitation']['Article']['Journal']['Title']
    papers['paper'][0, i_paper]['issue']    = article['MedlineCitation']['Article']['Journal']['JournalIssue']['Volume']
    try:
        papers['paper'][0, i_paper]['year']     = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
    except:
        papers['paper'][0, i_paper]['year'] =['']
    for locationId in article['MedlineCitation']['Article']['ELocationID']:
        if locationId.attributes['EIdType']=='doi':
            papers['paper'][0, i_paper]['url']      = locationId
    try:
        pages = article['MedlineCitation']['Article']['Pagination']['MedlinePgn']
        if len(pages.split('-')) < 2:
                pages = pages + '- '
        papers['paper'][0, i_paper]['first_page'] = pages.split('-')[0]
        papers['paper'][0, i_paper]['last_page'] = pages.split('-')[1]
    except:
        papers['paper'][0, i_paper]['first_page'] = ['']
        papers['paper'][0, i_paper]['last_page'] = ['']

    recordauthors = article['MedlineCitation']['Article']['AuthorList']
    i_author=0
    for author in recordauthors:
        # print(author['LastName'])
        papers['paper'][0, i_paper]['authors'][0, i_author] = dict()
        papers['paper'][0, i_paper]['authors'][0, i_author]['surname']  = author['LastName']
        papers['paper'][0, i_paper]['authors'][0, i_author]['initials'] = author['Initials']
        i_author=i_author+1
    i_paper=i_paper+1
## get the papers from only the selected years


## shooting the papers to NWO
username    =input("Enter your username:")
password    =input("Enter your password:")
project_id  =input("Enter your project ID")#016.Vidi.178.014

driver = webdriver.Chrome()

## navigate to NWO ISAAC, login
driver.get("https://www.isaac.nwo.nl/nl/home")

driver.find_element(By.ID,"_58_login").send_keys(username)
password_field  = driver.find_element(By.ID,"_58_password")
password_field.send_keys(password)
password_field.submit()


# go to the projects page
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Projects')]")))
driver.find_element_by_xpath("//*[contains(text(), 'Projects')]").click()

## go into the project you want to add publications to
project_id="//*[contains(text(),'"+ project_id+"')]"
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, project_id)))
driver.find_element_by_xpath(project_id).click()
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Product_1")))
driver.find_element(By.ID,"Product_1").click()

# start adding. This is where a loop should start also.
for i_paper in range(len(papers['paper'])):
# i_paper=1
    if int(papers['paper'][0,i_paper]['year'])==select_year:
        print(papers['paper'][0,i_paper]['title'])
        if i_paper==0:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Toevoegen_1")))
        else:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Verwijderen_1")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Toevoegen_1")))
        driver.find_element(By.ID,"Toevoegen_1").click()

        # scientific article
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "WetenschapelijkArtikel_1")))
        driver.find_element(By.ID,"WetenschapelijkArtikel_1").click()

        #title
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "WetenschappelijkArtikel-Titel_1")))
        driver.find_element(By.ID,"WetenschappelijkArtikel-Titel_1").send_keys(papers['paper'][0,i_paper]['title'])



        #refereed

        #journal
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "WetenschappelijkArtikel-TitelTijdschrift_1")))
        driver.find_element(By.ID,"WetenschappelijkArtikel-TitelTijdschrift_1").send_keys(papers['paper'][0,i_paper]['journal'])

        #year
        driver.find_element(By.ID,"WetenschappelijkArtikel-UitgaveJaar_1").send_keys(papers['paper'][0,i_paper]['year'])

        #issue
        driver.find_element(By.ID,"WetenschappelijkArtikel-Nummer_1").send_keys(papers['paper'][0,i_paper]['issue'])

        #start page
        driver.find_element(By.ID,"WetenschappelijkArtikel-Beginpagina_1").send_keys(papers['paper'][0,i_paper]['first_page'])

        #end page
        driver.find_element(By.ID,"WetenschappelijkArtikel-Eindpagina_1").send_keys(papers['paper'][0,i_paper]['last_page'])

        #type

        #doi
        urlnotinserted=1
        while urlnotinserted:
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "WetenschappelijkArtikel-OpenAccesUrl_1")))
                driver.find_element(By.ID,"WetenschappelijkArtikel-OpenAccesUrl_1").send_keys(papers['paper'][0,i_paper]['url'])
                urlnotinserted = 0
            except:
                urlnotinserted = 1
                print('failed submitting url, trying again')

        # add authors (should be loop)
        for i_author in range(len(papers['paper'][0, i_paper]['authors'])):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Toevoegen_1")))
            driver.find_element(By.ID,"Toevoegen_1").click()
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ProductBetrokkenheid-Voorletters_1")))
            driver.find_element(By.ID,"ProductBetrokkenheid-Voorletters_1").send_keys(
                papers['paper'][0, i_paper]['authors'][0, i_author]['initials'])
            driver.find_element(By.ID,"ProductBetrokkenheid-Achternaam_1").send_keys(
                papers['paper'][0, i_paper]['authors'][0, i_author]['surname'])
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Verder_2")))
            driver.find_element(By.ID,"Verder_2").click()

        # submit record
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "Opslaan_concept_en_sluiten_1")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Opslaan_concept_en_sluiten_1")))
        driver.find_element(By.ID,"Opslaan_concept_en_sluiten_1").click()
        # driver.find_element(By.ID,"Opslaan_concept_en_sluiten_1").click()

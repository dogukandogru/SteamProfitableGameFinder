from selenium import webdriver
from bs4 import BeautifulSoup
import time
import math
from datetime import datetime

start=datetime.now()
class gameInfo:
    name = ""
    appId = ""
    price = ""
    cardPrices = ""
    minPrice = ""
    avgPrice = ""
    maxPrice = ""
    def __init__(self,name,appId,price):
        self.name = name
        self.appId = appId
        self.price = price

    
    
loginLink = "https://store.steampowered.com/login/"
gamesLink = "https://store.steampowered.com/search/?sort_by=Price_ASC&category1=998&category2=29&specials=1&ignore_preferences=1&page="
seenCardLink = "https://steamcommunity.com/market/search?category_753_Game%5B%5D=tag_app_1069740&category_753_cardborder%5B%5D=tag_cardborder_0&category_753_item_class%5B%5D=tag_item_class_2&appid=753"




browser = webdriver.Chrome()
browser.get(loginLink)


print("Lütfen Steam'e Giriş Yapınız. (Steam'e giriş yapmanızın nedeni, steam pazar fiyatları araştırılır iken kart fiyatlarının TL cinsinden gözükmesi için steam cüzdanı oluşturulmuş bir hesap gerekmesidir. Aksi takdirde fiyatlar USD cinsinden gözükecek ve USD->TL çevirmesi esnasında hatalar olacaktır. Bu hatalar sonucu da istenen kar düzgün hesaplanamayacaktır.")
print("Steam'e giriş yaptıktan sonra lütfen konsola \"devam\" yazınız.")


cont = ""
while True:
    cont = input()
    if(cont == "devam"):
        break
    else:
        time.sleep(1)


print("\nKaç sayfa oyun taramak istersiniz ? : ")
gameInfos = set()
pageCount = int(input())
approximateNumOfGames = pageCount*25

print("\nTaratılacak sayfa sayısı : " + str(pageCount) + " Tahmini taratılacak oyun sayısı : " + str(approximateNumOfGames))
for num in range(1,pageCount+1):
    print("Çekilen oyun sayısı : " + str(len(gameInfos)))
    browser.get(gamesLink+str(num))
    html_source = browser.page_source
    soup = BeautifulSoup(html_source,'html.parser')
    nameDivs = soup.find_all("span",attrs={"class":"title"})
    appIdDivs = soup.find_all("a")
    priceDivs = soup.find_all("div",attrs={"class":"col search_price discounted responsive_secondrow"})
    
    
    appIds = list()
    
    for appIdWithNone in appIdDivs:
        appId = appIdWithNone.get("data-ds-appid")
        if str(appId) != "None":
            appIds.append(str(appId))
    
    
    length = len(nameDivs)
    for i in range(0,length):
        price = priceDivs[i]
        priceText = price.getText()
        priceText = priceText[priceText.index("TL")+2:priceText.rfind("TL")-1]
        name = nameDivs[i]
        game = gameInfo(name.getText(),appIds[i],priceText)
        
        if "," not in game.appId:
            gameInfos.add(game)



print("\n" + str(len(gameInfos)) + " adet oyun çekildi.\nOyunların steam pazar taramaları başlıyor..\n")

scannedGameCount = 0
baseURLFirstPart = "https://steamcommunity.com/market/search?category_753_Game%5B%5D=tag_app_" 
baseURLSecondPart = "&category_753_cardborder%5B%5D=tag_cardborder_0&category_753_item_class%5B%5D=tag_item_class_2&appid=753"
for game in gameInfos:
    print(str(scannedGameCount)  + "/" + str(len(gameInfos)) + " oyun tarandı.")
    try:
        url = baseURLFirstPart + str(game.appId) + baseURLSecondPart
        browser.get(url)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source,'html.parser')
        cardPricesWithSpan = soup.find_all("span",attrs={"class":"normal_price"})
        cardPrices = list()
        for card in cardPricesWithSpan:
            if str(card.get("data-price")) != "None":
                cardPrices.append(str(card.get("data-price")))
        
        pageText = browser.find_element_by_xpath("//*[@id=\"searchResults_links\"]").text
        if pageText == "1 2":    
            #pageTwo = browser.find_element_by_xpath("//*[@id=\"searchResults_links\"]/span[2]").click()
            browser.get(url+"#p2_popular_desc")
            time.sleep(2)
            html_source = browser.page_source
            soup = BeautifulSoup(html_source,'html.parser')
            cardPricesWithSpan = soup.find_all("span",attrs={"class":"normal_price"})
            for card in cardPricesWithSpan:
                if str(card.get("data-price")) != "None":
                    cardPrices.append(str(card.get("data-price")))
        game.cardPrices = cardPrices          
    
    except:
        game.cardPrices = list()
        continue
    scannedGameCount += 1

print(str(scannedGameCount)  + "/" + str(len(gameInfos)) + " oyun tarandı.")   
browser.close()


print("\nOyunların minimum ortalama ve maximum getireceği kârlar hesaplanıyor..")
for game in gameInfos:
    cardPrices = game.cardPrices
    for i in range(0, len(cardPrices)): 
        cardPrices[i] = int(cardPrices[i]) 
    
    if len(cardPrices) > 0 :
        cardCount = math.ceil((len(cardPrices)/2))
        minPrice = min(cardPrices)*cardCount
        avgPrice = (sum(cardPrices)/len(cardPrices))*cardCount
        maxPrice = max(cardPrices)*cardCount
        game.minPrice = minPrice/100
        game.avgPrice = avgPrice/100
        game.maxPrice = maxPrice/100
        
    else:
        game.minPrice = 0
        game.avgPrice = 0
        game.maxPrice = 0
    
print("\nOyunların bilgileri ve getireceği kârlar excel dosyasına yazılıyor..")

from xlwt import Workbook 
wb = Workbook() 

minSheet = wb.add_sheet("MinimumdanKarGetirenler")
minSheet.write(0,0,"Oyun Adı")
minSheet.write(0,1,"Fiyat")
minSheet.write(0,2,"Min")
minSheet.write(0,3,"Avg")
minSheet.write(0,4,"Max")
minSheet.write(0,5,"AppId")

    

#Minimumdan Kar Getirenler
sayi = 1
for game in gameInfos:
    gamePrice = game.price
    gamePrice = gamePrice.replace(",",".")
    if game.minPrice > float(gamePrice):
        minSheet.write(sayi,0,game.name)
        minSheet.write(sayi,1,game.price)
        minSheet.write(sayi,2,str(game.minPrice))
        minSheet.write(sayi,3,str(game.avgPrice)[0:str(game.avgPrice).index(".")+2])
        minSheet.write(sayi,4,str(game.maxPrice))
        minSheet.write(sayi,5,str(game.appId))
        sayi += 1


sayi = 1
avgSheet = wb.add_sheet("AveragedanKarGetirenler")
avgSheet.write(0,0,"Oyun Adı")
avgSheet.write(0,1,"Fiyat")
avgSheet.write(0,2,"Min")
avgSheet.write(0,3,"Avg")
avgSheet.write(0,4,"Max")
avgSheet.write(0,5,"AppId")        
        

#Averagedan Kar Getirenler
for game in gameInfos:
    gamePrice = game.price
    gamePrice = gamePrice.replace(",",".")
    if game.avgPrice > float(gamePrice):
        avgSheet.write(sayi,0,game.name)
        avgSheet.write(sayi,1,game.price)
        avgSheet.write(sayi,2,str(game.minPrice))
        avgSheet.write(sayi,3,str(game.avgPrice)[0:str(game.avgPrice).index(".")+2])
        avgSheet.write(sayi,4,str(game.maxPrice))
        avgSheet.write(sayi,5,str(game.appId))
        sayi += 1
        
        
sayi = 1
maxSheet = wb.add_sheet("MaximumdanKarGetirenler")
maxSheet.write(0,0,"Oyun Adı")
maxSheet.write(0,1,"Fiyat")
maxSheet.write(0,2,"Min")
maxSheet.write(0,3,"Avg")
maxSheet.write(0,4,"Max")
maxSheet.write(0,5,"AppId")        

#Maximumdan Kar Getirenler
for game in gameInfos:
    gamePrice = game.price
    gamePrice = gamePrice.replace(",",".")
    if game.maxPrice > float(gamePrice):
       maxSheet.write(sayi,0,game.name)
       maxSheet.write(sayi,1,game.price)
       maxSheet.write(sayi,2,str(game.minPrice))
       maxSheet.write(sayi,3,str(game.avgPrice)[0:str(game.avgPrice).index(".")+2])
       maxSheet.write(sayi,4,str(game.maxPrice))
       maxSheet.write(sayi,5,str(game.appId))
       sayi += 1


wb.save('KarlıOyunlar.xls')

print("\nToplam " + str(len(gameInfos)) + " adet oyun tarandı. Taranan tüm oyunların bilgileri ve getireceği kârlar \"KarlıOyunlar.xls\" belgesine kaydedildi. Lütfen kontrol ediniz.")
print("\nToplam Geçen Süre : "  + str((datetime.now()-start)))














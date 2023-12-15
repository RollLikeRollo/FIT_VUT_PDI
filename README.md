Podrobnosti k zadání jsou na odkazovaných stránkách. Na platformě Apache Flink vytvořte aplikaci, která se připojí na "Polohy vozidel hromadné dopravy" na webu Otevřená data Statutární město Brno, který je publikován pomocí ArcGIS Stream Services, a bude vykonávat následující činnosti pro aktivní dopravní prostředky (nepravdivé isinactive)

průběžně vypisovat vozidla mířící na sever (s max. odchylkou ± 45 stupnů)
vypisovat seznam vlaků s ID (či názvem) jejich poslední hlášené zastávky a časem poslední aktualizace pro každý vlak hlášený od startu aplikace
vypisovat seznam nejvýše 5 zpožděných vozů seřazených sestupně podle jejich posledně hlášeného zpoždění od startu aplikace
vypisovat seznam nejvýše 5 zpožděných vozů hlášených během posledních 3 minut a seřazených setupně podle času jejich poslední aktualizace
vypisovat průměrné zpoždění spočítané ze všech vozů (zpožděných i nezpožděných) hlášených během posledních 3 minut
vypisovat průměrnou dobu mezi jednotlivými hlášeními se započítáním posledních 10 hlášení



https://rychly-edu.gitlab.io/dist-apps/project/#zpracovani-proudu-dat-arcgis-stream-services-z-dopravy-idsjmk-pomoci-apache-sparkflink

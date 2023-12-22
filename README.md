# README.md

## Projekt PDI, zima 2023, Jan Zbořil, xzbori20

---

Detailní informace jsou v TESTING.md a INSTALL.md

Pro velikost testovacích dat nejsou přibalená v archivu, ale jsou umístěná na `https://nextcloud.fit.vutbr.cz/s/krjfs4c8sRiJcoH`

## Zdroje

- https://nightlies.apache.org/flink/flink-docs-master/api/python/reference/
- https://nightlies.apache.org/flink/flink-docs-master/docs/dev/python/overview/

#### Licence pro oba zdroje:

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.

## Zadání

Podrobnosti k zadání jsou na odkazovaných stránkách. Na platformě Apache Flink vytvořte aplikaci, která se připojí na "Polohy vozidel hromadné dopravy" na webu Otevřená data Statutární město Brno, který je publikován pomocí ArcGIS Stream Services, a bude vykonávat následující činnosti pro aktivní dopravní prostředky (nepravdivé isinactive)

- 1 průběžně vypisovat vozidla mířící na sever (s max. odchylkou ± 45 stupnů)
- 2 vypisovat seznam vlaků s ID (či názvem) jejich poslední hlášené zastávky a časem poslední aktualizace pro každý vlak hlášený od startu aplikace
- 3 vypisovat seznam nejvýše 5 zpožděných vozů seřazených sestupně podle jejich posledně hlášeného zpoždění od startu aplikace
- 4 vypisovat seznam nejvýše 5 zpožděných vozů hlášených během posledních 3 minut a seřazených sestupně podle času jejich poslední aktualizace
- 5 vypisovat průměrné zpoždění spočítané ze všech vozů (zpožděných i nezpožděných) hlášených během posledních 3 minut
- 6 vypisovat průměrnou dobu mezi jednotlivými hlášeními se započítáním posledních 10 hlášení

https://rychly-edu.gitlab.io/dist-apps/project/#zpracovani-proudu-dat-arcgis-stream-services-z-dopravy-idsjmk-pomoci-apache-sparkflink

Pro všechny varianty navíc platí následující požadavky:

Pro vypracování můžete použít libovolný programovací jazyk podporovaný zvolenou platformou a libovolnou knihovnu.
Všechny použité zdroje budou uvedeny v dokumentaci projektu v souboru README.md vč. jejich licencí.
Aplikace bude vypisovat odpovědi na uvedené dotazy, stačí textově (CLI/TUI), tzn. grafické uživatelské rozhraní není potřeba.
Můžete si zvolit, zda se budou vyhodnocovat všechny dotazy zárověň, či se nejprve zvolí jeden z nich (před/při spuštění aplikace).
Pokud to platforma dovolí, řešení bude spustitelné na jednom počítači (v aplikaci zabudovaný Spark/Flink) v systému GNU/Linux i na případném clusteru (Hadoop/Spark/Flink).
Popis přímého spuštění a popis nasazení na clusteru bude součástí dokumentace v souboru INSTALL.md.
Součástí řešení bude test (či testy) ověřující funkčnost nad testovacími daty, které budou součástí odevzdávaného řešení (offline data, např. záznam dat z proudu do souboru).
Popis spuětění testů a předpokládaných výsledků bude součástí dokumentace v souboru TESTING.md.
Odevzdává se archiv (ZIP či TAR+GZip) s repositářem projektu (bez adresáře .git).

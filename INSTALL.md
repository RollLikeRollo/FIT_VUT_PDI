# INSTALL.md

## Projekt PDI, zima 2023, Jan Zbořil, xzbori20

---

```
FIT_VUT_PDI_projekt/data -i /home/jzboril/Documents/VUT/mit/2mit_zimni_s/pdi/FIT_VUT_PDI_projekt/data -o ~/pyflinkdataout -a 1 -h
usage: pdi.py [-h] [-i INPUT] [-o OUTPUT] [-d D] -a {1,2,3,4,5,6}

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file to process.
  -o OUTPUT, --output OUTPUT
                        Output directory.
  -d D                  Directory to save incoming stream data to.
  -a {1,2,3,4,5,6}, --assignment {1,2,3,4,5,6}
                        Assignment to run. 1 - průběžně vypisovat vozidla mířící na sever (s max. odchylkou ± 45 stupnů) 2 - vypisovat seznam vlaků s ID
                        (či názvem) jejich poslední hlášené zastávky a časem poslední aktualizace pro každý vlak hlášený od startu aplikace 3 -
                        vypisovat seznam nejvýše 5 zpožděných vozů seřazených sestupně podle jejich posledně hlášeného zpoždění od startu aplikace 4 -
                        vypisovat seznam nejvýše 5 zpožděných vozů hlášených během posledních 3 minut a seřazených setupně podle času jejich poslední
                        aktualizace 5 - vypisovat průměrné zpoždění spočítané ze všech vozů (zpožděných i nezpožděných) hlášených během posledních 3
                        minut 6 - vypisovat průměrnou dobu mezi jednotlivými hlášeními se započítáním posledních 10 hlášení Body 2 - 6 - vypisuje do
                        souboru, ktery se neustale prepisuje
```

Aplikace spouští každou z úloh zvlášť, výběr úlohy je specifikován při spuštění programu pomocí přepínače `-a`.

## Požadavky

- `python 3.10` (programováno a testováno s verzí `3.10.13`)
- python závislosti:

  - `apache-flink`
  - `websockets`
  - možné nainstalovat pomocí `pip install -r requirements.txt` nebo `pip install apache-flink websockets`

  - doporučeno instalovat ve virtuálním prostředí

## Lokální spouštění

Jelikož `pyflink` nepodporuje načítání streamu pomocí `websockets` skrz něž je dostupný datový stream z `wss://gis.brno.cz/geoevent/ws/services/ODAE_public_transit_stream/StreamServer/subscribe?outSR=4326`, je nutné data streamu stahovat na lokální stroj. Pro lokální spouštění existují dva způsoby:

### 1. S automatickým stahováním streamu

`python3 pdi.py -d <adresář pro ukládání streamu/z něhož bude program načítat stream>  -o <výstupní adresář> -a <číslo úlohy> -s`
např.:
`python3 pdi.py -d /home/user/FIT_VUT_PDI_projekt/datadir  -o /home/user/FIT_VUT_PDI_projekt/pyflinkdataout -a 1 -s`

### 2. S manuálním stahováním streamu

Nejprve je nutné sream ručně stahovat. Je možné použít `download.py`

`python3 download.py -p <adresář pro ukládání streamu>`  
např.:
`python3 download.py -p /home/user/FIT_VUT_PDI_projekt/datadir`

poté je možné spustit samotné zpracování dat:

`python3 pdi.py -d <adresář pro ukládání streamu/z něhož bude program načítat stream>  -o <výstupní adresář> -a <číslo úlohy>`
např.:
`python3 pdi.py -d /home/user/FIT_VUT_PDI_projekt/datadir  -o /home/user/FIT_VUT_PDI_projekt/pyflinkdataout -a 1`

## Výstupy úloh

Všechny úlohy kromě úlohy č. 3 produkují svůj výsledek (kontinuální výpis nebo výpis nějakého seznamu) jak na standardní výstup, tak také do souborů v adresáří specifikovaném přepínačem `-o`.

Úloha č. 2 je specifická. Protože výsledný seznam vlaků je příliš dlouhý a velikost výstupních souborů by velmi ryhcle rostla, je výsledný seznam ukládán do jediného souboru, který je při každé aktualizaci výsledného streamu přepsán a existuje v něm tedy pouze nejnovější verze výstupu. Výstupní adresář je opět specifikován přepínačem `-o`. Kromě toho je seznam vypisován na standardní výstup.

## Spouštění na clusteru

Pro spouštění úloh na clusteru je nejprve nutné stáhnout prostředí Flink z oficíálního webu Apache:
`https://www.apache.org/dyn/closer.lua/flink/flink-1.18.0/flink-1.18.0-bin-scala_2.12.tgz`  
Po stažení archiv rozbalíme a přejdeme do rozbalené složky.
Ve složce je vhodné vytvořit virtuální prostředí `python3 -m venv venv`, a aktivovat jej `source venv/bin/activate`. V aktivovaném prostředí (nebo globálně) je třeba nainstalovat závislosti `apache-flink websockets`.

Nejprve spustíme cluster v adresáři s rozbaleným archivem:
`./bin/start-cluster.sh`  
Funkčnost clusteru ověříme na `http://localhost:8081/`, kde se nachází webové prostředí `Flink`. Zde uvidíme námi spuštěné úlohy a jejich výpis na standardní výstup.

Úlohy na clusteru nelze spuštět s automatickým stahováním streamu. Stahování je nutné začít ručně před spuštěním úlohy na clusteru.
Pro stažené streamu je možné použít download.py

`python3 download.py -p <adresář pro ukládání streamu>`  
např.: `python3 download.py -p /home/user/FIT_VUT_PDI_projekt/datadir`

poté je možné spustit samotné zpracování dat na clusteru:  
`./bin/flink run --python <cesta k programu (pdi.py)> -d <adreář se streamem> -o <adresář pro výstup> pyflinkdataout -a <číslo úlohy>`  
např.:
`./bin/flink run --python /home/user/FIT_VUT_PDI_projekt/pdi.py -d /home/user/FIT_VUT_PDI_projekt/data -o /home/user/FIT_VUT_PDI_projekt/pyflinkdataout -a 1`

V průběhu výpočtu je ve webovém rozhraní k vidění úloha, její detaily, logy, výstup atd.

Cluster je možné vypnout pomocí `./bin/stop-cluster.sh`

###

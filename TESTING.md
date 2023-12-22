# TESTING.md

## Projekt PDI, zima 2023, Jan Zbořil, xzbori20

Testy obsahují zkoušení, zda data zobrazená z výstupu Flinku jsou zahrnutá ve vstupních testovacích originálních datech a zda výsledky neobsahují žádná nesmyslná data.

Spouští se všechny testy najednou jedním spuštěním `tests/test.py`. Jelikož se spouští samostatný FLink výpočet pro každou z úloh, tak se doba trvání testu pohybuje v rozmezí jednotek minut.

Pro velikost testovacích dat nejsou přibalená v archivu, ale jsou umístěná na `https://nextcloud.fit.vutbr.cz/s/krjfs4c8sRiJcoH`

Testovací data byla nasbírána 21. 12. 2023 od 19:00 do 19:05, a nachází se v adresáři `data_testing_5min` ve webovém úložišti výše.

Předpřipravené spuštění testů:  
`python3 tests/test.py data_testing_5min pdi.py`

`Usage: python3 test.py <path_to_testing_data> <path_to_pdi_py>`

Předpokládáný výstup:

```
python3 tests/test.py data_testing_5min pdi.py


['tests/test.py', 'data_testing_5min', 'pdi.py']
Running tests with data from data_testing_5min, using pdi.py as pdi.py

Running PDI script Assignment 5
.
Running PDI script Assignment 4
...
Running PDI script  Assignment 1
......
Running PDI script Assignment 6
.
Running PDI script Assignment 3
.
Running PDI script Assignment 2
...
----------------------------------------------------------------------
Ran 15 tests in 172.039s

OK

```

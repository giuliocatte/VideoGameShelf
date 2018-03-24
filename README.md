# VideoGameShelf
WIP

## Requirements

python 3.6

* igdb_api_python (https://github.com/igdb/igdb_api_python)
* se si vuole la cli, fire
* se si vuole steam, steam (https://pypi.python.org/pypi/steam)

## SetUp
Mettere in un file secrets.py le seguenti costanti
* IGDB_KEY: la chiave di accesso per le API di igdb (https://api.igdb.com/)
* STEAM_KEY: la chiave di accesso per le API di steam (https://steamcommunity.com/dev/apikey)
* STEAM_PLAYER_ID: l'id numerico del giocatore di steam (in chiaro negli url del client)

## Usage
Mettere la working directory nella root del repo.
Per il primo deploy del db, eseguire
```
python3 vgs.py deploy-db
```
Per scaricare la lista dei giochi posseduti da un servizio (record "owned"), usare
```
python3 vgs.py download-list-from-service {servicename}
```
Per scaricare le anagrafiche per tutti i giochi owned non ancora caricati
 da igdb, utilizzare
```
python3 vgs.py download-masterdata-from-db
```
Una volta scaricate le anagrafiche non sempre il software riuscirà ad avere
 un match completo, e talvolta salverà dei risultati in una tabella di staging. Per
 associare manualmente i record "owned" mancanti alle anagrafiche, usare
```
python3 vgs.py process-staging
```
Questo metodo processa un singolo nome trovato sulla tabella di staging
 (a cui potenzialmente vengono abbinati più record owned).

## Features

* Download delle liste di giochi posseduti da:
     * Steam
     * GOG (TODO)
     * BattleNet (TODO)
     * Twitch (TODO)
     * Humble (TODO)
     * Origin (TODO)
     * Uplay (TODO)
* Integrazione con le anagrafiche da igdb.com (match basato su steam id o nome)
* Funzionalità interattiva di correzione dei match
* Funzionalità di aggiunta di giochi extra-piattaforma (TODO)
* Aggiunta di attributi personali, quali rating, livello di completamento, tags (TODO)

## Wishlist

* Identificazione dei giochi installati sul sistema corrente
* Lancio dei giochi direttamente da questa applicazione
* Salvataggio in cloud
* App mobile
* Integrare altri servizi di database

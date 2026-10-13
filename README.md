# repo-pulse

Dashboard privata del traffico dei repository di **simoz**, con storico JSON e raccolta giornaliera via GitHub Actions. Python standard library + GitHub CLI, nessun servizio analytics esterno.

Questo repository pubblico contiene solo il codice. I dati raccolti vengono salvati nel repository privato `simoz/repo-pulse-data`, quindi qui non compaiono mai.

## Visualizzazione

Scarica `index.html` dal repository privato dei dati e aprilo nel browser: include i dati e funziona offline.

## Avvio locale

```sh
gh auth login
DATA_DIR=../repo-pulse-data python3 collect.py
open ../repo-pulse-data/index.html
python3 -m unittest
```

## Automazione

Configura il secret Actions `TRAFFIC_TOKEN` con un fine-grained PAT del proprietario `simoz`, accesso ai repository desiderati, permesso **Administration: read** (Metadata read è implicito) e **Contents: read and write** su `repo-pulse-data`. Se scegli solo alcuni repository, la copertura sarà limitata a quelli visibili al token. Il token della CLI locale non viene copiato automaticamente nei secrets.

La Action gira ogni giorno alle 06:23 UTC e si può avviare manualmente. Il PAT legge il traffico e salva i risultati in `repo-pulse-data`. I log della Action sono pubblici e mostrano soltanto quanti repository sono stati letti e quanti errori ci sono stati, senza nomi né dettagli. Controlla la scadenza del PAT. GitHub può disattivare workflow pianificati dopo lunghi periodi di inattività in repository pubblici.

## Semantica dei dati

- Vengono raccolti i repository posseduti dall'account, inclusi privati, fork e archiviati visibili al token.
- GitHub fornisce visite e cloni degli ultimi 14 giorni; lo storico più vecchio è disponibile solo dopo aver iniziato la raccolta.
- Le osservazioni giornaliere sono aggiornate per timestamp, mai sommate a quelle già salvate.
- Gli unici di 14 giorni provengono direttamente dalle API: non sono la somma degli unici giornalieri e non si sommano tra repository.
- Oggi è parziale. Date assenti restano sconosciute; una raccolta fallita conserva lo storico e viene segnalata, senza presentare dati vecchi come attuali.
- `data/traffic.json` conserva tutto lo storico; la dashboard confronta la finestra corrente di 14 giorni.
- Repository eliminati o non più visibili restano nello storico ma sono esclusi dalla vista corrente.

API: https://docs.github.com/en/rest/metrics/traffic

# gaitAnalysis
## Gait Analysis at UNIMORE

####__gait_extract.ipynb__
Permette di estrarre i dati e le labels come numpy array e di salvarli in un unica cartella con per nomi indici crescenti. Le labels sono salvate come one-hot encoding. Le variabili in __MAIUSCOLO__ sono parametri che potete cambiare.
####__c3d.py__
La libreria python c3d(download con pip) ha un errore all'interno. Quindi sostituite il file c3d.py nei site-packages di python(se lavorate in virtualenv è meglio, si trova in path_to_env/env_name/lib/python2.7/site-packages) con quello che ho caricato e cancellate il c3d.pyc per sicurezza.

La struttura delle cartelle previste per lo script è:

* cartella_base_dati
  *  0
    *    paziente_1
      *      .c3d
      *      .c3d
  *  1
  *  2
  *  3

nelle cartelle 0-3 basta scompattare gli zip corrispondenti quindi.

## Timeline:
__12/01/2017__ 4-5 ore allo Spallanzani di Reggio. Visita al laboratorio e alle varie strumentazioni,
dimostrazione di alcune prove acquisitie in precedenza.

__27/01/2017__ ricezione dei dati dei pazienti dello Spallanzani: 1142 prove, 178 pazienti, 4 classi.

__17/02/2017__ 1 ora con Calderara, discussione su possibili approcci da prendere.
Dopo una breve descrizione dei dati e nostri tentativi, sono state proposte le seguenti strade:

- RNN stateless su finestre da 1 s l'una, disgiunte. (dove 1 s è arbitrario)
- Rete densa sulle trasformate di Fourier delle coordinate spaziali. Possibilità di sottocampionare e semplificare molto il modello.
- Analisi del laplaciano della matrice di adiacenza, che ha 1 nei joint adiacenti. Riferimenti: LeCun, Skeleton Laplacian

__02/03/2017__ presentazione del lavoro svolto a Guerra.

## Errori / casi particolari
**3 168 168_5.c3d**:
unico file in cui il quarto bit dei punti assume
valori diversi da 0 e -1 (errore di misura della telecamera), inoltre _non ha eventi da cui estrapolare i passi_


**3 114 114_8.c3d**:
header errato, illegibile da python

**0 10 10_1.c3d**:
identico a 0 10 10_2.c3d

**0 10 10_3.c3d**:
identico a 0 10 10_4.c3d

**3 154 154_6.c3d**:
ha pochi markers (248) e _non ha eventi da cui estrapolare i passi_


## Considerazioni
Sono state rimosse 2 prove da quelle fornite perché copie di altre.

Utilizzando i 20 markers consigliati, si ha una copertura di 1089 prove su 1140.

Utilizzando i 12 angoli consigliati, si ha una copertura di 1110 prove su 1140.

Utilizzando sia markers che angoli consigliati, si ha una copertura di 1088 prove su 1140.

#### Boundaries
Alcune prove sono state svolte seguento la direzione laterale corta,
in particolare per quei pazienti con particolare difficoltà di movimento.

- 726 prove sono lungo la direzione principale (y)
- 415 prove sono lungo la direzione laterale (x)
- 11 prove sono quasi diagonali
- 2 prove sono dubbie, perché praticamente diagonali.

#### Bad frames
Alcuni frame nelle prove sono considerati non validi, perché la strumentazione
del laboratorio non è riuscita a catturare le coordinate del marker.

Questi frame sono presenti in 300 prove, in modo più o meno frequente.

A seguito di analisi, per fortuna molti di questi frame invalidi sono consecutivi
e partono o dall'inizio o dalla fine della prova.
Una semplice soluzione per questi casi è il crop della prova che mantiene solo 
i frame validi.

#### Eventi
Di 1140 prove
- 22 presentano eventi con tempo precedente al frame iniziale
- 2 non hanno proprio eventi.

Per quanto riguarda le prove con eventi con tempo negativo, si potrebbe considerare solo
il sottoinsieme di eventi con tempo positivo.

Per quanto riguarda le prove con eventi mancanti, si potrebbero determinare gli eventi
programmaticamente, o semplicemente ignorare dato il piccolo numero di casi.

Avere un algoritmo di stima dei passi potrebbe comunque essere utile anche per
verificare che tutti gli altri eventi siano stati inseriti correttamente.
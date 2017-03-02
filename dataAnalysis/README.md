## Timeline:
__12/01/2017__ 4-5 ore allo Spallanzani di Reggio. Visita al laboratorio e alle varie strumentazioni,
dimostrazione di alcune prove acquisitie in precedenza.

__27/01/2017__ ricezione dei dati dei pazienti dello Spallanzani: 1142 prove, 178 pazienti, 4 classi.

__17/02/2017__ 1-2 ore con Calderara, discussione su possibili approcci da prendere.
Dopo una breve descrizione dei dati e nostri tentativi, sono state proposte le seguenti strade:

- RNN stateless su finestre da 1 s l'una, disgiunte. (dove 1 s è arbitrario)
- Rete densa sulle trasformate di Fourier delle coordinate spaziali. Possibilità di sottocampionare e semplificare molto il modello.
- Analisi del laplaciano della matrice di adiacenza, che ha 1 nei joint adiacenti. Riferimenti: LeCun, Skeleton Laplacian

## Errori / casi particolari
**3 168 168_5.c3d**:
unico file in cui il quarto bit dei punti assume
valori diversi da 0 e -1 (errore di misura della telecamera)

**1 59 59_1.c3d**:
ha 275 markers, di cui solo 255 segnati

**1 59 59_2.c3d**:
ha 339 markers, di cui solo 255 segnati

**3 114 114_8.c3d**:
header errato, illegibile da python

**0 10 10_1.c3d**:
identico a 0 10 10_2.c3d

**0 10 10_3.c3d**.
identico a 0 10 10_4.c3d

## Considerazioni
Utilizzando i 20 markers consigliati, si ha una copertura di 1090 prove su 1142.

#### Boundaries
Alcune prove sono state svolte seguento la direzione laterale corta,
in particolare per quei pazienti con particolare difficoltà di movimento.

726 prove sono lungo la direzione principale (y)
415 prove sono lungo la direzione laterale (x)

11 prove sono quasi diagonali
2 prove sono dubbie, perché praticamente diagonali

#### Bad frames
Alcuni frame nelle prove sono considerati non validi, perché la strumentazione
del laboratorio non è riuscita a catturare le coordinate del marker.

Questi frame sono presenti in 300 prove, in modo più o meno frequente.

A seguito di analisi, per fortuna molti di questi frame invalidi sono consecutivi
e partono o dall'inizio o dalla fine della prova.
Una semplice soluzione per questi casi è il crop della prova che mantiene solo 
i frame validi.
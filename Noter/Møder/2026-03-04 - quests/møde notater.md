# Grammar
Tænk over om det vil være bedst at lære SLM'en hele grammar eller om den blot skal lære regler også bruges kode til at vælge handlinger (atomic actions). 

> Kan man spare læringskraft ved at fjerne handlinger fra læringsdata eller er den bedre med?

Prøv at give hele grammar til GPT-5 og bed den om at lave en quest med kontekst og finde hvad vi mener er 'golden standard' for en quest. Have noget at sammenligne med som er hvad vi ønsker at opnå for en quest.

Lav en sektion 'procedural generation of quests' der viser hvordan vi har lavet koden for 'procedural quest generation'.

## Brug af LM
Man kan bruge koden til at generere quests og derefter bruge SLM til at tilføje 'flavour' til teksten. Man kan bruge ollama og f.eks. hente grok. 

Det vil også kunne bruges til at give den rigtige kontekst for en quest, så alt stemmer over ens.

Vector database kan bruges til at beslutte det mest passende svar for en given handling. Det kan gøres ved at vælge en lille sprogmodel og have den lave en vektor ud fra handlinger, hvor de handlinger bliver sat sammen i en stor vektor til sidst der bruges til at vælge handlinger.

# RAG
chromaDB

# Training different models
Når modeller ikke rammer \<EOS\> så gentager den sig selv. VI kan prøve selv at tilføje \<BOS\> og alle de tegn (tokens) der skal være for at modellerne kan genkende formattet.

flash attention er måske blevet brugt siden nogen modeller er hurtigere end andre og gør kvaliteten dårligere. Nogen modeller er bare hurtigere end andre.

Kig på target_modules for hvilke af de 8 forskellige der gør sig gældende.
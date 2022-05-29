from datetime import datetime

weekly_schedule = {
    0: {"filosofia": "8:00-9:00", "matematica": "9:00-10:00", "inglese": "10:00-11:00", "informatica": "11:15-13:00"},
    1: {"matematica": "8:00-9:00", "fisica": "9:00-10:00", "scienze": "10:00-11:00", "italiano": "11:15-12:00", "inglese": "12:00-13:00"},
    2: {"scienze": "8:00-10:00" , "italiano": "9:00-10:00", "scienze_motorie": "11:15-13:00"},
    3: {"arte": "8:00-9:00", "scienze": "9:00-10:00", "storia": "10:00-12:00", "religione": "12:00-13:00"},
    4: {"inglese": "8:00-9:00" , "scienze": "9:00-10:00", "fisica": "10:00-11:00", "matematica": "11:15-13:00"},
    5: {"italiano": "8:00-10:00", "arte": "10:00-11:00", "fisica": "11:15-12:00", "filosofia": "12:00-13:00"},
    6: {"un bel niente" : "00:00-24:00"}
}

known_birthdays = {
    "Elisa Braconi": "23/11",
    "Federico Cantani": "31/12",
    "Caterina Ciattaglia": "25/11",
    "Alexander Cingolani": "09/06",
    "Loris Durastanti": "26/02",
    "Tommaso Federici": "23/04",
    "Luca Gavazzi": "03/04",
    "Tommaso Ginesi": "31/07",
    "Pietro Giugliano": "09/06",
    "Federico Greganti": "10/08",
    "Alessandro Guzzini": "19/10",
    "Francesco Lillini": "14/12",
    "Elia Magini": "18/09",
    "Emma Marini": "22/12",
    "Matteo Mastri": "25/02",
    "Mattia Matani": "16/07",
    "Riccardo Montesi": "22/02",
    "Margherita Morettini": "09/08",
    "Nicola Salvo": "20/08",
    "Elena Thomas": "01/11",
    "Nicola Urbani": "29/10",
    "Wang Jun Feng": "28/12",
}

status_messages = (
    "Sono un bot, non ho sensazioni, però al momento sono operativo e funzionante. Tu?",
    "Uno schifo. Tu?",
    "Abbastanza bene. Tu?",
    "Oggi meglio del solito. Tu?",
)

days_of_the_week = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato")

command_list = """
<b>Comandi testuali: (Hanno tutti una controparte vocale)</b>
/ricordami_materie - Ti invierò giornalmente la lista delle materie del mattino seguente.
/non_mi_ricordare_materie - Smetterò di ricordarti delle tue materie.
/ricordami_compleanni - Ti ricorderò dei compleanni aggiunti.
/non_mi_ricordare_compleanni - Smetterò di ricordarti dei compleanni.
/elimina_compleanni - Eliminerò tutti i compleanni che hai salvato.
/compleanni_salvati - Visualizza i compleannni salvati dal più vicino al più lontano.
/aggiungi_compleanni_3BS - Aggiungerò i compleanni della 3BS ai tuoi compleanni salvati.
/lista_comandi - Ti la lista dei comandi.
/help - Ti invierò informazioni per contattare gli sviluppatori in caso di problemi.

<b>Comandi vocali:</b>
<i>"Trascrivi su file ____"</i> - Trascriverò ciò che hai detto in un file di testo.
<i>"Ripeti ____"</i> - Ripeterò ciò che hai detto in un messaggio.
<i>"Ricordami dei compleanni salvati"</i> - Ti ricorderò dei compleanni salvati.
<i>"Ricordami le materie"</i> - Ogni giorno ti invierò la lista delle materie del mattino seguente.
<i>"Non ricordarmi le materie"</i> - Smetterò di ricordarti delle tue materie.
<i>"Mostrami i compleanni salvati"</i> - Per vedere l'elenco dei compleanni salvati.
<i>"Aggiungi i compleanni della 3BS"</i> - Aggiungerò i compleanni della 3BS ai tuoi compleanni salvati.

<b>Comandi vocali e testuali:</b>
<i>"Nome Cognome compie gli anni il DD/MM"</i> - Per aggiungere un compleanno.
<i>"Dimentica il compleanno di Nome Cognome"</i> - Per eliminare un compleanno.
<i>"Quando compie gli anni Nome Cognome?"</i> - Per sapere quando qualcuno compie gli anni.
<i>"Quando c'è lezione di ____?"</i> - Per sapere la prossima volta che c'è una materia.
<i>"Come stai?"</i> - Per sapere come sto.
<i>"Che ore sono?"</i> - Per sapere che ore sono.

Se mi invii un file di testo ti invierò un vocale dove lo leggo ad alta voce.
"""
#!/usr/bin/env python
""" conjuguer - conjugaison des verbes francais
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

# Auxiliary verbs conjugation (to speed up things):
aux = {
    "avoir": {
        "Infinitif": {
            "Présent": "avoir",
            "Passé": "avoir eu",
        },
        "Indicatif": {
            "Présent": {
                "s": {
                    "1": "ai",
                    "2": "as",
                    "3": "a",
                },
                "p": {
                    "1": "avons",
                    "2": "avez",
                    "3": "ont",
                },
            },
            "Imparfait": {
                "s": {
                    "1": "avais",
                    "2": "avais",
                    "3": "avait",
                },
                "p": {
                    "1": "avions",
                    "2": "aviez",
                    "3": "avaient",
                },
            },
            "Passé simple": {
                "s": {
                    "1": "eus",
                    "2": "eus",
                    "3": "eut",
                },
                "p": {
                    "1": "eûmes",
                    "2": "eûtes",
                    "3": "eurent",
                },
            },
            "Futur simple": {
                "s": {
                    "1": "aurai",
                    "2": "auras",
                    "3": "aura",
                },
                "p": {
                    "1": "aurons",
                    "2": "aurez",
                    "3": "auront",
                },
            },
            "Passé composé": {
                "s": {
                    "1": "ai eu",
                    "2": "as eu",
                    "3": "a eu",
                },
                "p": {
                    "1": "avons eu",
                    "2": "avez eu",
                    "3": "ont eu",
                },
            },
            "Plus-que-parfait": {
                "s": {
                    "1": "avais eu",
                    "2": "avais eu",
                    "3": "avait eu",
                },
                "p": {
                    "1": "avions eu",
                    "2": "aviez eu",
                    "3": "avaient eu",
                },
            },
            "Passé antérieur": {
                "s": {
                    "1": "eus eu",
                    "2": "eus eu",
                    "3": "eut eu",
                },
                "p": {
                    "1": "eûmes eu",
                    "2": "eûtes eu",
                    "3": "eurent eu",
                },
            },
            "Futur antérieur": {
                "s": {
                    "1": "aurai eu",
                    "2": "auras eu",
                    "3": "aura eu",
                },
                "p": {
                    "1": "aurons eu",
                    "2": "aurez eu",
                    "3": "auront eu",
                },
            },
        },
        "Conditionnel": {
            "Présent": {
                "s": {
                    "1": "aurais",
                    "2": "aurais",
                    "3": "aurait",
                },
                "p": {
                    "1": "aurions",
                    "2": "auriez",
                    "3": "auraient",
                },
            },
            "Passé": {
                "s": {
                    "1": "aurais eu",
                    "2": "aurais eu",
                    "3": "aurait eu",
                },
                "p": {
                    "1": "aurions eu",
                    "2": "auriez eu",
                    "3": "auraient eu",
                },
            },
        },
        "Subjonctif": {
            "Présent": {
                "s": {
                    "1": "aie",
                    "2": "aies",
                    "3": "ait",
                },
                "p": {
                    "1": "ayons",
                    "2": "ayez",
                    "3": "aient",
                },
            },
            "Imparfait": {
                "s": {
                    "1": "eusse",
                    "2": "eusses",
                    "3": "eût",
                },
                "p": {
                    "1": "eussions",
                    "2": "eussiez",
                    "3": "eussent",
                },
            },
            "Passé": {
                "s": {
                    "1": "aie eu",
                    "2": "aies eu",
                    "3": "ait eu",
                },
                "p": {
                    "1": "ayons eu",
                    "2": "ayez eu",
                    "3": "aient eu",
                },
            },
            "Plus-que-parfait": {
                "s": {
                    "1": "eusse eu",
                    "2": "eusses eu",
                    "3": "eût eu",
                },
                "p": {
                    "1": "eussions eu",
                    "2": "eussiez eu",
                    "3": "eussent eu",
                },
            },
        },
        "Impératif": {
            "Présent": {
                "s": {
                    "2": "aie",
                },
                "p": {
                    "1": "ayons",
                    "2": "ayez",
                },
            },
            "Passé": {
                "s": {
                    "2": "aie eu",
                },
                "p": {
                    "1": "ayons eu",
                    "2": "ayez eu",
                },
            },
        },
        "Participe": {
            "Présent": "ayant",
            "Passé": {
                "s": {
                    "m": "eu",
                    "f": "eue",
                },
                "p": {
                    "m": "eus",
                    "f": "eues",
                },
                "a": "ayant eu",
            },
        },
        "Gérondif": {
            "Présent": "ayant",
            "Passé": "ayant eu",
        },
    },

    "être": {
        "Infinitif": {
            "Présent": "être",
            "Passé": "avoir été",
        },
        "Indicatif": {
            "Présent": {
                "s": {
                    "1": "suis",
                    "2": "es",
                    "3": "est",
                },
                "p": {
                    "1": "sommes",
                    "2": "êtes",
                    "3": "sont",
                },
            },
            "Imparfait": {
                "s": {
                    "1": "étais",
                    "2": "étais",
                    "3": "était",
                },
                "p": {
                    "1": "étions",
                    "2": "étiez",
                    "3": "étaient",
                },
            },
            "Passé simple": {
                "s": {
                    "1": "fus",
                    "2": "fus",
                    "3": "fut",
                },
                "p": {
                    "1": "fûmes",
                    "2": "fûtes",
                    "3": "furent",
                },
            },
            "Futur simple": {
                "s": {
                    "1": "serai",
                    "2": "seras",
                    "3": "sera",
                },
                "p": {
                    "1": "serons",
                    "2": "serez",
                    "3": "seront",
                },
            },
            "Passé composé": {
                "s": {
                    "1": "ai été",
                    "2": "as été",
                    "3": "a été",
                },
                "p": {
                    "1": "avons été",
                    "2": "avez été",
                    "3": "ont été",
                },
            },
            "Plus-que-parfait": {
                "s": {
                    "1": "avais été",
                    "2": "avais été",
                    "3": "avait été",
                },
                "p": {
                    "1": "avions été",
                    "2": "aviez été",
                    "3": "avaient été",
                },
            },
            "Passé antérieur": {
                "s": {
                    "1": "eus été",
                    "2": "eus été",
                    "3": "eut été",
                },
                "p": {
                    "1": "eûmes été",
                    "2": "eûtes été",
                    "3": "eurent été",
                },
            },
            "Futur antérieur": {
                "s": {
                    "1": "aurai été",
                    "2": "auras été",
                    "3": "aura été",
                },
                "p": {
                    "1": "aurons été",
                    "2": "aurez été",
                    "3": "auront été",
                },
            },
        },
        "Conditionnel": {
            "Présent": {
                "s": {
                    "1": "serais",
                    "2": "serais",
                    "3": "serait",
                },
                "p": {
                    "1": "serions",
                    "2": "seriez",
                    "3": "seraient",
                },
            },
            "Passé": {
                "s": {
                    "1": "aurais été",
                    "2": "aurais été",
                    "3": "aurait été",
                },
                "p": {
                    "1": "aurions été",
                    "2": "auriez été",
                    "3": "auraient été",
                },
            },
        },
        "Subjonctif": {
            "Présent": {
                "s": {
                    "1": "sois",
                    "2": "sois",
                    "3": "soit",
                },
                "p": {
                    "1": "soyons",
                    "2": "soyez",
                    "3": "soient",
                },
            },
            "Imparfait": {
                "s": {
                    "1": "fusse",
                    "2": "fusses",
                    "3": "fût",
                },
                "p": {
                    "1": "fussions",
                    "2": "fussiez",
                    "3": "fussent",
                },
            },
            "Passé": {
                "s": {
                    "1": "aie été",
                    "2": "aies été",
                    "3": "ait été",
                },
                "p": {
                    "1": "ayons été",
                    "2": "ayez été",
                    "3": "aient été",
                },
            },
            "Plus-que-parfait": {
                "s": {
                    "1": "eusse été",
                    "2": "eusses été",
                    "3": "eût été",
                },
                "p": {
                    "1": "eussions été",
                    "2": "eussiez été",
                    "3": "eussent été",
                },
            },
        },
        "Impératif": {
            "Présent": {
                "s": {
                    "2": "sois",
                },
                "p": {
                    "1": "soyons",
                    "2": "soyez",
                },
            },
            "Passé": {
                "s": {
                    "2": "aie été",
                },
                "p": {
                    "1": "ayons été",
                    "2": "ayez été",
                },
            },
        },
        "Participe": {
            "Présent": "étant",
            "Passé": {
                "s": {
                    "m": "été",
                    "f": "été",
                },
                "p": {
                    "m": "été",
                    "f": "été",
                },
                "a": "ayant été",
            },
        },
        "Gérondif": {
            "Présent": "étant",
            "Passé": "ayant été",
        },
    },
}

# Verbs that are conjugated with être auxiliary:
etre_aux = [
    "advenir",
    "aller",
    "arriver",
    "avenir",
    "décéder",
    "devenir",
    "intervenir",
    "mourir",
    "naître",
    "obvenir",
    "partir",
    "parvenir",
    "provenir",
    "redevenir",
    "renaître",
    "rentrer",
    "repartir",
    "rester",
    "retomber",
    "revenir",
    "survenir",
    "venir",
]

# Verbs that can be conjugated with both auxiliaries:
both_aux = [
    "aborder",
    "aboutir",
    "accoucher",
    "accourir",
    "accroître",
    "alunir",
    "amerrir",
    "apparaître",
    "atterrir",
    "augmenter",
    "avorter",
    "baisser",
    "camper",
    "changer",
    "chavirer",
    "choir",
    "commencer",
    "convenir",
    "crever",
    "croître",
    "crouler",
    "croupir",
    "déborder",
    "décamper",
    "déchoir",
    "décroître",
    "dégeler",
    "dégénérer",
    "déménager",
    "demeurer",
    "dénicher",
    "descendre",
    "diminuer",
    "disconvenir",
    "disparaître",
    "divorcer",
    "échapper",
    "échoir",
    "échouer",
    "éclater",
    "éclore",
    "embellir",
    "empirer",
    "enlaidir",
    "entrer",
    "expier",
    "expirer",
    "faillir",
    "finir",
    "grandir",
    "grossir",
    "jaillir",
    "maigrir",
    "monter",
    "paraître",
    "passer",
    "pourrir",
    "rajeunir",
    "réapparaître",
    "réchapper",
    "récidiver",
    "redescendre",
    "remonter",
    "reparaître",
    "repasser",
    "ressortir",
    "ressusciter",
    "résulter",
    "retourner",
    "sonner",
    "sortir",
    "stationner",
    "tomber",
    "tourner",
    "trébucher",
    "trépasser",
    "vieillir",
]

# Verb patterns association with groups and models:
patterns = {
    "circoncire": [3, "confire"],
    "démanteler": [1, "modeler"],
    "encasteler": [1, "modeler"],
    "stupéfaire": [3, "stupéfaire"],
    "appauvrir": [2, "finir"],
    "bienvenir": [3, "bienvenir"],
    "comparoir": [3, "comparoir"],
    "connaître": [3, "connaître"],
    "crocheter": [1, "modeler"],
    "défaillir": [3, "assaillir"],
    "écarteler": [1, "modeler"],
    "accroire": [3, "accroire"],
    "apparoir": [3, "apparoir"],
    "assavoir": [3, "assavoir"],
    "asservir": [2, "finir"],
    "béqueter": [1, "modeler"],
    "bouillir": [3, "bouillir"],
    "congeler": [1, "modeler"],
    "corseter": [1, "modeler"],
    "cueillir": [3, "cueillir"],
    "enquerre": [3, "enquerre"],
    "épaissir": [2, "finir"],
    "forclore": [3, "forclore"],
    "malfaire": [3, "malfaire"],
    "marteler": [1, "modeler"],
    "messeoir": [3, "messeoir"],
    "pleuvoir": [3, "pleuvoir"],
    "pourvoir": [3, "pourvoir"],
    "racheter": [1, "modeler"],
    "repaître": [3, "repaître"],
    "surgeler": [1, "modeler"],
    "surseoir": [3, "surseoir"],
    "acheter": [1, "modeler"],
    "asseoir": [3, "asseoir"],
    "chaloir": [3, "chaloir"],
    "ciseler": [1, "modeler"],
    "confire": [3, "confire"],
    "déceler": [1, "modeler"],
    "déchoir": [3, "déchoir"],
    "dégeler": [1, "modeler"],
    "endêver": [3, "endêver"],
    "envoyer": [1, "envoyer"],
    "faillir": [3, "faillir"],
    "falloir": [3, "falloir"],
    "fileter": [1, "modeler"],
    "fureter": [1, "modeler"],
    "haleter": [1, "modeler"],
    "jaillir": [2, "finir"],
    "maudire": [2, "finir"],
    "modeler": [1, "modeler"],
    "mouvoir": [3, "mouvoir"],
    "pouvoir": [3, "pouvoir"],
    "prendre": [3, "prendre"],
    "receler": [1, "modeler"],
    "reclure": [3, "reclure"],
    "sourdre": [3, "sourdre"],
    "suffire": [3, "confire"],
    "vaincre": [3, "vaincre"],
    "vouloir": [3, "vouloir"],
    "aillir": [3, "assaillir"],
    "aindre": [3, "craindre"],
    "baller": [1, "aimer"],
    "battre": [3, "battre"],
    "bruire": [2, "finir"],
    "caller": [1, "aimer"],
    "cevoir": [3, "recevoir"],
    "chérir": [2, "finir"],
    "coudre": [3, "coudre"],
    "courir": [3, "courir"],
    "croire": [3, "croire"],
    "daller": [1, "aimer"],
    "devoir": [3, "devoir"],
    "dormir": [3, "dormir"],
    "échoir": [3, "échoir"],
    "eindre": [3, "peindre"],
    "foutre": [3, "rendre"],
    "galler": [1, "aimer"],
    "guérir": [2, "finir"],
    "mentir": [3, "sentir"],
    "mettre": [3, "mettre"],
    "moudre": [3, "moudre"],
    "mourir": [3, "mourir"],
    "naître": [3, "naître"],
    "occire": [3, "occire"],
    "oindre": [3, "joindre"],
    "paître": [3, "paître"],
    "partir": [3, "sentir"],
    "pentir": [3, "sentir"],
    "plaire": [3, "plaire"],
    "raller": [1, "aimer"],
    "rassir": [3, "rassir"],
    "ravoir": [3, "ravoir"],
    "savoir": [3, "savoir"],
    "sentir": [3, "sentir"],
    "servir": [3, "servir"],
    "sortir": [3, "sentir"],
    "soudre": [3, "absoudre"],
    "suivre": [3, "suivre"],
    "taller": [1, "aimer"],
    "tistre": [3, "tistre"],
    "valoir": [3, "valoir"],
    "aître": [3, "connaître"],
    "aller": [3, "aller"],
    "amuïr": [2, "finir"],
    "andre": [3, "rendre"],
    "ardre": [3, "ardre"],
    "avoir": [0, "avoir"],
    "batre": [3, "battre"],
    "boire": [3, "boire"],
    "celer": [1, "modeler"],
    "choir": [3, "choir"],
    "clore": [3, "clore"],
    "clure": [3, "conclure"],
    "crire": [3, "écrire"],
    "ébrer": [1, "céder"],
    "écher": [1, "céder"],
    "écrer": [1, "céder"],
    "égler": [1, "céder"],
    "égner": [1, "céder"],
    "égrer": [1, "céder"],
    "éguer": [1, "céder"],
    "endre": [3, "rendre"],
    "erdre": [3, "rendre"],
    "étrer": [1, "céder"],
    "evrer": [1, "peser"],
    "faire": [3, "faire"],
    "férir": [3, "férir"],
    "fiche": [1, "aimer"],
    "frire": [3, "confire"],
    "gésir": [3, "gésir"],
    "geler": [1, "modeler"],
    "issir": [1, "issir"],
    "ompre": [3, "rendre"],
    "oître": [3, "croître"],
    "ondre": [3, "rendre"],
    "ordre": [3, "rendre"],
    "périr": [2, "finir"],
    "peler": [1, "modeler"],
    "raire": [3, "traire"],
    "seoir": [3, "seoir"],
    "taire": [3, "plaire"],
    "vêtir": [3, "vêtir"],
    "vivre": [3, "vivre"],
    "ayer": [1, "payer"],
    "dire": [3, "dire"],
    "écer": [1, "céder"],
    "ecer": [1, "peser"],
    "éder": [1, "céder"],
    "éger": [1, "assiéger"],
    "éler": [1, "céder"],
    "eler": [1, "jeter"],
    "émer": [1, "céder"],
    "emer": [1, "peser"],
    "éner": [1, "céder"],
    "ener": [1, "peser"],
    "enir": [3, "tenir"],
    "eper": [1, "peser"],
    "érer": [1, "céder"],
    "érir": [3, "acquérir"],
    "éser": [1, "céder"],
    "eser": [1, "peser"],
    "éter": [1, "céder"],
    "être": [0, "être"],
    "eter": [1, "jeter"],
    "ever": [1, "peser"],
    "frir": [3, "couvrir"],
    "fuir": [3, "fuir"],
    "haïr": [2, "haïr"],
    "huir": [3, "huir"],
    "lire": [3, "lire"],
    "ouïr": [3, "ouïr"],
    "oyer": [1, "broyer"],
    "rire": [3, "rire"],
    "voir": [3, "voir"],
    "uire": [3, "cuire"],
    "uyer": [1, "broyer"],
    "vrir": [3, "couvrir"],
    "cer": [1, "placer"],
    "dre": [3, "rendre"],
    "éer": [1, "créer"],
    "ger": [1, "manger"],
    "ier": [1, "apprécier"],
    "er": [1, "aimer"],
    "ir": [2, "finir"],
}

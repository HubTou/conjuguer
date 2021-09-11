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

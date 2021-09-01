#!/usr/bin/env python
""" conjuguer - conjugaison des verbes Français
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import copy
import getopt
import logging
import os
import re
import sys
import time

import colorama

from .aux import aux
from .blank import blank_verb

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: conjuguer - conjugaison des verbes Français v0.1.2 (September 1, 2021) by Hubert Tournier $"

# Default parameters. Can be overcome by environment variables, then command line options
parameters = {
    "Dictionary path": "",
    "Dictionary type": "",
    "Color display": True,
    "Display columns": 4,
    "DictPath": [],
}

# Display constants:
VERB_COLOR = colorama.Fore.WHITE + colorama.Style.BRIGHT
MODE_CAPS=True
MODE_COLOR = colorama.Fore.GREEN + colorama.Style.BRIGHT
MODE_SEPARATOR="═"
TENSE_COLOR = colorama.Fore.CYAN
TENSE_SEPARATOR="─"
EMPTY_CONJUGATION = "-"
BLANK_LINES=True
COLUMN_SPACES = "    "

# Default dictionaries:
ABU = "dict-fr-ABU-mots_communs"
DELA = "dict-fr-DELA"


################################################################################
def display_help():
    """Displays usage and help"""
    print("usage: conjuguer [--debug] [--help|-?] [--version]", file=sys.stderr)
    print("       [-c|--columns NUMBER] [-d|--dictionary PATH] [-n|--nocolor]", file=sys.stderr)
    print("       [--] verb [...]", file=sys.stderr)
    print("  ----------------  -----------------------------------------------------", file=sys.stderr)
    print("  -c|--columns NUM      Choose number of columns to display between 1, 2 or 4", file=sys.stderr)
    print("  -d|--dictionary PATH  Select a specific dictionary", file=sys.stderr)
    print("  -n|--nocolor          Disable color output", file=sys.stderr)
    print("  --debug               Enable debug mode", file=sys.stderr)
    print("  --help|-?             Print usage and this help message and exit", file=sys.stderr)
    print("  --version             Print version and exit", file=sys.stderr)
    print("  --                    Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)


################################################################################
def detect_dictionary_type():
    """Return the type of dictionary or ?"""
    with open(parameters["Dictionary path"], "r", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.strip()
            if line == "avoir,.V+z1:W":
                return "DELA"

            if line == "avoir	avoir	Ver:Inf":
                return "ABU"

    return "?"


################################################################################
def process_environment_variables():
    """Process environment variables"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    if "CONJUGUER_DEBUG" in os.environ.keys():
        logging.disable(logging.NOTSET)

    if "DICTPATH" in os.environ.keys():
        for directory in os.environ["DICTPATH"].split(os.pathsep):
            if os.path.isdir(directory):
                parameters["DictPath"].append(directory)
            else:
                logging.warning('DICTPATH directory "%s" not found', directory)
        if len(parameters["DictPath"]) == 0:
            logging.critical("None of the directories specified in DICTPATH found")
            sys.exit(1)
    else:
        if os.name == "posix":
            if os.path.isdir("/usr/share/dict"):
                parameters["DictPath"].append("/usr/share/dict")
            if os.path.isdir("/usr/local/share/dict"):
                parameters["DictPath"].append("/usr/local/share/dict")
            if "HOME" in os.environ.keys():
                home = os.environ["HOME"]
                if os.path.isdir(home + os.sep + ".local/share/dict"):
                    parameters["DictPath"].append(home + os.sep + ".local/share/dict")

        elif os.name == "nt":
            appdata_path = os.sep + "appdata" + os.sep + "roaming"
            pnu_dictpath = os.sep + "python" + os.sep + "share" + os.sep + "dict"
            if os.environ["APPDATA"]:
                pnu_dictpath = os.environ["APPDATA"] + pnu_dictpath
            elif os.environ["HOMEPATH"]:
                pnu_dictpath = os.environ["HOMEPATH"] + appdata_path + pnu_dictpath
            elif os.environ["USERPROFILE"]:
                pnu_dictpath = os.environ["USERPROFILE"] + appdata_path + pnu_dictpath
            if os.path.isdir(pnu_dictpath):
                parameters["DictPath"].append(pnu_dictpath)

            pnu_dictpath2=sys.executable.replace("python.exe", "share" + os.sep + "dict")
            if os.path.isdir(pnu_dictpath2):
                parameters["DictPath"].append(pnu_dictpath2)

    # Setting the default dictionary, if any:
    # (the first one named words)
    for directory in parameters["DictPath"]:
        if os.path.isfile(directory + os.sep + DELA):
            parameters["Dictionary path"] = directory + os.sep + DELA
            break
        if os.path.isfile(directory + os.sep + ABU):
            parameters["Dictionary path"] = directory + os.sep + ABU
            break

    if "CONJUGUER_DICT" in os.environ.keys():
        if os.path.isfile(os.environ["CONJUGUER_DICT"]):
            parameters["Dictionary path"] = os.environ["CONJUGUER_DICT"]
        else:
            logging.critical("Dictionary pathname doesn't exist: %s", os.environ["CONJUGUER_DICT"])
            sys.exit(1)

    if parameters["Dictionary path"]:
        parameters["Dictionary type"] = detect_dictionary_type()
        if parameters["Dictionary type"] not in ("ABU", "DELA"):
            logging.critical("The selected dictionary doesn't seem to be of ABU or DELA type")
            sys.exit(1)

    logging.debug("process_environment_variables(): parameters:")
    logging.debug(parameters)


################################################################################
def process_command_line():
    """Process command line options"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "c:d:n?"
    string_options = [
        "columns=",
        "debug",
        "dictionary=",
        "help",
        "nocolor",
        "version",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical("Syntax error: %s", error)
        display_help()
        sys.exit(1)

    for option, argument in options:

        if option in ("-c", "--columns"):
            try:
                parameters["Display columns"] = int(argument)
            except ValueError:
                logging.critical("Option -c/--columns is expecting an integer argument")
                sys.exit(1)
            if parameters["Display columns"] not in (1, 2, 4):
                logging.critical("Option -c/--columns is expecting 1, 2 or 4 columns")
                sys.exit(1)

        elif option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("-d", "--dictionary"):
            if os.path.isfile(argument):
                parameters["Dictionary path"] = argument
                parameters["Dictionary type"] = detect_dictionary_type()
                if parameters["Dictionary type"] not in ("ABU", "DELA"):
                    logging.critical("The selected dictionary doesn't seem to be of ABU or DELA type")
                    sys.exit(1)
            else:
                logging.critical("Option -d/--dictionary is expecting a valid pathname")
                sys.exit(1)

        elif option in ("--help", "-?"):
            display_help()
            sys.exit(0)

        elif option in ("-n", "--nocolor"):
            parameters["Color display"] = False

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(0)

    logging.debug("process_command_line(): parameters:")
    logging.debug(parameters)
    logging.debug("process_command_line(): remaining_arguments:")
    logging.debug(remaining_arguments)

    return remaining_arguments


################################################################################
def load_all_verbs_from_dictionary():
    """Load the verbs part of an inflected dictionary"""
    time_start = time.time()
    verbs = []
    with open(parameters["Dictionary path"], "r", encoding="utf-8") as file:
        if parameters["Dictionary type"] == "DELA":
            for line in file.readlines():
                line = line.strip()
                if ".V" in line:
                    verbs.append(line)
        elif parameters["Dictionary type"] == "ABU":
            for line in file.readlines():
                line = line.strip()
                if "	Ver:" in line:
                    verbs.append(line)

    time_stop = time.time()
    logging.debug("load_all_verbs_from_dictionary() time: %f / lines: %d", time_stop - time_start, len(verbs))

    return verbs


################################################################################
def select_verb_from_verbs(verb, verbs):
    """Return only the lines of the inflected dictionary matching the chosen verb"""
    time_start = time.time()
    conjugations = []
    if parameters["Dictionary type"] == "DELA":
        # I don't know if there may be several keys for a same verb
        # let's do like this for the time being...
        verb_keys = []
        for line in verbs:
            if line.startswith(verb + ",.V"):
                key = line.split(",")[1]
                key = re.sub(r":.*", "", key)
                logging.debug("Key: %s", key)
                verb_keys.append(key)
        if len(verb_keys) > 1:
            logging.warning("More than one key found for %s: %s", verb, " ".join(verb_keys))
            logging.warning("Only considering the first one")
        if len(verb_keys) == 0:
            return conjugations

        # note: what follows does not include the infinitive form in conjugations
        # which we already have anyway
        re_key = re.escape("," + verb + verb_keys[0])
        for line in verbs:
            if re.search(re_key, line):
                logging.debug("Line: %s", line)
                conjugations.append(line)

    elif parameters["Dictionary type"] == "ABU":
        for line in verbs:
            if "	" + verb + "	" in line:
                logging.debug("Line: %s", line)
                conjugations.append(line)

    time_stop = time.time()
    logging.debug("select_verb_from_verbs() time: %f / conjugations: %d", time_stop - time_start, len(conjugations))

    return conjugations


################################################################################
def fill_verb_from_dela_dictionary_data(verb, conjugations, auxiliary):
    """Fill a verb data structure rom dictionary data"""
    time_start = time.time()
    conjugated_verb = copy.deepcopy(blank_verb)

    # Conjugation lines have this format:
    # conjugated_verb,unconjugated_verb.V+optional_subclass:inflection1:Inflection2:inflectionN

    conjugated_verb["Infinitif"]["Présent"] = verb

    # We first need to find the "Participe passé" tense for this verb:
    suffix = ""
    for line in conjugations:
        for inflection in line.split(":")[1:]:
            if inflection == "Kms":
                suffix = " " + line.split(",")[0]
                break
    if not suffix:
        logging.warning("Infinitif passé not found for %s", verb)
    else:
        conjugated_verb["Infinitif"]["Passé"] = auxiliary + suffix

    for line in conjugations:
        conjugation = line.split(",")[0]
        for inflection in line.split(":")[1:]:
            part = list(inflection)
            if part[0] == "P":
                conjugated_verb["Indicatif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé composé"][part[2]][part[1]] = aux[auxiliary]["Indicatif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "I":
                conjugated_verb["Indicatif"]["Imparfait"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Plus-que-parfait"][part[2]][part[1]] = aux[auxiliary]["Indicatif"]["Imparfait"][part[2]][part[1]] + suffix
            elif part[0] == "J":
                conjugated_verb["Indicatif"]["Passé simple"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé antérieur"][part[2]][part[1]] = aux[auxiliary]["Indicatif"]["Passé simple"][part[2]][part[1]] + suffix
            elif part[0] == "F":
                conjugated_verb["Indicatif"]["Futur simple"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Futur antérieur"][part[2]][part[1]] = aux[auxiliary]["Indicatif"]["Futur simple"][part[2]][part[1]] + suffix
            elif part[0] == "C":
                conjugated_verb["Conditionnel"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Conditionnel"]["Passé"][part[2]][part[1]] = aux[auxiliary]["Conditionnel"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "S":
                conjugated_verb["Subjonctif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Passé"][part[2]][part[1]] = aux[auxiliary]["Subjonctif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "T":
                conjugated_verb["Subjonctif"]["Imparfait"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Plus-que-parfait"][part[2]][part[1]] = aux[auxiliary]["Subjonctif"]["Imparfait"][part[2]][part[1]] + suffix
            elif part[0] == "Y":
                conjugated_verb["Impératif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Impératif"]["Passé"][part[2]][part[1]] = aux[auxiliary]["Impératif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "G":
                conjugated_verb["Participe"]["Présent"] = conjugation
                conjugated_verb["Gérondif"]["Présent"] = conjugation
                if suffix:
                    conjugated_verb["Participe"]["Passé"]["a"] = aux[auxiliary]["Participe"]["Présent"] + suffix
                    conjugated_verb["Gérondif"]["Passé"] = conjugated_verb["Participe"]["Passé"]["a"]
            elif part[0] == "K":
                conjugated_verb["Participe"]["Passé"][part[2]][part[1]] = conjugation

    time_stop = time.time()
    logging.debug("fill_verb_from_dela_dictionary_data() time: %f / conjugations: %d", time_stop - time_start, len(conjugations))

    return conjugated_verb


################################################################################
def fill_verb_from_abu_dictionary_data(verb, conjugations, auxiliary):
    """Fill a verb data structure rom dictionary data"""
    time_start = time.time()
    conjugated_verb = copy.deepcopy(blank_verb)

    # Conjugation lines have this format:
    # conjugated_verb	unconjugated_verb	Ver:inflection1:Inflection2:inflectionN

    conjugated_verb["Infinitif"]["Présent"] = verb

    # We first need to find the "Participe passé" tense for this verb:
    suffix = ""
    for line in conjugations:
        for inflection in line.split(":")[1:]:
            if inflection == "PPas+Mas+SG":
                suffix = " " + line.split("	")[0]
                break
    if not suffix:
        logging.warning("Infinitif passé not found for %s", verb)
    else:
        conjugated_verb["Infinitif"]["Passé"] = auxiliary + suffix

    for line in conjugations:
        conjugation = line.split("	")[0]
        for inflection in line.split(":")[1:]:
            part = inflection.split("+")

            number = ""
            person = ""
            gender = ""
            if len(part) >= 2:
                if part[1] == "SG":
                    number = "s"
                elif part[1] == "PL":
                    number = "p"
                elif part[1] == "Mas":
                    gender = "m"
                elif part[1] == "Fem":
                    gender = "f"
            if len(part) >= 3:
                if part[2] == "SG":
                    number = "s"
                elif part[2] == "PL":
                    number = "p"
                elif part[2] == "P1":
                    person = "1"
                elif part[2] == "P2":
                    person = "2"
                elif part[2] == "P3":
                    person = "3"

            if part[0] == "IPre":
                conjugated_verb["Indicatif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé composé"][number][person] = aux[auxiliary]["Indicatif"]["Présent"][number][person] + suffix
            elif part[0] == "IImp":
                conjugated_verb["Indicatif"]["Imparfait"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Plus-que-parfait"][number][person] = aux[auxiliary]["Indicatif"]["Imparfait"][number][person] + suffix
            elif part[0] == "IPSim":
                conjugated_verb["Indicatif"]["Passé simple"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé antérieur"][number][person] = aux[auxiliary]["Indicatif"]["Passé simple"][number][person] + suffix
            elif part[0] == "IFut":
                conjugated_verb["Indicatif"]["Futur simple"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Futur antérieur"][number][person] = aux[auxiliary]["Indicatif"]["Futur simple"][number][person] + suffix
            elif part[0] == "CPre":
                conjugated_verb["Conditionnel"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Conditionnel"]["Passé"][number][person] = aux[auxiliary]["Conditionnel"]["Présent"][number][person] + suffix
            elif part[0] == "SPre":
                conjugated_verb["Subjonctif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Passé"][number][person] = aux[auxiliary]["Subjonctif"]["Présent"][number][person] + suffix
            elif part[0] == "SImp":
                conjugated_verb["Subjonctif"]["Imparfait"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Plus-que-parfait"][number][person] = aux[auxiliary]["Subjonctif"]["Imparfait"][number][person] + suffix
            elif part[0] == "ImPre":
                conjugated_verb["Impératif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Impératif"]["Passé"][number][person] = aux[auxiliary]["Impératif"]["Présent"][number][person] + suffix
            elif part[0] == "PPre":
                conjugated_verb["Participe"]["Présent"] = conjugation
                conjugated_verb["Gérondif"]["Présent"] = conjugation
                if suffix:
                    conjugated_verb["Participe"]["Passé"]["a"] = aux[auxiliary]["Participe"]["Présent"] + suffix
                    conjugated_verb["Gérondif"]["Passé"] = conjugated_verb["Participe"]["Passé"]["a"]
            elif part[0] == "PPas":
                conjugated_verb["Participe"]["Passé"][number][gender] = conjugation

    time_stop = time.time()
    logging.debug("fill_verb_from_abu_dictionary_data() time: %f / conjugations: %d", time_stop - time_start, len(conjugations))

    return conjugated_verb


################################################################################
# conjuguer = conjugate in French
def conjuguer(verb, conjugations):
    """Conjugation wrapper to do the (future) dirty work..."""
    if parameters["Dictionary type"] == "DELA":
        conjugated_verb = fill_verb_from_dela_dictionary_data(verb, conjugations, "avoir")
    elif parameters["Dictionary type"] == "ABU":
        conjugated_verb = fill_verb_from_abu_dictionary_data(verb, conjugations, "avoir")
    return conjugated_verb


################################################################################
def print_verb(verb):
    """Return lines describing the conjugated verb"""
    lines = []
    if parameters["Color display"]:
        lines.append(VERB_COLOR + "Tableau de conjugaison du verbe " + colorama.Style.RESET_ALL + verb)
    else:
        lines.append("Tableau de conjugaison du verbe " + verb)
    lines.append("")

    return lines


################################################################################
def print_mode(mode):
    """Return lines describing the conjugation mode"""
    if MODE_CAPS:
        mode = mode.upper()
    lines = []
    if parameters["Color display"]:
        lines.append(MODE_COLOR + mode + colorama.Style.RESET_ALL)
    else:
        lines.append(mode)
        mode = re.sub(r".", MODE_SEPARATOR, mode)
        lines.append(mode)

    return lines


################################################################################
def print_tense(tense):
    """Return lines describing the conjugation tense"""
    lines = []
    if parameters["Color display"]:
        lines.append(TENSE_COLOR + tense + colorama.Style.RESET_ALL)
    else:
        lines.append(tense)
        tense = re.sub(r".", TENSE_SEPARATOR, tense)
        lines.append(tense)
    return lines


################################################################################
def get_pronoun(mode, number, person, conjugated_verb):
    """Return a string with the pronoun to be used depending of the parameters"""
    pronoun = ""
    if mode == "Gérondif":
        pronoun = "en "
    elif mode == "Subjonctif":
        if number == "s":
            if person == "1":
                if conjugated_verb[0] in ['a', 'e', 'i', 'o', 'u', 'y']:
                    pronoun = "que j'   "
                else:
                    pronoun = "que je   "
            elif person == "2":
                pronoun = "que tu   "
            else:
                pronoun = "qu'il    "
        else:
            if person == "1":
                pronoun = "que nous "
            elif person == "2":
                pronoun = "que vous "
            else:
                pronoun = "qu'ils   "
    else:
        if number == "s":
            if person == "1":
                if conjugated_verb[0] in ['a', 'e', 'i', 'o', 'u', 'y']:
                    pronoun = "j'   "
                else:
                    pronoun = "je   "
            elif person == "2":
                pronoun = "tu   "
            else:
                pronoun = "il   "
        else:
            if person == "1":
                pronoun = "nous "
            elif person == "2":
                pronoun = "vous "
            else:
                pronoun = "ils  "

    return pronoun


################################################################################
def strip_ansi_sequences(text):
    """Return a string cleaned of ANSI sequences"""
    # This snippet of code is from Martijn Pieters
    # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


################################################################################
def get_max_width(lines):
    """Return the maximum width of a column of (ANSI sequence stripped) text"""
    max_width = 0
    for line in lines:
        length = len(strip_ansi_sequences(line))
        if length > max_width:
            max_width = length

    return max_width


################################################################################
def get_tense_conjugation(mode, tense, conjugation):
    """Return the conjugation of a verb for a specific mode and tense"""
    column = print_tense(tense)
    if mode == "Infinitif" \
    or (mode == "Participe" and tense == "Présent"):
        if conjugation[mode][tense]:
            column.append(conjugation[mode][tense])
        else:
            column.append(EMPTY_CONJUGATION)
    elif mode == "Participe" and tense == "Passé":
        for number, gender in [["s", "m"], ["s", "f"], ["p", "m"], ["p", "f"]]:
            if conjugation[mode][tense][number][gender]:
                column.append(conjugation[mode][tense][number][gender])
            else:
                column.append(EMPTY_CONJUGATION)
        if conjugation[mode][tense]["a"]:
            column.append(conjugation[mode][tense]["a"])
        else:
            column.append(EMPTY_CONJUGATION)
    elif mode == "Gérondif":
        if conjugation[mode][tense]:
            column.append(
                get_pronoun(mode, "", "", conjugation[mode][tense])
                + conjugation[mode][tense]
            )
        else:
            column.append(EMPTY_CONJUGATION)
    elif mode == "Impératif":
        for number, person in [["s", "2"], ["p", "1"], ["p", "2"]]:
            if conjugation[mode][tense][number][person]:
                column.append(conjugation[mode][tense][number][person])
            else:
                column.append(EMPTY_CONJUGATION)
    else:
        for number in ["s", "p"]:
            for person in ["1", "2", "3"]:
                if conjugation[mode][tense][number][person]:
                    column.append(
                        get_pronoun(mode, number, person, conjugation[mode][tense][number][person])
                        + conjugation[mode][tense][number][person]
                    )
                else:
                    column.append(EMPTY_CONJUGATION)
    if BLANK_LINES:
        column.append("")

    return column


################################################################################
def print_verb_conjugation_odd_columns(conjugation):
    """Print a 1 column verb conjugation"""
    column = []
    column += print_verb(conjugation["Infinitif"]["Présent"])

    column += print_mode("Indicatif")
    for tense in ["Présent", "Imparfait", "Passé simple", "Futur simple", "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
        column += get_tense_conjugation("Indicatif", tense, conjugation)

    column += print_mode("Conditionnel")
    for tense in ["Présent", "Passé"]:
        column += get_tense_conjugation("Conditionnel", tense, conjugation)

    column += print_mode("Subjonctif")
    for tense in ["Présent", "Imparfait", "Passé", "Plus-que-parfait"]:
        column += get_tense_conjugation("Subjonctif", tense, conjugation)

    column += print_mode("Impératif")
    for tense in ["Présent", "Passé"]:
        column += get_tense_conjugation("Impératif", tense, conjugation)

    column += print_mode("Infinitif")
    for tense in ["Présent", "Passé"]:
        column += get_tense_conjugation("Infinitif", tense, conjugation)

    column += print_mode("Participe")
    for tense in ["Présent", "Passé"]:
        column += get_tense_conjugation("Participe", tense, conjugation)

    column += print_mode("Gérondif")
    for tense in ["Présent", "Passé"]:
        column += get_tense_conjugation("Gérondif", tense, conjugation)

    for line in column:
        print(line)


################################################################################
def print_verb_conjugation_even_columns(conjugation):
    """Print a 2 or 4 columns verb conjugation"""
    column_1 = []
    column_1 += print_mode("Indicatif")
    for tense in ["Présent", "Imparfait", "Passé simple", "Futur simple"]:
        column_1 += get_tense_conjugation("Indicatif", tense, conjugation)
    column_1 += print_mode("Conditionnel")
    column_1 += get_tense_conjugation("Conditionnel", "Présent", conjugation)

    column_2 = [""]
    if not parameters["Color display"]:
        column_2.append("")
    for tense in ["Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
        column_2 += get_tense_conjugation("Indicatif", tense, conjugation)
    column_2.append("")
    if not parameters["Color display"]:
        column_2.append("")
    column_2 += get_tense_conjugation("Conditionnel", "Passé", conjugation)

    column_12 = []
    column_1_max_width = get_max_width(column_1)
    for i in range(len(column_1)):
        text = column_1[i]
        for _ in range(column_1_max_width - len(strip_ansi_sequences(column_1[i]))):
            text += " "
        text += COLUMN_SPACES + column_2[i]
        column_12.append(text)

    column_3 = []
    column_3 += print_mode("Subjonctif")
    for tense in ["Présent", "Imparfait"]:
        column_3 += get_tense_conjugation("Subjonctif", tense, conjugation)
    column_3 += print_mode("Impératif")
    column_3 += get_tense_conjugation("Impératif", "Présent", conjugation)
    column_3 += print_mode("Infinitif")
    column_3 += get_tense_conjugation("Infinitif", "Présent", conjugation)
    column_3 += print_mode("Participe")
    column_3 += get_tense_conjugation("Participe", "Présent", conjugation)
    column_3 += ["", "", "", ""]
    column_3 += print_mode("Gérondif")
    column_3 += get_tense_conjugation("Gérondif", "Présent", conjugation)

    column_4 = [""]
    if not parameters["Color display"]:
        column_4.append("")
    for tense in ["Passé", "Plus-que-parfait"]:
        column_4 += get_tense_conjugation("Subjonctif", tense, conjugation)
    column_4.append("")
    if not parameters["Color display"]:
        column_4.append("")
    column_4 += get_tense_conjugation("Impératif", "Passé", conjugation)
    column_4.append("")
    if not parameters["Color display"]:
        column_4.append("")
    column_4 += get_tense_conjugation("Infinitif", "Passé", conjugation)
    column_4.append("")
    if not parameters["Color display"]:
        column_4.append("")
    column_4 += get_tense_conjugation("Participe", "Passé", conjugation)
    column_4.append("")
    if not parameters["Color display"]:
        column_4.append("")
    column_4 += get_tense_conjugation("Gérondif", "Passé", conjugation)

    column_34 = []
    column_3_max_width = get_max_width(column_3)
    for i in range(len(column_3)):
        text = column_3[i]
        for _ in range(column_3_max_width - len(strip_ansi_sequences(column_3[i]))):
            text += " "
        text += COLUMN_SPACES + column_4[i]
        column_34.append(text)

    for line in print_verb(conjugation["Infinitif"]["Présent"]):
        print(line)
    if parameters["Display columns"] == 2:
        for line in column_12 + column_34:
            print(line)
    else:
        for _ in range(len(column_12) - len(column_34)):
            column_34.append("")

        column_12_max_width = get_max_width(column_12)
        for i in range(len(column_12)):
            text = column_12[i]
            for _ in range(column_12_max_width - len(strip_ansi_sequences(column_12[i]))):
                text += " "
            text += COLUMN_SPACES + column_34[i]
            print(text)


################################################################################
def print_verb_conjugation(verb):
    """Print a 1, 2 or 4 columns verb conjugation"""
    if parameters["Display columns"] == 1:
        print_verb_conjugation_odd_columns(verb)
    else:
        print_verb_conjugation_even_columns(verb)


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])

    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)

    process_environment_variables()
    arguments = process_command_line()

    if parameters["Dictionary type"] not in ("ABU", "DELA"):
        logging.debug("Unknown inflected dictionary format")
        sys.exit(1)
    verbs = load_all_verbs_from_dictionary()

    if not arguments:
        logging.critical("conjuguer expects at least one argument")
        display_help()
        sys.exit(1)

    exit_status = 0
    for argument in arguments:
        conjugations = select_verb_from_verbs(argument, verbs)
        if conjugations:
            verb = conjuguer(argument, conjugations)
            print_verb_conjugation(verb)
        else:
            logging.error("%s is not in the dictionary used", argument)
            exit_status = 1

    sys.exit(exit_status)


if __name__ == "__main__":
    main()

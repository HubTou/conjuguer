#!/usr/bin/env python
""" conjuguer - conjugaison des verbes Français
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import collections
import copy
import getopt
import gettext
import locale
import logging
import os
import re
import sys
import time

import colorama

from .verbs import aux, etre_aux, both_aux, patterns
from .blank import blank_verb

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: conjuguer - conjugaison des verbes Français v0.5.1 (October 10, 2021) by Hubert Tournier $"

# Default parameters. Can be overcome by environment variables, then command line options
parameters = {
    "Dictionary path": "",
    "Dictionary type": "",
    "Color display": True,
    "Display columns": 4,
    "DELA output": False,
    "ABU output": False,
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
AU_DELA = "dict-fr-AU-DELA"
DELA = "dict-fr-DELA"
ABU = "dict-fr-ABU-mots_communs"


################################################################################
def initialize_debugging(program_name):
    """Debugging set up"""
    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)


################################################################################
def initialize_internationalization(program_name, lang=locale.getdefaultlocale()[0][:2]):
    """Internationalization set up"""
    locale_dirs = []

    if os.name == "posix":
        # local packages override system packages:
        if "HOME" in os.environ.keys():
            home = os.environ["HOME"]
            if os.path.isdir(home + os.sep + ".local/share/locale"):
                locale_dirs.append(home + os.sep + ".local/share/locale")

        if os.path.isdir("/usr/share/locale"):
            locale_dirs.append("/usr/share/locale")
        if os.path.isdir("/usr/local/share/locale"):
            locale_dirs.append("/usr/local/share/locale")
    elif os.name == "nt":
        appdata_path = os.sep + "appdata" + os.sep + "roaming"
        locale_suffix = os.sep + "python" + os.sep + "share" + os.sep + "locale"
        if os.environ["APPDATA"]:
            locale_path = os.environ["APPDATA"] + locale_suffix
        elif os.environ["HOMEPATH"]:
            locale_path = os.environ["HOMEPATH"] + appdata_path + locale_suffix
        elif os.environ["USERPROFILE"]:
            locale_path = os.environ["USERPROFILE"] + appdata_path + locale_suffix
        if os.path.isdir(locale_path):
            locale_dirs.append(locale_path)

        locale_path = sys.base_prefix + os.sep + "share" + os.sep + "locale"
        if os.path.isdir(locale_path):
            locale_dirs.append(locale_path)

    for directory in locale_dirs:
        if gettext.find(program_name, localedir=directory, languages=[lang]) != None:
            translation = gettext.translation(program_name, localedir=directory, languages=[lang])
            translation.install()
            return

    gettext.install(program_name)


################################################################################
def display_help():
    """Displays usage and help"""
    print(_("usage: conjuguer [--debug] [--help|-?] [--locale LANG] [--version]"), file=sys.stderr)
    print(
        "       "
        + _("[-c|--columns NUMBER] [-n|--nocolor] [-A|--ABU] [-D|--DELA]"),
        file=sys.stderr
    )
    print("       " + _("[-d|--dictionary PATH]"), file=sys.stderr)
    print("       " + _("[--] verb [...]"), file=sys.stderr)
    print(
        "  " + _("--------------------  -----------------------------------------------------"),
        file=sys.stderr
    )
    print(
        "  " + _("-c|--columns NUM      Choose number of columns to display between 1, 2 or 4"),
        file=sys.stderr
    )
    print("  " + _("-d|--dictionary PATH  Select a specific dictionary"), file=sys.stderr)
    print("  " + _("-n|--nocolor          Disable color output"), file=sys.stderr)
    print("  " + _("-A|--ABU              Enable ABU format output"), file=sys.stderr)
    print("  " + _("-D|--DELA             Enable DELA format output"), file=sys.stderr)
    print("  " + _("--debug               Enable debug mode"), file=sys.stderr)
    print(
        "  " + _("--help|-?             Print usage and this help message and exit"),
        file=sys.stderr
    )
    print(
        "  " + _("--locale LANG         Override environment to select another language"),
        file=sys.stderr
    )
    print("  " + _("--version             Print version and exit"), file=sys.stderr)
    print("  " + _("--                    Options processing terminator"), file=sys.stderr)
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
                logging.warning(_("DICTPATH directory") + ' "%s" ' + _("not found"), directory)
        if len(parameters["DictPath"]) == 0:
            logging.critical(_("None of the directories specified in DICTPATH found"))
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

            pnu_dictpath2 = sys.base_prefix + os.sep + "share" + os.sep + "dict"
            if os.path.isdir(pnu_dictpath2):
                parameters["DictPath"].append(pnu_dictpath2)

    # Setting the default dictionary, if any:
    # (the first one named words)
    for directory in parameters["DictPath"]:
        if os.path.isfile(directory + os.sep + AU_DELA):
            parameters["Dictionary path"] = directory + os.sep + AU_DELA
            break
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
            logging.critical(_("Dictionary pathname doesn't exist") + ": %s", os.environ["CONJUGUER_DICT"])
            sys.exit(1)

    if parameters["Dictionary path"]:
        parameters["Dictionary type"] = detect_dictionary_type()
        if parameters["Dictionary type"] not in ("ABU", "DELA"):
            logging.critical(_("The selected dictionary doesn't seem to be of ABU or DELA type"))
            sys.exit(1)

    logging.debug("process_environment_variables(): parameters:")
    logging.debug(parameters)


################################################################################
def process_command_line(program_name):
    """Process command line options"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "Ac:d:Dn?"
    string_options = [
        "ABU",
        "columns=",
        "debug",
        "DELA",
        "dictionary=",
        "help",
        "locale=",
        "nocolor",
        "version",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical(_("Syntax error") + ": %s", error)
        display_help()
        sys.exit(1)

    for option, argument in options:

        if option in ("-A", "--ABU"):
            parameters["ABU output"] = True
            parameters["DELA output"] = False

        elif option in ("-c", "--columns"):
            try:
                parameters["Display columns"] = int(argument)
            except ValueError:
                logging.critical(_("Option -c/--columns is expecting an integer argument"))
                sys.exit(1)
            if parameters["Display columns"] not in (1, 2, 4):
                logging.critical(_("Option -c/--columns is expecting 1, 2 or 4 columns"))
                sys.exit(1)

        elif option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("-D", "--DELA"):
            parameters["DELA output"] = True
            parameters["ABU output"] = False

        elif option in ("-d", "--dictionary"):
            if os.path.isfile(argument):
                parameters["Dictionary path"] = argument
                parameters["Dictionary type"] = detect_dictionary_type()
                if parameters["Dictionary type"] not in ("ABU", "DELA"):
                    logging.critical(
                        _("The selected dictionary doesn't seem to be of ABU or DELA type")
                    )
                    sys.exit(1)
            else:
                logging.critical(_("Option -d/--dictionary is expecting a valid pathname"))
                sys.exit(1)

        elif option in ("--help", "-?"):
            display_help()
            sys.exit(0)

        elif option == "--locale":
            initialize_internationalization(program_name, argument)

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
                    # Unescape "-", "," and "." characters:
                    line = line.replace("\\", "")
                    verbs.append(line)
        elif parameters["Dictionary type"] == "ABU":
            for line in file.readlines():
                line = line.strip()
                if "	Ver:" in line:
                    verbs.append(line)

    time_stop = time.time()
    logging.debug(
        "load_all_verbs_from_dictionary() "
        + _("time")
        + ": %f / "
        + _("lines")
        + ": %d",
        time_stop - time_start, len(verbs)
    )

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
                logging.debug(_("Key") + ": %s", key)
                verb_keys.append(key)
        if len(verb_keys) > 1:
            logging.warning(_("More than one key found for") + " %s: %s", verb, " ".join(verb_keys))
            logging.warning(_("Only considering the first one"))
        if len(verb_keys) == 0:
            return conjugations

        # note: what follows does not include the infinitive form in conjugations
        # which we already have anyway
        re_key = re.escape("," + verb + verb_keys[0])
        for line in verbs:
            if re.search(re_key, line):
                logging.debug(_("Line") + ": %s", line)
                conjugations.append(line)

    elif parameters["Dictionary type"] == "ABU":
        for line in verbs:
            if "	" + verb + "	" in line:
                logging.debug(_("Line") + ": %s", line)
                conjugations.append(line)

    time_stop = time.time()
    logging.debug(
        "select_verb_from_verbs() "
        + _("time")
        + ": %f / "
        + _("conjugations")
        + ": %d",
        time_stop - time_start, len(conjugations)
    )

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
    suffix_s = ""
    suffix_p = ""
    for line in conjugations:
        for inflection in line.split(":")[1:]:
            if inflection == "Kms":
                suffix_s = " " + line.split(",")[0]
            if inflection == "Kmp":
                suffix_p = " " + line.split(",")[0]
    if not suffix_s:
        logging.warning(_("Infinitif passé not found for") + " %s", verb)
    else:
        conjugated_verb["Infinitif"]["Passé"] = auxiliary + suffix_s
    if not suffix_p:
        suffix_p = suffix_s

    for line in conjugations:
        conjugation = line.split(",")[0]
        for inflection in line.split(":")[1:]:
            part = list(inflection)
            suffix = suffix_s
            if auxiliary == "être" and len(part) == 3 and part[2] == "p":
                suffix = suffix_p

            if part[0] == "P":
                conjugated_verb["Indicatif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé composé"][part[2]][part[1]] = \
                        aux[auxiliary]["Indicatif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "I":
                conjugated_verb["Indicatif"]["Imparfait"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Plus-que-parfait"][part[2]][part[1]] = \
                        aux[auxiliary]["Indicatif"]["Imparfait"][part[2]][part[1]] + suffix
            elif part[0] == "J":
                conjugated_verb["Indicatif"]["Passé simple"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé antérieur"][part[2]][part[1]] = \
                        aux[auxiliary]["Indicatif"]["Passé simple"][part[2]][part[1]] + suffix
            elif part[0] == "F":
                conjugated_verb["Indicatif"]["Futur simple"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Futur antérieur"][part[2]][part[1]] = \
                        aux[auxiliary]["Indicatif"]["Futur simple"][part[2]][part[1]] + suffix
            elif part[0] == "C":
                conjugated_verb["Conditionnel"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Conditionnel"]["Passé"][part[2]][part[1]] = \
                        aux[auxiliary]["Conditionnel"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "S":
                conjugated_verb["Subjonctif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Passé"][part[2]][part[1]] = \
                        aux[auxiliary]["Subjonctif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "T":
                conjugated_verb["Subjonctif"]["Imparfait"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Plus-que-parfait"][part[2]][part[1]] = \
                        aux[auxiliary]["Subjonctif"]["Imparfait"][part[2]][part[1]] + suffix
            elif part[0] == "Y":
                conjugated_verb["Impératif"]["Présent"][part[2]][part[1]] = conjugation
                if suffix:
                    conjugated_verb["Impératif"]["Passé"][part[2]][part[1]] = \
                        aux[auxiliary]["Impératif"]["Présent"][part[2]][part[1]] + suffix
            elif part[0] == "G":
                conjugated_verb["Participe"]["Présent"] = conjugation
                conjugated_verb["Gérondif"]["Présent"] = conjugation
                if suffix:
                    conjugated_verb["Participe"]["Passé"]["a"] = \
                        aux[auxiliary]["Participe"]["Présent"] + suffix
                    conjugated_verb["Gérondif"]["Passé"] = \
                        conjugated_verb["Participe"]["Passé"]["a"]
            elif part[0] == "K":
                conjugated_verb["Participe"]["Passé"][part[2]][part[1]] = conjugation

    time_stop = time.time()
    logging.debug(
        "fill_verb_from_dela_dictionary_data() "
        + _("time")
        + ": %f / "
        + _("conjugations")
        + ": %d",
        time_stop - time_start, len(conjugations)
    )

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
    suffix_s = ""
    suffix_p = ""
    for line in conjugations:
        for inflection in line.split(":")[1:]:
            if inflection == "PPas+Mas+SG":
                suffix_s = " " + line.split("	")[0]
            if inflection == "PPas+Mas+PL":
                suffix_p = " " + line.split("	")[0]
    if not suffix_s:
        logging.warning(_("Infinitif passé not found for") + " %s", verb)
    else:
        conjugated_verb["Infinitif"]["Passé"] = auxiliary + suffix_s
    if not suffix_p:
        suffix_p = suffix_s

    for line in conjugations:
        conjugation = line.split("	")[0]
        for inflection in line.split(":")[1:]:
            part = inflection.split("+")

            number = ""
            person = ""
            gender = ""
            if len(part) == 1:
                number = "s"
                gender = "m"
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
            suffix = suffix_s
            if auxiliary == "être" and number == "p":
                suffix = suffix_p

            if part[0] == "IPre":
                conjugated_verb["Indicatif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé composé"][number][person] = \
                        aux[auxiliary]["Indicatif"]["Présent"][number][person] + suffix
            elif part[0] == "IImp":
                conjugated_verb["Indicatif"]["Imparfait"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Plus-que-parfait"][number][person] = \
                        aux[auxiliary]["Indicatif"]["Imparfait"][number][person] + suffix
            elif part[0] == "IPSim":
                conjugated_verb["Indicatif"]["Passé simple"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Passé antérieur"][number][person] = \
                        aux[auxiliary]["Indicatif"]["Passé simple"][number][person] + suffix
            elif part[0] == "IFut":
                conjugated_verb["Indicatif"]["Futur simple"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Indicatif"]["Futur antérieur"][number][person] = \
                        aux[auxiliary]["Indicatif"]["Futur simple"][number][person] + suffix
            elif part[0] == "CPre":
                conjugated_verb["Conditionnel"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Conditionnel"]["Passé"][number][person] = \
                        aux[auxiliary]["Conditionnel"]["Présent"][number][person] + suffix
            elif part[0] == "SPre":
                conjugated_verb["Subjonctif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Passé"][number][person] = \
                        aux[auxiliary]["Subjonctif"]["Présent"][number][person] + suffix
            elif part[0] == "SImp":
                conjugated_verb["Subjonctif"]["Imparfait"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Subjonctif"]["Plus-que-parfait"][number][person] = \
                        aux[auxiliary]["Subjonctif"]["Imparfait"][number][person] + suffix
            elif part[0] == "ImPre":
                conjugated_verb["Impératif"]["Présent"][number][person] = conjugation
                if suffix:
                    conjugated_verb["Impératif"]["Passé"][number][person] = \
                        aux[auxiliary]["Impératif"]["Présent"][number][person] + suffix
            elif part[0] == "PPre":
                conjugated_verb["Participe"]["Présent"] = conjugation
                conjugated_verb["Gérondif"]["Présent"] = conjugation
                if suffix:
                    conjugated_verb["Participe"]["Passé"]["a"] = \
                        aux[auxiliary]["Participe"]["Présent"] + suffix
                    conjugated_verb["Gérondif"]["Passé"] = \
                        conjugated_verb["Participe"]["Passé"]["a"]
            elif part[0] == "PPas":
                conjugated_verb["Participe"]["Passé"][number][gender] = conjugation

    time_stop = time.time()
    logging.debug(
        "fill_verb_from_abu_dictionary_data() "
        + _("time")
        + ": %f / "
        + _("conjugations")
        + ": %d",
        time_stop - time_start, len(conjugations)
    )

    return conjugated_verb


################################################################################
# conjuguer = conjugate in French
def conjuguer(verb, conjugations, auxiliary):
    """Conjugation wrapper to do the (future) dirty work..."""
    if parameters["Dictionary type"] == "DELA":
        conjugated_verb = fill_verb_from_dela_dictionary_data(verb, conjugations, auxiliary)
    elif parameters["Dictionary type"] == "ABU":
        conjugated_verb = fill_verb_from_abu_dictionary_data(verb, conjugations, auxiliary)
    return conjugated_verb


################################################################################
def analyze_verb(verb):
    """Return a verb pattern, group and conjugation model"""
    group = None
    group_text = ""
    model = ""

    for key in patterns.keys():
        if verb.endswith(key):
            group = patterns[key][0]
            model = patterns[key][1]
            break

    if group == 0:
        group_text = _("auxiliary")
    elif group == 1:
        group_text = _("1st group")
    elif group == 2:
        group_text = _("2nd group")
    elif group == 3:
        group_text = _("3rd group")
    else:
        group_text = _("unknown group")

    return key, group_text, model


################################################################################
def print_verb(verb):
    """Return lines describing the conjugated verb"""
    pattern, group, model = analyze_verb(verb)
    lines = []
    if parameters["Color display"]:
        lines.append(
            VERB_COLOR
            + _("Conjugation tables for")
            + " "
            + colorama.Style.RESET_ALL
            + verb
        )
    else:
        lines.append(_("Conjugation tables for") + " " + verb)

    if verb == model:
        lines.append(group + ", " + _("model for verbs like") + " *" + pattern)
    else:
        lines.append(group + ", " + _("conjugated like") + " " + model)

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
                if conjugated_verb[0] in [
                    'a', 'â', 'à', 'ä', 'e', 'ê', 'é', 'è', 'ë',
                    'i', 'î', 'ï', 'o', 'ô', 'ö', 'u', 'ù', 'y'
                ]:
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
                if conjugated_verb[0] in [
                    'a', 'â', 'à', 'ä', 'e', 'ê', 'é', 'è', 'ë',
                    'i', 'î', 'ï', 'o', 'ô', 'ö', 'u', 'ù', 'y'
                ]:
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
    for tense in [
        "Présent", "Imparfait", "Passé simple", "Futur simple",
        "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"
    ]:
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
def add_inflection(inflected_list, key, value):
    """ """
    if key:
        if key in inflected_list.keys():
            inflected_list[key] += value
        else:
            inflected_list[key] = value

    return inflected_list


################################################################################
def print_ABU_inflections(verb):
    """Print a verb conjugations in ABU format"""
    inflected_verb = {}
    inflected_verb = add_inflection(inflected_verb, verb["Infinitif"]["Présent"], ":Inf")
    for plural in [["s", "+SG"], ["p", "+PL"]]:
        for person in [["1", "+P1"], ["2", "+P2"], ["3", "+P3"]]:
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Présent"][plural[0]][person[0]], ":IPre" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Imparfait"][plural[0]][person[0]], ":IImp" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Passé simple"][plural[0]][person[0]], ":IPSim" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Futur simple"][plural[0]][person[0]], ":IFut" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Conditionnel"]["Présent"][plural[0]][person[0]], ":CPre" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Subjonctif"]["Présent"][plural[0]][person[0]], ":SPre" + plural[1] + person[1])
            inflected_verb = add_inflection(inflected_verb, verb["Subjonctif"]["Imparfait"][plural[0]][person[0]], ":SImp" + plural[1] + person[1])
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Présent"], ":PPre")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["s"]["m"], ":PPas+Mas+SG")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["s"]["f"], ":PPas+Fem+SG")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["p"]["m"], ":PPas+Mas+PL")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["p"]["f"], ":PPas+Fem+PL")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["s"]["2"], ":ImPre+SG+P2")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["p"]["1"], ":ImPre+PL+P1")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["p"]["2"], ":ImPre+PL+P2")
    inflected_verb = collections.OrderedDict(sorted(inflected_verb.items()))

    for key in inflected_verb.keys():
        print("{}	{}	Ver{}".format(key, verb["Infinitif"]["Présent"], inflected_verb[key]))


################################################################################
def escape_DELA_special_characters(verb):
    """Escape "-", "," and "." characters with a backslash"""
    verb = verb.replace("-", "\\-")
    verb = verb.replace(",", "\\,")
    verb = verb.replace(".", "\\.")
    return verb


################################################################################
def print_DELA_inflections(verb):
    """Print a verb conjugations in DELA format"""
    inflected_verb = {}
    inflected_verb = add_inflection(inflected_verb, verb["Infinitif"]["Présent"], ":W")
    for plural in ["s", "p"]:
        for person in ["1", "2", "3"]:
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Présent"][plural][person], ":P" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Imparfait"][plural][person], ":I" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Passé simple"][plural][person], ":J" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Indicatif"]["Futur simple"][plural][person], ":F" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Conditionnel"]["Présent"][plural][person], ":C" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Subjonctif"]["Présent"][plural][person], ":S" + person + plural)
            inflected_verb = add_inflection(inflected_verb, verb["Subjonctif"]["Imparfait"][plural][person], ":T" + person + plural)
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Présent"], ":G")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["s"]["m"], ":Kms")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["s"]["f"], ":Kfs")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["p"]["m"], ":Kmp")
    inflected_verb = add_inflection(inflected_verb, verb["Participe"]["Passé"]["p"]["f"], ":Kfp")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["s"]["2"], ":Y2s")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["p"]["1"], ":Y1p")
    inflected_verb = add_inflection(inflected_verb, verb["Impératif"]["Présent"]["p"]["2"], ":Y2p")
    inflected_verb = collections.OrderedDict(sorted(inflected_verb.items()))

    for key in inflected_verb.keys():
        if key == verb["Infinitif"]["Présent"]:
            print(
                "{},.V{}".format(
                    escape_DELA_special_characters(key),
                    inflected_verb[key]
                )
            )
        else:
            print(
                "{},{}.V{}".format(
                    escape_DELA_special_characters(key),
                    escape_DELA_special_characters(verb["Infinitif"]["Présent"]),
                    inflected_verb[key]
                )
            )


################################################################################
def print_verb_conjugation(verb):
    """Print a verb conjugations in different output formats"""
    if parameters["ABU output"]:
        print_ABU_inflections(verb)
    elif parameters["DELA output"]:
        print_DELA_inflections(verb)
    elif parameters["Display columns"] == 1:
        print_verb_conjugation_odd_columns(verb)
    else:
        print_verb_conjugation_even_columns(verb)


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])

    initialize_debugging(program_name)
    initialize_internationalization(program_name)
    process_environment_variables()
    arguments = process_command_line(program_name)

    if not arguments:
        logging.critical(_("conjuguer expects at least one argument"))
        display_help()
        sys.exit(1)

    if parameters["Dictionary type"] not in ("ABU", "DELA"):
        logging.debug(_("Unknown inflected dictionary format"))
        sys.exit(1)

    verbs = load_all_verbs_from_dictionary()

    exit_status = 0
    for argument in arguments:
        conjugations = select_verb_from_verbs(argument, verbs)
        if conjugations:
            verb = None
            verb2 = None

            if argument in etre_aux:
                verb = conjuguer(argument, conjugations, "être")
            elif argument in both_aux:
                verb = conjuguer(argument, conjugations, "être")
                verb2 = conjuguer(argument, conjugations, "avoir")
            else:
                verb = conjuguer(argument, conjugations, "avoir")

            print_verb_conjugation(verb)
            if argument in both_aux \
            and not parameters["ABU output"] \
            and not parameters["DELA output"]:
                print_verb_conjugation(verb2)

        else:
            logging.error("%s " + _("is not in the dictionary used"), argument)
            pattern, group, model = analyze_verb(argument)
            print(
                _("If it really exists, it would be")
                + " "
                + group
                + ", "
                + _("conjugated like")
                + " "
                + model
            )
            exit_status = 1

    sys.exit(exit_status)


if __name__ == "__main__":
    main()

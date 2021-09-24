# Installation
pip install [pnu-conjuguer](https://pypi.org/project/pnu-conjuguer/)

# CONJUGUER(1)

## NAME
conjuguer — conjugaison des verbes Francais

## SYNOPSIS
**conjuguer**
\[-c|--columns NUM\]
\[-d|--dictionary PATH\]
\[-n|--nocolor\]
\[--debug\]
\[--help|-?\]
\[--version\]
\[--\]
verb [...]

## DESCRIPTION
The **conjuguer** utility displays a French conjugation table for the verbs supplied on the command line.

It will display the verb modes and tenses in color, unless you use the *-n|--nocolor* option.

The display will be made in 4 columns, Bescherelle style (a famous verbs dictionary),
or in 1 or 2 columns if you use the *-c|--columns* option.

The data is obtained from a DELA or ABU type inflected French dictionary, rather than generated.
The dictionary will be selected from the *DICTPATH* environment variable,
or obtained from the *-d|--dictionary* option if used.
The dictionary type is automatically detected.

### OPTIONS
Options | Use
------- | ---
-c\|--columns NUM|Choose number of columns to display between 1, 2 or 4
-d\|--dictionary PATH|Select a specific dictionary
-n\|--nocolor|Disable color output
--debug|Enable debug mode
--help\|-?|Print usage and a short help message and exit
--version|Print version and exit
--|Options processing terminator

## ENVIRONMENT
The CONJUGUER_DEBUG environment variable can be set to any value to enable debug mode.

The DICTPATH environment variable is searched for one of the default dictionary files.

Alternatively, the CONJUGUER_DICT environment variable can also be set to the path of the dictionary file you want to use.

## FILES
The *dict-fr-AU-DELA* file is the preferred dictionary used, if found in the *DICTPATH*.

Else, the *dict-fr-DELA* file or the *dict-fr-ABU-mots_communs* file (which contains half of the verbs in the DELA) will be used instead.

## EXIT STATUS
The **conjuguer** utility exits 0 on success, and >0 if an error occurs.

## SEE ALSO
typo(1),
[spell(1)](https://www.freebsd.org/cgi/man.cgi?query=spell),
ispell(1),
aspell(1),
hunspell(1),
dict(7)

## STANDARDS
The **conjuguer** utility is not a standard UNIX command.

This utility tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## HISTORY
This utility was made for the [PNU project](https://github.com/HubTou/PNU),
both as a way to test inflected dictionaries, and to validate the data inside.

## LICENSE
It is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou)

The source code also includes a [snippet of code](https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python) from Martijn Pieters, for stripping ANSI sequences in strings.

## CAVEATS
The results are only as good (or bad) as what's included in the dictionary used.
The data in both the ABU and DELA dictionaries obviously contains errors, often on the same verbs...
I do not know yet the proportion of correct conjugations.

## BUGS
There are probably lots of peculiarities that would need specific processing,
the verbs conjugated with the "être" auxiliary when used with a pronoun for example.

Though the software is probably mostly correct, I will consider it as Beta quality
till I get a better idea of the quality of the source data and offer a way to improve it...

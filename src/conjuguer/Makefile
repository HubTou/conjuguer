NAME=conjuguer
SECTION=1
SOURCES=main.py verbs.py blank.py
DESTROOTDIR=/usr/local

# Default action is to show this help message:
.help:
	@echo "Possible targets:"
	@echo "  check-code     Verify PEP 8 compliance (lint)"
	@echo "  check-security Verify security issues (audit)"
	@echo "  check-unused   Find unused code"
	@echo "  check-version  Find required Python version"
	@echo "  check-sloc     Count Single Lines of Code"
	@echo "  checks         Make all the previous tests"
	@echo "  format         Format code"
	@echo "  install        Install under ${DESTROOTDIR}"
	@echo "  uninstall      Uninstall from ${DESTROOTDIR}"
	@echo "  whatis         Rebuild the whatis(1) database"
	@echo "  clean          Remove the compressed man page"
	@echo "  distclean      Remove everything made"

check-code: /usr/local/bin/pylint
	-pylint ${SOURCES}

lint: check-code

check-security: /usr/local/bin/bandit
	-bandit -r ${SOURCES}

audit: check-security

check-unused: /usr/local/bin/vulture
	-vulture --sort-by-size ${SOURCES}

check-version: /usr/local/bin/vermin
	-vermin ${SOURCES}

check-sloc: /usr/local/bin/pygount
	-pygount --format=summary .

checks: check-code check-security check-unused check-version check-sloc

format: /usr/local/bin/black
	black ${SOURCES}

${NAME}.${SECTION}.gz: ../../man/${NAME}.${SECTION}
	@gzip -k9c ../../man/${NAME}.${SECTION} > ${NAME}.${SECTION}.gz

po/${NAME}.pot:
	@mkdir po
	@xgettext --language=Python -o po/${NAME}.pot *.py

po/en/${NAME}.po: po/${NAME}.pot
	@mkdir -p po/en
	@msginit --locale=en --input=po/${NAME}.pot --output=po/en/${NAME}.po

po/en/${NAME}.mo: po/en/${NAME}.po
	@msgfmt --output-file=po/en/${NAME}.mo po/en/${NAME}.po

po/fr/${NAME}.po: po/${NAME}.pot
	@mkdir -p po/fr
	@msginit --locale=fr --input=po/${NAME}.pot --output=po/fr/${NAME}.po

po/fr/${NAME}.mo: po/fr/${NAME}.po
	@msgfmt --output-file=po/fr/${NAME}.mo po/fr/${NAME}.po

install: ${NAME}.${SECTION}.gz po/en/${NAME}.mo po/fr/${NAME}.mo
	install -m 0755 -o root -g wheel main.py ${DESTROOTDIR}/bin/${NAME}
	install -m 0644 -o root -g wheel ${NAME}.${SECTION}.gz ${DESTROOTDIR}/man/man${SECTION}
	install -m 0644 -o root -g wheel po/en/${NAME}.mo ${DESTROOTDIR}/share/locale/en/LC_MESSAGES
	install -m 0644 -o root -g wheel po/fr/${NAME}.mo ${DESTROOTDIR}/share/locale/fr/LC_MESSAGES

uninstall:
	rm -f ${DESTROOTDIR}/bin/${NAME}
	rm -f ${DESTROOTDIR}/man/man${SECTION}/${NAME}.${SECTION}.gz
	rm -f ${DESTROOTDIR}/share/locale/en/LC_MESSAGES/${NAME}.mo
	rm -f ${DESTROOTDIR}/share/locale/fr/LC_MESSAGES/${NAME}.mo

whatis:
	makewhatis

love:
	@echo "Not war!"

clean:
	@rm -f ${NAME}.${SECTION}.gz po/en/${NAME}.mo po/fr/${NAME}.mo

distclean: clean


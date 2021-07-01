
.phony: all
.SUFFIXES:

all : aux/sil.dtd

aux/sil.dtd : aux/sil_ns.dtd aux/ldml.dtd
	python bin/dtd2dtd -I aux $< $@

aux/sil_ns.dtd : doc/sil_namespace.md
	python bin/extractrnc -t dtd $< $@


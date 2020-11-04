
.phony: all
.SUFFIXES:

all : doc/sil.dtd

doc/sil.dtd : doc/sil_ns.dtd doc/ldml.dtd
	python bin/dtd2dtd -I doc $< $@

doc/sil_ns.dtd : doc/sil_namespace.md
	python bin/extractrnc -t dtd $< $@


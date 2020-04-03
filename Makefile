
.phony: all
.SUFFIXES:

all : doc/sil.dtd

doc/sil.dtd : doc/sil_ns.dtd doc/ldml.dtd
	bin/dtd2dtd -I doc $< $@

doc/sil_ns.dtd : doc/sil_namespace.md
	bin/extractrnc -t dtd $< $@


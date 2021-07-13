
.phony: all
.SUFFIXES:

all : auxdata/sil.dtd

auxdata/sil.dtd : auxdata/sil_ns.dtd auxdata/ldml.dtd
	python bin/dtd2dtd -I auxdata $< $@

auxdata/sil_ns.dtd : doc/sil_namespace.md
	python bin/extractrnc -t dtd $< $@



.phony: all
.SUFFIXES:

all : auxdata/sil.dtd

auxdata/sil.dtd : auxdata/sil_ns.dtd auxdata/ldml.dtd
	python3 bin/dtd2dtd -I auxdata -H $< $@

auxdata/sil_ns.dtd : doc/sil_namespace.md
	python3 bin/extractrnc -t dtd $< $@



.phony: all
.SUFFIXES:

all : doc/sil.rng

doc/sil.dtd : doc/sil.rnc doc/ldml.rnc
	trang -I rnc -O dtd $< $@

doc/sil.rng: doc/sil.rnc doc/ldml.rnc
	trang -I rnc -O rng $< $@
	# trang rewrites its input files after its output file!
	@- touch doc/ldml.rnc $@

doc/ldml.rnc: doc/ldml.rng
	trang -I rng -O rnc $< doc/ldml_temp.rnc
	bin/hackldmlattribs doc/ldml_temp.rnc $@

doc/ldml.rng: doc/ldml.dtd
	trang -I dtd -O rng $< $@

doc/sil.rnc: doc/sil_namespace.md
	bin/extractrnc $< $@

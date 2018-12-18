
.phony: all

all : doc/sil.rng

doc/sil.rng: doc/sil.rnc doc/ldml.rng doc/ldml.rnc
	trang -I rnc -O rng $< $@

doc/ldml.rnc: doc/ldml.rng
	trang -I rng -O rnc $< $@

doc/ldml.rng: doc/ldml.dtd
	trang -I dtd -O rng $< $@

doc/sil.rnc: doc/sil_namespace.md
	bin/extractrnc $< $@

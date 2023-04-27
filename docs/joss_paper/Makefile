
# Setup Ruby and execute `bundle install` to get whedon
OPENJOURNALS_PATH := .whedon/resources

draft: paper.pdf

paper.pdf: paper.md paper.bib
	pandoc -o paper.pdf -V documentclass=scrartcl -V geometry:margin=1in --pdf-engine=xelatex --citeproc paper.md


joss: paper.md paper.bib .whedon
	pandoc \
    --defaults=joss-defaults.yaml \
		--data-dir=$(OPENJOURNALS_PATH) \
		--resource-path=.:$(OPENJOURNALS_PATH) \
		--csl=$(OPENJOURNALS_PATH)/apa.csl \
		--template=$(OPENJOURNALS_PATH)/joss/latex.template \
		--lua-filter=$(OPENJOURNALS_PATH)/time.lua \
  	--metadata=aas_logo_path:$(OPENJOURNALS_PATH)/joss/aas-logo.png \
  	--metadata=logo_path:$(OPENJOURNALS_PATH)/joss/logo.png \
  	$<

.whedon:
	git clone https://github.com/openjournals/whedon $@

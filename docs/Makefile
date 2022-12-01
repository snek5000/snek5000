# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

INTERSPHINX_TARGETS := \
	intersphinx-python \
	intersphinx-jinja2 \
	intersphinx-nek \
	intersphinx-fluiddyn \
	intersphinx-fluidsim

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@printf "Build finished.\nfile://"$(shell pwd)"/_build/html/index.html\n"

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile html $(INTERSPHINX_TARGETS) autobuild cleanall

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


$(INTERSPHINX_TARGETS): intersphinx-%:
	@python ls_intersphinx_targets.py $(subst intersphinx-,,$@)

autobuild:
	@sphinx-autobuild --watch ../src --re-ignore '(_build|generated)\/.*' "$(SOURCEDIR)" "$(BUILDDIR)/html"

cleanall: clean
	@echo "Removing everything under '_generated'..."
	@rm -rf _generated/*

format:
	mdformat --wrap 88 .

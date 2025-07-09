# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)/*

livehtml:
	sphinx-autobuild -b html $(SOURCEDIR) $(BUILDDIR)/html

# LaTeX/PDF build targets
latex:
	@echo "Building LaTeX files..."
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "LaTeX files are in $(BUILDDIR)/latex"

pdf: latex
	@echo "Building PDF from LaTeX..."
	@if command -v xelatex >/dev/null 2>&1; then \
		cd $(BUILDDIR)/latex && \
		xelatex OptiX.tex && \
		xelatex OptiX.tex && \
		echo "PDF built successfully: $(BUILDDIR)/latex/OptiX.pdf"; \
	else \
		echo "XeLaTeX not found. Please install LaTeX distribution."; \
		echo "On macOS: brew install --cask mactex"; \
		echo "On Ubuntu: sudo apt-get install texlive-xetex"; \
		echo "After installation, restart your terminal."; \
		false; \
	fi

# Alternative PDF build using latexmk (if available)
pdflatex: latex
	@echo "Building PDF using latexmk..."
	@if command -v latexmk >/dev/null 2>&1; then \
		cd $(BUILDDIR)/latex && \
		latexmk -pdf -xelatex OptiX.tex && \
		echo "PDF built successfully: $(BUILDDIR)/latex/OptiX.pdf"; \
	else \
		echo "latexmk not found. Falling back to manual xelatex..."; \
		$(MAKE) pdf; \
	fi

# View PDF (macOS specific)
viewpdf: pdf
	@if [ -f "$(BUILDDIR)/latex/OptiX.pdf" ]; then \
		open $(BUILDDIR)/latex/OptiX.pdf; \
	else \
		echo "PDF not found. Run 'make pdf' first."; \
	fi

# LaTeX info target
latexinfo:
	@echo "LaTeX build information:"
	@echo "  Source directory: $(SOURCEDIR)"
	@echo "  Build directory: $(BUILDDIR)"
	@echo "  LaTeX files will be in: $(BUILDDIR)/latex"
	@echo "  PDF will be: $(BUILDDIR)/latex/OptiX.pdf"
	@echo ""
	@echo "Available LaTeX targets:"
	@echo "  latex     - Build LaTeX files"
	@echo "  pdf       - Build PDF from LaTeX"
	@echo "  pdflatex  - Build PDF using latexmk"
	@echo "  viewpdf   - Build and view PDF"
	@echo ""
	@echo "LaTeX dependencies check:"
	@if command -v xelatex >/dev/null 2>&1; then \
		echo "  ✓ xelatex found: $$(which xelatex)"; \
	else \
		echo "  ✗ xelatex not found"; \
	fi
	@if command -v latexmk >/dev/null 2>&1; then \
		echo "  ✓ latexmk found: $$(which latexmk)"; \
	else \
		echo "  ✗ latexmk not found"; \
	fi
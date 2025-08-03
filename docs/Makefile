# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = source
BUILDDIR     = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Custom targets for OptiX documentation

# Build HTML documentation with custom theme
html:
	@echo "Building OptiX HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "HTML documentation built in $(BUILDDIR)/html/"
	@echo "Open $(BUILDDIR)/html/index.html in your browser"

# Build PDF documentation
latexpdf:
	@echo "Building OptiX PDF documentation..."
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@echo "Running LaTeX files through pdflatex..."
	@$(MAKE) -C "$(BUILDDIR)/latex" all-pdf
	@echo "PDF documentation built in $(BUILDDIR)/latex/OptiX.pdf"

# Build both HTML and PDF
all: html latexpdf

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	@rm -rf "$(BUILDDIR)"
	@echo "Build directory cleaned"

# Serve documentation locally
serve:
	@echo "Starting local documentation server..."
	@cd "$(BUILDDIR)/html" && python -m http.server 8080
	@echo "Documentation available at http://localhost:8080"

# Auto-build on file changes (requires sphinx-autobuild)
livehtml:
	@echo "Starting live-reload server for development..."
	@sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --host 0.0.0.0 --port 8080

# Generate API documentation from source code
apidoc:
	@echo "Generating API documentation from source code..."
	@sphinx-apidoc -o "$(SOURCEDIR)/api" "../src" --force --module-first
	@echo "API documentation generated in $(SOURCEDIR)/api/"

# Check for documentation issues
check:
	@echo "Checking documentation for issues..."
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -b coverage "$(SOURCEDIR)" "$(BUILDDIR)/coverage" $(SPHINXOPTS) $(O)
	@echo "Check results in $(BUILDDIR)/linkcheck/ and $(BUILDDIR)/coverage/"

# Build documentation for different formats
epub:
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" $(SPHINXOPTS) $(O)
	@echo "EPUB documentation built in $(BUILDDIR)/epub/"

man:
	@$(SPHINXBUILD) -b man "$(SOURCEDIR)" "$(BUILDDIR)/man" $(SPHINXOPTS) $(O)
	@echo "Manual pages built in $(BUILDDIR)/man/"

# Development helpers
install-deps:
	@echo "Installing documentation dependencies..."
	@pip install sphinx sphinx-rtd-theme sphinx-copybutton sphinx-tabs myst-parser sphinx-autobuild

# Quick development build (faster, less checking)
quickhtml:
	@echo "Building HTML documentation (quick mode)..."
	@$(SPHINXBUILD) -b html -E "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Display documentation statistics
stats:
	@echo "Documentation Statistics:"
	@echo "========================="
	@find "$(SOURCEDIR)" -name "*.rst" -o -name "*.md" | wc -l | awk '{print "Documentation files: " $$1}'
	@find "$(SOURCEDIR)" -name "*.rst" -exec wc -l {} + | tail -1 | awk '{print "Total lines: " $$1}'
	@find "$(SOURCEDIR)" -name "*.py" | wc -l | awk '{print "Python examples: " $$1}'

# Help for OptiX-specific targets
optix-help:
	@echo "OptiX Documentation Build Targets:"
	@echo "=================================="
	@echo "  html         Build HTML documentation with custom theme"
	@echo "  latexpdf     Build PDF documentation"
	@echo "  all          Build both HTML and PDF"
	@echo "  clean        Clean all build files"
	@echo "  serve        Serve HTML docs locally on port 8080"
	@echo "  livehtml     Auto-rebuild docs on file changes"
	@echo "  apidoc       Generate API docs from source code"
	@echo "  check        Check for broken links and coverage"
	@echo "  quickhtml    Fast HTML build for development"
	@echo "  stats        Show documentation statistics"
	@echo "  install-deps Install required Python packages"
	@echo ""
	@echo "Examples:"
	@echo "  make html           # Build HTML documentation"
	@echo "  make livehtml       # Development with auto-reload"
	@echo "  make all            # Build complete documentation"
	@echo "  make serve          # Serve built docs locally"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
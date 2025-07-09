# OptiX Documentation

This directory contains the Sphinx-based documentation for the OptiX library.

## Building the Documentation

### HTML Documentation

To build the HTML documentation:

```bash
cd docs
make html
```

The built documentation will be available in `_build/html/`.

### PDF Documentation

To build the PDF documentation:

```bash
cd docs
make pdf
```

The PDF will be generated as `_build/latex/OptiX.pdf`.

### LaTeX Documentation

To build LaTeX files (without PDF compilation):

```bash
cd docs
make latex
```

The LaTeX files will be available in `_build/latex/`.

## Live Reload

For development with live reload:

```bash
cd docs
make livehtml
```

## LaTeX/PDF Build Targets

- `make latex` - Build LaTeX files only
- `make pdf` - Build PDF from LaTeX (requires XeLaTeX)
- `make pdflatex` - Build PDF using latexmk (alternative method)
- `make viewpdf` - Build and open PDF (macOS only)
- `make latexinfo` - Show LaTeX build information and dependency status

## Requirements

The documentation requires the following packages (already included in pyproject.toml):

- sphinx
- sphinx-rtd-theme
- sphinxcontrib-apidoc
- myst-parser

For class diagrams, you'll also need:

- graphviz (system package)

For PDF generation, you'll also need:

- LaTeX distribution (XeLaTeX)

### Installing Graphviz

On macOS:
```bash
brew install graphviz
```

On Ubuntu/Debian:
```bash
sudo apt-get install graphviz
```

On Windows:
```bash
choco install graphviz
```

### Installing LaTeX

On macOS:
```bash
brew install --cask mactex
# or for a smaller installation:
brew install --cask basictex
```

On Ubuntu/Debian:
```bash
sudo apt-get install texlive-xetex texlive-latex-extra texlive-fonts-recommended
```

On Windows:
```bash
choco install miktex
```

After installing LaTeX, restart your terminal or run:
```bash
eval "$(/usr/libexec/path_helper)"  # macOS only
```

## Documentation Structure

- `index.rst` - Main documentation index
- `overview.rst` - Library overview and features
- `quickstart.rst` - Quick start guide
- `examples.rst` - Usage examples
- `architecture.rst` - Architecture documentation
- `api/` - API reference documentation
- `conf.py` - Sphinx configuration
- `_build/` - Built documentation (generated)
- `_static/` - Static files for documentation

## Features

- **Autodoc**: Automatically generates documentation from Python docstrings
- **Class Diagrams**: Inheritance diagrams using Sphinx extensions
- **Cross-references**: Automatic linking between documentation sections
- **Search**: Built-in search functionality
- **RTD Theme**: Professional Read the Docs theme
- **PDF Generation**: Modern-looking PDF documentation with LaTeX
- **Multiple Formats**: HTML, PDF, LaTeX, and ePub output formats
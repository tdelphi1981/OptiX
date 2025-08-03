# OptiX Documentation

This directory contains the comprehensive documentation for the OptiX Mathematical Optimization Framework.

## 📚 Documentation Structure

```
docs/
├── source/                 # Sphinx source files
│   ├── conf.py            # Sphinx configuration
│   ├── index.rst          # Documentation homepage
│   ├── installation.rst   # Installation guide
│   ├── quickstart.rst     # Quick start guide
│   ├── api/               # API reference documentation
│   ├── tutorials/         # Step-by-step tutorials
│   ├── examples/          # Comprehensive examples
│   └── user_guide/        # User guide sections
├── build/                 # Generated documentation
│   ├── html/             # HTML documentation
│   └── latex/            # LaTeX/PDF documentation
├── _static/              # Static assets (CSS, JS, images)
├── _templates/           # Custom Sphinx templates
├── Makefile              # Build automation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Building Documentation

### Prerequisites

1. **Python 3.12+** with pip
2. **LaTeX distribution** (for PDF generation):
   - **Linux**: `sudo apt-get install texlive-full`
   - **macOS**: Install MacTeX from https://tug.org/mactex/
   - **Windows**: Install MiKTeX from https://miktex.org/

### Quick Setup

```bash
# Navigate to docs directory
cd docs

# Install dependencies
pip install -r requirements.txt

# Build HTML documentation
make html

# Open in browser
open build/html/index.html  # macOS
# or
xdg-open build/html/index.html  # Linux
# or
start build/html/index.html  # Windows
```

### Available Build Targets

```bash
# HTML documentation (recommended for development)
make html

# PDF documentation
make latexpdf

# Build both HTML and PDF
make all

# Clean build directory
make clean

# Serve documentation locally
make serve  # Available at http://localhost:8080

# Auto-rebuild on changes (for development)
make livehtml

# Generate API docs from source code
make apidoc

# Check for broken links and coverage
make check

# Quick build (faster, less validation)
make quickhtml

# Show documentation statistics
make stats

# See all available targets
make optix-help
```

## 🎨 Custom Theming

### HTML Theme Features

- **Modern Design**: Custom CSS with OptiX branding
- **Responsive Layout**: Mobile-friendly responsive design
- **Interactive Elements**: Copy buttons, tabs, collapsible sections
- **Enhanced Navigation**: Improved sidebar and breadcrumbs
- **Code Highlighting**: Syntax highlighting for Python and other languages
- **Search Integration**: Full-text search with highlighting
- **Dark Mode**: Toggle between light and dark themes

### LaTeX/PDF Theme Features

- **Professional Layout**: Academic-quality typesetting
- **Custom Title Page**: OptiX-branded cover design
- **Mathematics Support**: Beautiful equation rendering
- **Code Listings**: Properly formatted code blocks
- **Cross-references**: Automatic linking and numbering
- **Bibliography**: Citation and reference management

## 📖 Content Organization

### API Reference
- **problem.rst**: Problem type classes (CSP, LP, GP)
- **solvers.rst**: Solver interfaces and implementations
- **constraints.rst**: Constraint definitions and operators
- **variables.rst**: Variable management and types
- **data.rst**: Database integration and data management
- **utilities.rst**: Utility functions and helpers

### Examples
- **diet_problem.rst**: Classic linear programming example
- **bus_assignment.rst**: Goal programming with real-world data
- **production_planning.rst**: Multi-objective optimization
- **portfolio_optimization.rst**: Financial optimization application

### Tutorials
- **linear_programming.rst**: LP theory and implementation
- **goal_programming.rst**: Multi-objective optimization
- **special_constraints.rst**: Non-linear constraint modeling
- **custom_solvers.rst**: Extending with new solvers

### User Guide
- **problem_types.rst**: Understanding CSP, LP, and GP
- **solvers.rst**: Solver selection and configuration
- **constraints.rst**: Advanced constraint modeling
- **variables.rst**: Variable creation and management
- **database_integration.rst**: Working with data objects

## 🛠 Development Workflow

### Live Development

For documentation development with auto-reload:

```bash
# Start live-reload server
make livehtml

# Edit files in source/
# Browser automatically refreshes on changes
```

### Adding New Content

1. **Create new .rst file** in appropriate directory
2. **Add to toctree** in relevant index file
3. **Build and test** with `make html`
4. **Check links** with `make check`

### Writing Guidelines

- Use **reStructuredText** (.rst) for main content
- Use **Markdown** (.md) for simple pages (via MyST parser)
- Include **code examples** for all features
- Add **cross-references** using Sphinx directives
- Follow **existing style** and structure

### Code Examples

```rst
.. code-block:: python
   :caption: Example Caption
   :linenos:

   from problem import OXLPProblem
   
   # Create problem
   problem = OXLPProblem()

.. note::
   This is a note admonition.

.. tip::
   This is a tip admonition.

.. warning::
   This is a warning admonition.
```

## 📊 Quality Assurance

### Automated Checks

```bash
# Link checking
make check  # Checks external links

# Coverage analysis
sphinx-build -b coverage source build/coverage

# Spell checking (if aspell installed)
sphinx-build -b spelling source build/spelling
```

### Manual Review

- **Content accuracy**: Verify code examples work
- **Cross-references**: Check internal links
- **Formatting**: Ensure consistent styling
- **Completeness**: All features documented

## 🔧 Customization

### Modifying Themes

**HTML Theme**:
- Edit `_static/css/custom.css` for styling
- Modify `_static/js/custom.js` for behavior
- Update `source/conf.py` for theme options

**LaTeX Theme**:
- Edit `latex_elements` in `source/conf.py`
- Customize preamble for additional packages
- Modify templates in `_templates/` if needed

### Adding Extensions

1. **Install extension**: `pip install sphinx-extension-name`
2. **Add to conf.py**: Include in `extensions` list
3. **Configure**: Add extension settings
4. **Test**: Build and verify functionality

## 📈 Analytics and Metrics

### Documentation Statistics

```bash
make stats  # Show file counts and metrics
```

### Build Performance

```bash
# Time the build process
time make html

# Profile Sphinx build
sphinx-build -v -T source build/html
```

## 🚀 Deployment

### GitHub Pages

```bash
# Build HTML documentation
make html

# Copy to gh-pages branch
cp -r build/html/* /path/to/gh-pages/

# Commit and push
cd /path/to/gh-pages/
git add .
git commit -m "Update documentation"
git push origin gh-pages
```

### Read the Docs

1. Connect repository to Read the Docs
2. Configure `.readthedocs.yml` in project root
3. Automatic builds on commits

### Docker Deployment

```dockerfile
FROM nginx:alpine
COPY build/html /usr/share/nginx/html
EXPOSE 80
```

## 🧪 Testing Documentation

### Local Testing

```bash
# Build all formats
make all

# Test serving
make serve

# Open different browsers for testing
```

### Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Documentation
on: [push, pull_request]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        cd docs
        pip install -r requirements.txt
    - name: Build documentation
      run: |
        cd docs
        make html
    - name: Check links
      run: |
        cd docs
        make check
```

## 💡 Tips and Best Practices

### Performance
- Use `make quickhtml` for faster development builds
- Minimize image sizes in `_static/`
- Use caching for external resources

### Content
- Write for your audience (beginners vs. experts)
- Include practical examples
- Update regularly with new features
- Cross-reference related sections

### Maintenance
- Review and update annually
- Check for outdated information
- Update dependencies regularly
- Monitor build warnings

## 🆘 Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Clean and rebuild
make clean
make html
```

**Missing Dependencies**:
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

**LaTeX Errors**:
```bash
# Check LaTeX installation
pdflatex --version

# Install missing packages
tlmgr install <package-name>
```

**Extension Conflicts**:
- Check `conf.py` extension configuration
- Test with minimal extensions
- Update to compatible versions

### Getting Help

- Check Sphinx documentation: https://www.sphinx-doc.org/
- OptiX project issues: GitHub Issues
- Sphinx community: Stack Overflow with `sphinx` tag

## 📄 License

Documentation is licensed under the same terms as the OptiX project (AFL-3.0).

---

**Happy documenting! 📚✨**
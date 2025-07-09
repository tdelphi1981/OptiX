# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OptiX'
copyright = '2025, Tolga BERBER, Beyzanur SİYAH'
author = 'Tolga BERBER, Beyzanur SİYAH'
version = '0.1.0'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.autosummary',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Autodoc configuration ---------------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
}

# -- Napoleon configuration --------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# -- Inheritance diagram configuration ---------------------------------------
inheritance_graph_attrs = dict(rankdir="TB", size='"6.0, 8.0"',
                               fontsize=14, ratio='compress')
inheritance_node_attrs = dict(shape='ellipse', fontsize=14, color='blue',
                             style='filled', fillcolor='lightblue')
inheritance_edge_attrs = dict(penwidth=1.2, color='black')

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# -- Autosummary configuration -----------------------------------------------
autosummary_generate = True

# -- Options for LaTeX output ------------------------------------------------
latex_engine = 'xelatex'
latex_use_xindy = False

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'fontpkg': r'''
        \usepackage{fontspec}
        \setmainfont{Times New Roman}
        \setsansfont{Arial}
        \setmonofont{Courier New}
    ''',
    'preamble': r'''
        \usepackage{xcolor}
        \usepackage{geometry}
        \usepackage{fancyhdr}
        \usepackage{titlesec}
        \usepackage{tocloft}
        \usepackage{booktabs}
        \usepackage{longtable}
        \usepackage{array}
        \usepackage{multirow}
        \usepackage{wrapfig}
        \usepackage{float}
        \usepackage{colortbl}
        \usepackage{pdflscape}
        \usepackage{tabu}
        \usepackage{threeparttable}
        \usepackage{threeparttablex}
        \usepackage{ulem}
        \usepackage{makecell}
        
        % Modern color scheme
        \definecolor{primarycolor}{RGB}{0, 123, 191}
        \definecolor{secondarycolor}{RGB}{108, 117, 125}
        \definecolor{accentcolor}{RGB}{255, 193, 7}
        \definecolor{codebackground}{RGB}{248, 249, 250}
        
        % Custom geometry
        \geometry{
            top=1.2in,
            bottom=1.2in,
            left=1.1in,
            right=1.1in,
            headheight=14pt,
            headsep=0.3in,
            footskip=0.3in
        }
        
        % Custom headers and footers
        \pagestyle{fancy}
        \fancyhf{}
        \fancyhead[LE,RO]{\textcolor{primarycolor}{\textbf{\thepage}}}
        \fancyhead[LO]{\textcolor{secondarycolor}{\nouppercase{\leftmark}}}
        \fancyhead[RE]{\textcolor{secondarycolor}{\nouppercase{\rightmark}}}
        \fancyfoot[C]{\textcolor{secondarycolor}{\small OptiX Framework Documentation}}
        \renewcommand{\headrulewidth}{0.5pt}
        \renewcommand{\footrulewidth}{0.5pt}
        \renewcommand{\headrule}{\hbox to\headwidth{\color{primarycolor}\leaders\hrule height \headrulewidth\hfill}}
        \renewcommand{\footrule}{\hbox to\headwidth{\color{primarycolor}\leaders\hrule height \footrulewidth\hfill}}
        
        % Title formatting
        \titleformat{\chapter}[display]
            {\normalfont\huge\bfseries\color{primarycolor}}
            {\chaptertitlename\ \thechapter}{20pt}{\Huge}
        \titleformat{\section}
            {\normalfont\Large\bfseries\color{primarycolor}}
            {\thesection}{1em}{}
        \titleformat{\subsection}
            {\normalfont\large\bfseries\color{secondarycolor}}
            {\thesubsection}{1em}{}
        \titleformat{\subsubsection}
            {\normalfont\normalsize\bfseries\color{secondarycolor}}
            {\thesubsubsection}{1em}{}
        
        % Code block styling
        \definecolor{VerbatimColor}{RGB}{248, 249, 250}
        \definecolor{VerbatimBorderColor}{RGB}{222, 226, 230}
        
        % Table of contents styling
        \renewcommand{\cfttoctitlefont}{\huge\bfseries\color{primarycolor}}
        \renewcommand{\cftchapfont}{\bfseries\color{primarycolor}}
        \renewcommand{\cftsecfont}{\color{secondarycolor}}
        \renewcommand{\cftsubsecfont}{\color{secondarycolor}}
        
        % Hyperlink colors
        \usepackage{hyperref}
        \hypersetup{
            colorlinks=true,
            linkcolor=primarycolor,
            urlcolor=primarycolor,
            citecolor=primarycolor,
            filecolor=primarycolor
        }
        
        % Custom title page
        \makeatletter
        \renewcommand{\maketitle}{
            \begin{titlepage}
                \centering
                \vspace*{2cm}
                
                {\Huge\bfseries\color{primarycolor} \@title \par}
                \vspace{1.5cm}
                
                {\LARGE\color{secondarycolor} Python Optimization Framework \par}
                \vspace{0.5cm}
                
                {\Large\color{secondarycolor} Version \@release \par}
                \vspace{2cm}
                
                {\large\color{secondarycolor} \@author \par}
                \vspace{1cm}
                
                {\large\color{secondarycolor} \@date \par}
                
                \vfill
                
                {\small\color{secondarycolor} 
                This documentation provides comprehensive information about the OptiX framework, \\
                including API reference, examples, and architectural details.
                \par}
                
                \vspace{1cm}
            \end{titlepage}
        }
        \makeatother
    ''',
    'tableofcontents': r'''
        \tableofcontents
        \clearpage
    ''',
    'printindex': r'\printindex',
    'sphinxsetup': '''
        hmargin={1.1in,1.1in},
        vmargin={1.2in,1.2in},
        verbatimwithframe=true,
        VerbatimColor={RGB}{248,249,250},
        VerbatimBorderColor={RGB}{222,226,230},
        noteBorderColor={RGB}{255,193,7},
        warningBorderColor={RGB}{220,53,69},
        attentionBorderColor={RGB}{255,193,7},
        importantBorderColor={RGB}{40,167,69},
        tipBorderColor={RGB}{23,162,184}
    '''
}

# LaTeX document class and options
latex_documents = [
    ('index', 'OptiX.tex', 'OptiX Documentation',
     'Tolga BERBER, Beyzanur SİYAH', 'manual'),
]

# LaTeX logo
latex_logo = None

# LaTeX additional files
latex_additional_files = []

# -- Options for manual page output ------------------------------------------
man_pages = [
    ('index', 'optix', 'OptiX Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    ('index', 'OptiX', 'OptiX Documentation',
     author, 'OptiX', 'Python Optimization Framework',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

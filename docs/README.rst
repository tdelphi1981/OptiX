OptiX Documentation
==================

This directory contains the documentation for the OptiX project.

Building the Documentation
-------------------------

To build the documentation, you need to have Sphinx and other required packages installed.
You can install them using Poetry:

.. code-block:: bash

    poetry install --with dev

Then, you can build the documentation using:

.. code-block:: bash

    # On Unix-like systems
    cd docs
    make html

    # On Windows
    cd docs
    make.bat html

The built documentation will be available in the `_build/html` directory.
You can open `_build/html/index.html` in your browser to view it.

Documentation Structure
---------------------

- `index.rst`: Main documentation page
- `installation.rst`: Installation instructions
- `usage.rst`: Usage examples
- `api/`: Auto-generated API documentation
- `contributing.rst`: Contribution guidelines (from CONTRIBUTING.md)
- `changelog.rst`: Project changelog (from CHANGELOG.md)

Adding New Documentation
----------------------

To add new documentation:

1. Create a new `.rst` file in the `docs` directory
2. Add the file to the table of contents in `index.rst`
3. Build the documentation to see your changes
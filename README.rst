ChecklistTools
==============

ChecklistTools is a collection of Python scripts to facilitate work with
`ENA sample checklists <https://www.ebi.ac.uk/ena/browser/checklists>`_.

Source repository: `<https://github.com/jmenglund/ChecklistTools>`_

--------------------------------

.. contents:: Table of contents
   :local:
   :backlinks: none


Prerequisites
-------------

* Python 3.10+
* The Python library `Pandera <https://github.com/unionai-oss/pandera>`_
  version 0.16.1 or higher (installed with the tool)

An easy way to get Python working on your computer is to install the free
`Anaconda distribution <http://anaconda.com/download)>`_.


Installation
------------

The project is hosted at `<https://github.com/jmenglund/ChecklistTools>`_ and 
can be installed using `pip`:

.. code-block::

    $ pip install git+https://github.com/jmenglund/ChecklistTools.git#egg=ChecklistTools

You may consider installing ChecklistTools and its required Python packages 
within a virtual environment in order to avoid cluttering your system's 
Python path.

Usage
-----

Use the command-line tool ``validate_samples`` to validate sample metadata
against a `checklist <https://www.ebi.ac.uk/ena/browser/checklists>`_:

.. code-block::
    

    $ validate_samples --help   
    usage: validate_samples.py [-h] [-V] [-o, --output FILE] checklist-file samples-file

    Validate sample metadata before submitting them to ENA

    positional arguments:
    checklist-file     Checkist XML file
    samples-file       TSV-file with sample metadata

    optional arguments:
    -h, --help         show this help message and exit
    -V, --version      show program's version number and exit
    -o, --output FILE  output file with failure cases in TSV format


License
-------

ChecklistTools is distributed under the 
`MIT license <https://opensource.org/licenses/MIT>`_.


Author
------

Markus Englund, `orcid.org/0000-0003-1688-7112 <http://orcid.org/0000-0003-1688-7112>`_

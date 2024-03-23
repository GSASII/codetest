# -*- coding: utf-8 -*-
#
# sphinx documentation build configuration file based on one built by sphinx-quickstart
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath(os.path.join('..', '..','GSASII')))
sys.path.insert(1, os.path.abspath(os.path.join('..', '..','GSASII','exports')))
sys.path.insert(1, os.path.abspath(os.path.join('..', '..','GSASII','imports')))
sys.path.insert(1, os.path.abspath(os.path.join('..', '..','GSASII','install')))
sys.path.insert(1, os.path.abspath(os.path.join('..', '..','tests')))
# get version number tag from git
# scan all files to get version number
import git
g2repo = git.Repo(os.path.abspath(os.path.join('..', '..')))
version_date = g2repo.head.commit.committed_datetime.strftime('%d-%b-%Y %H:%M')
version = None
for h in list(g2repo.iter_commits('HEAD'))[:50]: # (don't go too far back)
    tags = g2repo.git.tag('--points-at',h).split('\n')
    for item in tags:
        try:
            if item.isnumeric():
                version = int(item)
                break
        except:
            pass
    if version: break
print(f'Found highest version as {version}')
# put the version into the docs
print(os.path.split(__file__)[0])
fp = open(os.path.join(os.path.split(__file__)[0],'version.rst'),'w')
fp.write(f'This documentation was prepared from GSAS-II from {version_date} tagged as version {version}\n')
fp.close()
# update to use the most recent variables list
fil = os.path.normpath(os.path.join(
    os.path.split(__file__)[0],'..','..','GSASII','install','makeVarTbl.py'))
with open(fil, 'rb') as f:
    exec(compile(f.read(), fil, 'exec'), {"__file__": fil,"__name__": "__main__"})
# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'
# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'GSAS-II'
copyright = u'2013-2024, R. B. Von Dreele and B. H. Toby for Argonne National Laboratory'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = f'{version}'
# The full version, including alpha/beta/rc tags.
release = 'version {version} {version_date}'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'
#html_theme = 'default'
#html_theme = 'agogo'
#html_theme = 'sphinxdoc'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'collapse_navigation': False,
#    'navigation_depth': 2,
#    'includehidden': False,
#    'titles_only': True
}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'G2_html_logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# to force tables from being too wide in the HTML rendering
# file trunk/docs/source/_static/theme_overrides.css is added
# to limit the page width.
html_css_files = [
    'theme_overrides.css',
]

# from https://github.com/spacetelescope/pysynphot/issues/116 (tnx Paul)
# converts LaTeX Angstrom symbol to Unicode symbol in HTML output
rst_prolog = u"""\

.. only:: html

  :math:`\\renewcommand\\AA{\\text{Å}}`

"""



# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'GSASIIdoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

#this allows \AA to be used in equations 
'preamble': '\\global\\renewcommand{\\AA}{\\text{\\r{A}}}',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'GSASIIdoc.tex', u'GSAS-II Developers Documentation',
   u'Robert B. Von Dreele and Brian H. Toby', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = 'G2_html_logo.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True

#build PDF with Unicode characters
latex_engine = 'xelatex'

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'GSASIIdoc', u'GSAS-II Developers Documentation',
     [u'Robert B. Von Dreele',u'Brian H. Toby'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'GSASIIdoc', u'GSAS-II Developers Documentation',
   u'Robert B. Von Dreele and Brian H. Toby', 'GSASIIdoc', 'GSAS-II Developers Manual',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# set up dummy packages for misc imports not on readthedocs
#autodoc_mock_imports = "wx numpy scipy matplotlib pillow OpenGL h5py".split()

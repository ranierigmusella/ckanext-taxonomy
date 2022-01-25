import sys
import click
from logging import getLogger

logger = getLogger(__name__)

# Click commands for CKAN 2.9 and above

usage = """
# Initialising the database
paster taxonomy init

# Remove the database tables
paster taxonomy cleanup

# Loading a taxonomy
paster taxonomy load --url URL --name NAME --title TITLE --lang LANG --uri URI
paster taxonomy load --filename FILE --name NAME --title TITLE --lang LANG --uri URI

# Loading taxonomy extras
paster taxonomy load-extras --filename FILE --name NAME

Where:
    URL  is the url to a SKOS document
    FILE is the local path to a SKOS/extras document
    NAME is the short-name of the taxonomy
    TITLE is the title of the taxonomy
    LANG (optional) is a language identifier, e.g. en, es, fr
    URI is a uri for the taxonomy
"""

@click.group(short_help='Perform Tag Taxonomy related actions')
def taxonomy():
    """taxonomy commands
    """
    pass


@taxonomy.command()
def init():
    """Creates the database tables required.
    """
    from ckanext.taxonomy.models import init_tables
    init_tables()
    logger.info("DB tables created")


@taxonomy.command()
def cleanup():
    """Deletes the database tables required.
    """
    from ckanext.taxonomy.models import remove_tables
    remove_tables()
    logger.info("DB tables removed")


@taxonomy.command()
@click.argument(u'filename')
@click.argument(u'name')
def load_extras(filename, name):
    """
    Load extra information about the terms in the taxonomy

    These are loaded from a JSON file which contains an Array of Objects
    which have a 'title' key which corresponds to the 'label' of the
    taxonomy term.

    [{"title": "term1",
        "extra1", "value2",
        "extra2", "value2",
        ...},
        {"title": "term2",
        "extra1", "value2",
        "extra2", "value2",
        ...}]

    This file format has been adopted from the themes.json file used in
    data.gov.uk. As well as the 'title', key which is used to match up with
    the 'label' of the taxonomy term, the keys 'description' and
    'stored_as' are also removed from the object before storing it in the
    JSON extras field.
    """
    if not filename:
        logger.error("No FILENAME provided and it is required")
        logger.error(usage)
        return

    if not name:
        logger.error("No NAME provided and it is required")
        logger.error(usage)
        return

    from . import lib
    lib.load_term_extras(filename, taxonomy_name=name)
    logger.info('Extras loaded')


def get_commands():
    return [taxonomy]

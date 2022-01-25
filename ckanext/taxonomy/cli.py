import sys
import click
from logging import getLogger
from ckanext.taxonomy.commands import TaxonomyCommand

log = getLogger(__name__)

# Click commands for CKAN 2.9 and above

@click.group(short_help='Perform Tag Taxonomy related actions')
def taxonomy():
    """taxonomy commands
    """
    pass


@taxonomy.command()
def init():
    """Creates the database tables required.
    """
    cmd = TaxonomyCommand('init')
    cmd.init()

@taxonomy.command()
def cleanup():
    """Deletes the database tables required.
    """
    cmd = TaxonomyCommand('cleanup')
    cmd.cleanup()
    
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
    cmd = TaxonomyCommand('load-extras')
    cmd.load_extras(filename, name)

def get_commands():
    return [taxonomy]

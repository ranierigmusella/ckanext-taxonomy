import sys
import click
import rdflib
import skos
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
@click.option('--url'     , is_flag = False, default = False, help = "URL to a resource")
@click.option('--filename', is_flag = False, default = False, help = "Path to a file")
@click.option('--name'    , is_flag = False, default = False, help = "Name of the taxonomy to work with")
@click.option('--title'   , is_flag = False, default = False, help = "Title of the taxonomy")
@click.option('--lang'    , is_flag = False, default = False, help = "Language to use when retrieving labels")
@click.option('--uri'     , is_flag = False, default = False, help = "The URI of the taxonomy")
def load(url, filename, name, title, lang, uri):
    """Load a taxonomy
    """
    if not url and not filename:
        logger.error("No URL or FILENAME provided and one is required")
        logger.error(usage)
        return

    if not name:
        print("No NAME provided and it is required")
        logger.error(usage)
        return

    if not uri:
        logger.error("No URI provided and it is required")
        logger.error(usage)
        return

    logger.info("Loading graph")
    graph = rdflib.Graph()
    result = graph.parse(url or filename)
    loader = skos.RDFLoader(graph,
                            max_depth=float('inf'),
                            flat=True,
                            lang=lang)

    logger.info("Processing concepts")
    concepts = loader.getConcepts()

    top_level = []
    for _, v in concepts.items():
        if not v.broader:
            top_level.append(v)
    top_level.sort(key=lambda x: x.prefLabel)

    import ckan.model as model
    import ckan.logic as logic

    context = {'model': model, 'ignore_auth': True }

    try:
        current = logic.get_action('taxonomy_show')(
            context,
            {'id': name})
        logic.get_action('taxonomy_delete')(
            context,
            {'id': name})
    except logic.NotFound:
        pass

    tx = logic.get_action('taxonomy_create')(context, {
        'title': title or name,
        'name': name,
        'uri': uri
    })

    for t in top_level:
       _add_node(context, tx, t)
    logger.info('Load complete')

def _add_node(context, tx, node, parent=None, depth = 1):
    import ckan.logic as logic

    logger.debug(('   ' * depth) + node.prefLabel.encode('utf-8'))

    description = ''
    if hasattr(node, 'definition') and node.definition:
        description = node.definition.encode('utf-8')

    logger.debug(type(node))
    # rdfs:comment print dir(node)

    nd = logic.get_action('taxonomy_term_create')(context,  {
        'label': node.prefLabel.encode('utf-8'),
        'uri': node.uri,
        'description': description,
        'taxonomy_id': tx['id'],
        'parent_id': parent
    })
    node_id = nd['id']

    for _, child in node.narrower.items():
        _add_node(context, tx, child, node_id, depth + 1)

@taxonomy.command()
@click.argument(u'filename')
@click.argument(u'name')
def load_extras(filename, name):
    """Load extra information about the terms in the taxonomy
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

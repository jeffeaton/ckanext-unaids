# encoding: utf-8
import logging
import cStringIO
import json
from flask import Blueprint, Response, abort, request, jsonify
import ckan.plugins.toolkit as t
from ckanext.validation.jobs import _load_dataframe
from ckanext.validation.helpers import validation_load_schemed_table

log = logging.getLogger(__name__)

unaids_blueprint = Blueprint(
    u'unaids_blueprint',
    __name__,
    url_prefix=u'/validation'
)


def download_table_template(validation_schema):
    """
    Downloads a CSV template file for the specified validation schema.
    """
    try:
        format = request.args.get('format', 'csv')
        logging.warning(format)

        log.info('Fetching creating schema: ' + validation_schema)
        schema_directory = t.config['ckanext.validation.schema_directory']
        file_path = schema_directory + '/' + validation_schema + '.json'
        schemed_table = validation_load_schemed_table(file_path)
        template = schemed_table.create_template()

        if format == 'csv':
            csv_content = template.to_csv(
                header=False,
                index=False,
                encoding='utf-8'
            )
            return Response(
                csv_content,
                mimetype="text/csv",
                headers={"Content-disposition":
                         "attachment; filename=" + str(validation_schema) + ".csv"}
            )

        elif format == 'xls':
            template = template.iloc[1:]  # Remove headers
            out = cStringIO.StringIO()
            template.to_excel(out, columns=None, index=None)
            out.seek(0)
            return Response(
                out,
                mimetype="application/xls",
                headers={"Content-disposition":
                         "attachment; filename=" + str(validation_schema) + ".xls"}
            )

    except AttributeError as e:
        log.exception(e)
        abort(404, "404 Not Found Error: No schema exists for " + validation_schema)

    except Exception as e:
        log.exception(e)
        abort(
            500,
            "500 Internal server error: Something went wrong whilst "
            "generating your template " + validation_schema
        )


def download_naomi_geodata(package_id):
    # Get package metadata
    package = t.get_action('package_show')({}, {'id': package_id})

    for resource in package.get('resources', []):
        # Get resource data from the packages metadata.
        logging.warning("NAME: " + str(resource['name']) + "=======================")
        resource_id = resource['id']
        resource_format = resource.get('format', 'csv').lower()
        resource_path = "/".join([
            t.config.get('ckan.storage_path', '/var/lib/ckan'),
            'resources',
            resource_id[0:3],
            resource_id[3:6],
            resource_id[6:]
        ])

        # Safely load the resources as a pandas dataframe:
        df = _load_dataframe(resource_path, resource_format)
        logging.warning(df.head())

        # If json load the data as json file:
        if 'json' in resource_format:
            with open(resource_path, 'r') as json_file:
                json_data = json.load(json_file)
                logging.warning(
                    [x['properties']['area_id'] for x in json_data['features']]
                )

    return jsonify(package)


unaids_blueprint.add_url_rule(
    u'/geodata/<package_id>',
    view_func=download_naomi_geodata
)
unaids_blueprint.add_url_rule(
    u'/template/<validation_schema>',
    view_func=download_table_template
)

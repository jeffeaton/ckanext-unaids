# encoding: utf-8
import logging
from flask import Blueprint, Response, abort
from ckan.plugins.toolkit import config
from ckanext.validation.jobs import load_schema_from_path

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
        schema_directory = config['ckanext.validation.schema_directory']
        file_path = schema_directory + '/' + validation_schema + '.json'
        schemed_table = load_schema_from_path(file_path)
        template = schemed_table.create_template()
        csv_content = template.to_csv(header=False, index=False, encoding='utf-8')

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=" + str(validation_schema) + ".csv"}
        )

    except AttributeError as e:
        logging.error(e)
        abort(404, "404 Not Found Error: No schema exists for " + validation_schema)
    except Exception as e:
        logging.error(e)
        abort(
            500,
            "500 Internal server error: Something went wrong whilst "
            "generating your template " + validation_schema
        )


unaids_blueprint.add_url_rule(
    u'/template/<validation_schema>',
    view_func=download_table_template
)

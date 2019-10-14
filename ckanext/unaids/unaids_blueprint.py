# encoding: utf-8
import logging
import cStringIO
from flask import Blueprint, Response, abort, request
from ckan.plugins.toolkit import config
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
        schema_directory = config['ckanext.validation.schema_directory']
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


unaids_blueprint.add_url_rule(
    u'/template/<validation_schema>',
    view_func=download_table_template
)

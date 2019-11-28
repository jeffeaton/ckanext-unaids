# encoding: utf-8
import logging
import cStringIO
import json
import os
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
    package = t.get_action('package_show')({}, {'id': package_id})
    found_location_hierarchy = False
    found_area_geojson = False
    for resource in package.get('resources', []):
        if resource['name'] == u'Location Hierarchy':
            found_location_hierarchy = True
            resource_format = resource.get('format', 'csv').lower()
            resource_path = __get_resource_path(resource)
            location_hierarchy_df = _load_dataframe(resource_path, resource_format)
            location_hierarchy_df['area_sort_order'] = location_hierarchy_df['area_sort_order'].fillna('')
        elif resource['name'] == u'Regional Geometry':
            found_area_geojson = True
            resource_path = __get_resource_path(resource)
            with open(resource_path, 'r') as json_file:
                area_gejson = json.load(json_file)
    if found_area_geojson and found_location_hierarchy:
        for feature in area_gejson['features']:
            prop = feature['properties']
            area_id = prop['area_id']
            area_data = location_hierarchy_df.loc[area_id]
            for key in ['parent_area_id', 'area_sort_order']:
                prop[key] = area_data[key]
    else:
        raise RuntimeError("Failed to fetch proper geographic package resources")

    return jsonify(area_gejson)


def __get_resource_path(resource):
    resource_id = resource['id']
    resource_path = os.path.join(
        t.config.get('ckan.storage_path', '/var/lib/ckan'),
        'resources',
        resource_id[0:3],
        resource_id[3:6],
        resource_id[6:]
    )
    return resource_path


unaids_blueprint.add_url_rule(
    u'/geodata/<package_id>',
    view_func=download_naomi_geodata
)
unaids_blueprint.add_url_rule(
    u'/template/<validation_schema>',
    view_func=download_table_template
)

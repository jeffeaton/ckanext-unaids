import ckan.plugins as p
import logging
import licenses
import ckan.model.license as core_licenses
import ckan.model.package as package
import ckan.lib.uploader as uploader
import cgi
from ckan.plugins import toolkit
from collections import OrderedDict
from ckan.common import request

log = logging.getLogger(__name__)


def add_licenses():
    package.Package._license_register = core_licenses.LicenseRegister()
    package.Package._license_register.licenses = [
        core_licenses.License(
            licenses.LicenseCreativeCommonsIntergovernmentalOrgs()),
        core_licenses.License(
            core_licenses.LicenseNotSpecified())
        ]


class UNAIDSPlugin(p.SingletonPlugin):
    """
    This plugin implements the configurations needed for AIDS data exchange

    """

    p.implements(p.IConfigurer)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    # IConfigurer
    def update_config(self, config):
        '''
        This method allows to access and modify the CKAN configuration object
        '''
        add_licenses()
        log.info("UNAIDS Plugin is enabled")
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')

    def dataset_facets(self, facet_dict, package_type):
        new_fd = OrderedDict()
        new_fd['organization'] = p.toolkit._('Organizations')
        new_fd['dataset_type'] = p.toolkit._('Data Type')
        new_fd['tags'] = p.toolkit._('Tags')
        new_fd["year"] = p.toolkit._('Year')
        new_fd["geo-location"] = p.toolkit._('Location')
        return new_fd

    def organization_facets(self, facet_dict, org_type, package_type):

        return facet_dict

    def after_create(self, context, package_dict):
        logging.warning(package_dict)
        if package_dict.get('type', "") == 'spectrum-dataset':
            with open('/usr/lib/ckan/Mauritius_2018_shadow.PJNZ', 'rb') as f:
                upload = cgi.FieldStorage()
                upload.filename = getattr(f, 'name', 'data')
                upload.name = "spectrum_file"
                upload.file = f
                resource_dict = {
                    'package_id': package_dict['id'],
                    'url': package_dict['spectrum_file'],
                    'name': "Source Spectrum File",
                    'validator_schema': '',
                    'upload': upload
                }
                toolkit.get_action('resource_create')(context, resource_dict)

import ckan.plugins as p
import logging
import licenses
import ckan.model.license as core_licenses
import ckan.model.package as package
from unaids_blueprint import unaids_blueprint
from collections import OrderedDict
from ckan.lib.plugins import DefaultTranslation
from ckanext.unaids.helpers import get_logo_path

log = logging.getLogger(__name__)


def add_licenses():
    package.Package._license_register = core_licenses.LicenseRegister()
    package.Package._license_register.licenses = [
        core_licenses.License(
            licenses.LicenseCreativeCommonsIntergovernmentalOrgs()),
        core_licenses.License(
            core_licenses.LicenseNotSpecified())
        ]


class UNAIDSPlugin(p.SingletonPlugin, DefaultTranslation):
    """
    This plugin implements the configurations needed for AIDS data exchange

    """

    p.implements(p.IConfigurer)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IBlueprint)
    p.implements(p.ITranslation)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # IConfigurer
    def update_config(self, config):
        '''
        This method allows to access and modify the CKAN configuration object
        '''
        add_licenses()
        log.info("UNAIDS Plugin is enabled")
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')

    def get_blueprint(self):
        return unaids_blueprint

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

    # ITemplateHelpers
    def get_helpers(self):
        return {
            u'get_logo_path': get_logo_path
        }

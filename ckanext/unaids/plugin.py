import ckan.plugins as p
import logging
import licenses
import ckan.model.license as core_licenses
import ckan.model.package as package
from collections import OrderedDict

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
    p.implements(p.IFacets)

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
        log.warning(facet_dict)
        log.warning(package_type)

        new_fd = OrderedDict()

        new_fd['organization'] = p.toolkit._('Organizations')

        new_fd['dataset_type'] = p.toolkit._('Data Type')
        new_fd['tags'] = p.toolkit._('Tags')
        new_fd["year"] = p.toolkit._('Year')
        new_fd["geo-location"] = p.toolkit._('Location')
        return new_fd

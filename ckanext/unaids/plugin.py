import ckan.plugins as p
import logging
 
log = logging.getLogger(__name__)


class UNAIDSPlugin(p.SingletonPlugin):
    """
    This plugin implements a way to connect superset to a table in the datastore

    """
    
    p.implements(p.IConfigurer)
    
    # IConfigurer
    def update_config(self, config):
        '''
        This method allows to access and modify the CKAN configuration object
        '''
        log.info("UNAIDS Plugin is enabled")
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')

        

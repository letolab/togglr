# -*- coding: utf-8 -*-
import os

from flask.config import Config


class TogglrConfig(Config):

    """ A dict that provides access to all Togglr configuration values, and
    defines the environment variables used by Togglr. It allows both Flask
    settings and Togglr-specific settings to be defined in a single Python
    configuration file.

    The values in `TogglrConfig.env_vars` are configuration variables that
    Togglr uses. They can either be set directly as environment variables
    (which takes precedence), or they can be defined in a Python file along
    with any other Flask settings. This file should be specified in the
    environment variable 'TOGGLR_SETTINGS'.

    The dict keys/values should be added to the Flask app configuration, either
    manually or (if the Flask version allows) by using this class as the value
    for `Flask.config_class`.
    """

    env_vars = {
        'api_token': 'TOGGLR_TOGGL_API_TOKEN',
        'wsid':      'TOGGLR_TOGGL_WSID',
    }

    env_file_var = 'TOGGLR_SETTINGS'

    def __init__(self, *args, **kwargs):
        super(TogglrConfig, self).__init__(*args, **kwargs)

        self._load_from_file()
        self._load_from_direct_env_vars()

    def _load_from_file(self):
        if self.env_file_var in os.environ:
            self.from_envvar(self.env_file_var)

    def _load_from_direct_env_vars(self):
        for var in sorted(self.env_vars):
            if var in os.environ:
                self[var] = os.environ[var]

    def get_internal(self, key):
        """ Use key independent of the environment variable name. """
        return self.get(self.env_vars[key])

    def check_and_warn(self, logger=None):
        """ Print and log warnings if expected variables are missing """
        msgs = []
        for var in sorted(self.env_vars.itervalues()):
            if var not in self:
                msgs.append('Configuration variable not defined: %s' % var)

        # Print configuration problems to terminal, just in case app.logger is not
        # writing to stderr.
        if msgs:
            full_msg = "\n".join(msgs)
            if logger:
                logger.warning(full_msg)
            linebreak = "-" * 80
            print "\n".join([linebreak, 'WARNING:', full_msg, linebreak])

# This saves others files from having to create their own config instance.
TOGGLR_CONFIG = TogglrConfig(root_path=os.getcwd())

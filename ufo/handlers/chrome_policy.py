"""The module for generating and outputing chrome policy."""

import json

import flask

import ufo
from ufo.database import models


def _make_chrome_policy_json():
  """Generates the json string of chrome policy based on values in the db.

  This policy string has the following form:

  Returns:
    A json string of current chrome policy.
  """
  proxy_servers = models.ProxyServer.query.all()
  proxy_server_public_keys = [s.get_public_key_as_authorization_file_string() for s in proxy_servers]

  config = ufo.get_user_config()

  policy_dictionary = {
      "proxy_server_keys": proxy_server_public_keys,
      "enforce_proxy_server_validity": config.proxy_server_validity,
  }

  return json.dumps(policy_dictionary)

def _make_settings_json():
  """Generates the json string of all settings based on values in the db.

  Returns:
    A json string of current server settings.
  """
  config = ufo.get_user_config()

  settings_dictionary = {
      "enforce_network_jail": config.network_jail_until_google_auth,
      "enforce_proxy_server_validity": config.proxy_server_validity,
  }

  return json.dumps(settings_dictionary)


def get_policy_resources_dict():
  """Get the resources for the chrome policy component.

    Returns:
      A dict of the resources for the chrome policy component.
  """
  return {
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'isChromePolicy': True,
    'hasAddFlow': False,
    'policy_filename': 'chrome_policy.json',
    'titleText': 'Chrome Policy',
  }


def get_policy_configuration_resources_dict():
  """Get the resources for the chrome policy configuration component.

    Returns:
      A dict of the resources for the chrome policy configuration component.
  """
  return {
    'hasAddFlow': False,
    'titleText': 'Chrome Policy Configurations',
    'getSettingsUrl': flask.url_for('get_settings'),
    'editUrl': flask.url_for('edit_policy_config'),
    'proxyValidityText': 'Enforce Proxy Server Check from Invitation Link',
    'networkJailText': 'Enforce Network Jail Before Google Login',
    'saveText': 'Save',
  }


@ufo.app.route('/chromepolicy/')
@ufo.setup_required
def display_chrome_policy():
  """Renders the current chrome policy as json and editable values.

  Returns:
    The rendered chrom_policy.html template with policy values as variables.
  """
  policy_json = _make_chrome_policy_json()
  config = ufo.get_user_config()

  return flask.render_template(
      'chrome_policy.html', policy_json=policy_json,
      enforce_proxy_server_validity=config.proxy_server_validity,
      enforce_network_jail=config.network_jail_until_google_auth)


@ufo.app.route('/settings/', methods=['GET'])
@ufo.setup_required
def get_settings():
  """Gets the current settings as a json object.

  Returns:
    A flask response with the json settings.
  """
  return flask.Response(_make_settings_json(), mimetype='application/json')


@ufo.app.route('/chromepolicy/download/')
@ufo.setup_required
def download_chrome_policy():
  """Outputs the managed chrome policy in json form for downloading as a file.

  Returns:
    A json file of the current managed chrome policy.
  """
  return flask.Response(_make_chrome_policy_json(),
                        mimetype='application/json')

@ufo.app.route('/chromepolicy/edit', methods=['POST'])
@ufo.setup_required
def edit_policy_config():
  """Receives the posted form for editing the policy config values.

  The new policy config values are stored in the database.

  Returns:
    A redirect back to display chrome policy with will display the new values.
  """
  # TODO(eholder): Move the display of config values and the edit handlers to
  # something more sensible once UI review tells us what that should be. I'm
  # envisioning a settings or options page which is underneath the overall
  # Setup link. For now, I just want these settings to be edittable somewhere.

  config = ufo.get_user_config()

  proxy_server_string = flask.request.form.get('enforce_proxy_server_validity')
  network_jail_string = flask.request.form.get('enforce_network_jail')
  config.proxy_server_validity = json.loads(proxy_server_string)
  config.network_jail_until_google_auth = json.loads(network_jail_string)

  config.save()

  return flask.redirect(flask.url_for('get_settings'))

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SHIB_ATTRIBUTE_MAP = settings.SHIBBOLETH_ATTRIBUTE_MAP

# Set to true if you are testing and want to insert sample headers.
SHIB_MOCK_HEADERS = getattr(settings, 'SHIBBOLETH_MOCK_HEADERS', False)

# This list of attributes will map to Django permission groups
GROUP_ATTRIBUTES = getattr(settings, 'SHIBBOLETH_GROUP_ATTRIBUTES', [])

# If a group attribute is actually a list of groups, define the
# delimiters used to split the list
GROUP_DELIMITERS = getattr(settings, 'SHIBBOLETH_GROUP_DELIMITERS', [';'])
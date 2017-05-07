from __future__ import unicode_literals

import contextlib

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework_simplejwt.settings import api_settings


def client_action_wrapper(action):
    def wrapper_method(self, *args, **kwargs):
        if self.view_name is None:
            raise ValueError('Must give value for `view_name` property')

        reverse_args = kwargs.pop('reverse_args', tuple())
        reverse_kwargs = kwargs.pop('reverse_kwargs', dict())
        query_string = kwargs.pop('query_string', None)

        url = reverse(self.view_name, args=reverse_args, kwargs=reverse_kwargs)
        if query_string is not None:
            url = url + '?{0}'.format(query_string)

        return getattr(self.client, action)(url, *args, **kwargs)

    return wrapper_method


class APIClientTestCaseMixin(object):
    def setUp(self):
        super(APIClientTestCaseMixin, self).setUp()

        self.client = APIClient()

    def authenticate_with_user(self, user):
        """
        Authenticates requests with the given user's token.
        """
        self.authenticate_with_token(Token.objects.get(user=user))

    def authenticate_with_token(self, token):
        """
        Authenticates requests with the given token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    view_name = None

    view_post = client_action_wrapper('post')
    view_patch = client_action_wrapper('patch')
    view_get = client_action_wrapper('get')


class APIViewTestCase(APIClientTestCaseMixin, TestCase):
    pass


@contextlib.contextmanager
def override_api_settings(**settings):
    for k, v in settings.items():
        setattr(api_settings, k, v)

    yield

    for k in settings.keys():
        delattr(api_settings, k)
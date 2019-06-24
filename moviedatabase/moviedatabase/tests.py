import random
import string

from django.http import Http404
from django.test import TestCase

from . import views


NOT_FOUND_MOVIE_TITLE = ''.join(random.choices(
    string.ascii_letters + string.digits, k=50))
ONEWORD_MOVIE_TITLE = 'Deadpool'
MULTIWORD_MOVIE_TITLE = 'Back to the Future'


class ExternalApiTests(TestCase):
    def test_no_api_key(self):
        self.assertRaises(
            Http404, views.get_details_from_external_api, '', api_key='')

    def test_invalid_api_key(self):
        self.assertRaises(
            Http404, views.get_details_from_external_api, '', api_key='spam egg ham')

    def test_empty_title(self):
        self.assertRaises(
            Http404, views.get_details_from_external_api, '')

    def test_movie_not_found(self):
        self.assertRaises(
            Http404, views.get_details_from_external_api, NOT_FOUND_MOVIE_TITLE)

    def _helper_test_movie_found(self, title):
        details = views.get_details_from_external_api(title)
        self.assertIsInstance(details, dict)
        self.assertNotEqual(details, {})

    def test_oneword_movie_found(self):
        self._helper_test_movie_found(ONEWORD_MOVIE_TITLE)

    def test_multiword_movie_found(self):
        self._helper_test_movie_found(MULTIWORD_MOVIE_TITLE)

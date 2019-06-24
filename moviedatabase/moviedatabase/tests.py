import random
import string

from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from . import views
from .models import Movie


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


class MoviesViewTests(TestCase):
    def _get_all_movies(self):
        return self.client.get(reverse('movies'))

    def test_no_movies(self):
        response = self._get_all_movies()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_post_no_title(self):
        response = self.client.post(reverse('movies'))
        self.assertEqual(response.status_code, 400)

    def test_post_empty_title(self):
        response = self.client.post(reverse('movies'), {'title': ''})
        self.assertEqual(response.status_code, 404)

    def test_post_movie_not_found(self):
        response = self.client.post(
            reverse('movies'), {'title': NOT_FOUND_MOVIE_TITLE})
        self.assertEqual(response.status_code, 404)

    def _post_movie(self, title):
        return self.client.post(reverse('movies'), {'title': title})

    def test_post_saves_to_database(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        movie = Movie.objects.last()
        self.assertEqual(ONEWORD_MOVIE_TITLE, movie.title)
        self.assertIsInstance(movie.details, dict)
        self.assertNotEqual(movie.details, {})

    def test_post_response(self):
        response = self._post_movie(ONEWORD_MOVIE_TITLE)
        movie_id = Movie.objects.last().pk
        # Fetched `movie_id` instead of hardcoded `1`, because it seems Django
        # does not completely reset database to its initial state at the
        # beginning of each test.
        # It is possible that reason of this is described in the 'Warning':
        # https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.TransactionTestCase
        expected_url = reverse('filtered_movies', args=(movie_id,))
        self.assertRedirects(response, expected_url)

        response = self.client.get(expected_url)
        self.assertContains(response, f'"title": "{ONEWORD_MOVIE_TITLE}"')
        self.assertContains(response, '"details":')

    def test_get_all(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        self._post_movie(MULTIWORD_MOVIE_TITLE)
        response = self._get_all_movies()
        self.assertContains(response, ONEWORD_MOVIE_TITLE)
        self.assertContains(response, MULTIWORD_MOVIE_TITLE)

import random
import string

from unittest import mock

from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import (
    Comment,
    Movie,
)


NOT_FOUND_MOVIE_TITLE = ''.join(random.choices(
    string.ascii_letters + string.digits, k=50))
ONEWORD_MOVIE_TITLE = 'Deadpool'
MULTIWORD_MOVIE_TITLE = 'Back to the Future'

EXAMPLE_NON_EMPTY_COMMENT = 'Great movie, 5/7.'


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

    def _test_movie_found(self, title):
        details = views.get_details_from_external_api(title)
        self.assertIsInstance(details, dict)
        self.assertNotEqual(details, {})

    def test_oneword_movie_found(self):
        self._test_movie_found(ONEWORD_MOVIE_TITLE)

    def test_multiword_movie_found(self):
        self._test_movie_found(MULTIWORD_MOVIE_TITLE)


class MovieDatabaseViewTestCase(TestCase):
    def _post_movie(self, title):
        return self.client.post(reverse('movies'), {'title': title})

    def _post_comment_to_last_movie(self, text):
        movie = Movie.objects.last()
        response = self.client.post(
            reverse('comments'),
            {'movie_id': movie.pk, 'text': text}
        )
        return movie, response

    def _post_three_comments_with_mocked_datetime(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        mocked_datetimes = [
            timezone.datetime(
                2017, 1, 1, tzinfo=timezone.get_current_timezone()),
            timezone.datetime(
                2018, 1, 1, tzinfo=timezone.get_current_timezone()),
            timezone.datetime(
                2019, 1, 1, tzinfo=timezone.get_current_timezone()),
        ]
        for mocked in mocked_datetimes:
            with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
                self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        return mocked_datetimes


class MoviesViewTests(MovieDatabaseViewTestCase):
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


class CommentsViewTests(MovieDatabaseViewTestCase):
    def _get_all_comments(self):
        return self.client.get(reverse('comments'))

    def test_no_comments(self):
        response = self._get_all_comments()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_post_no_movie_id_and_text(self):
        response = self.client.post(reverse('comments'))
        self.assertEqual(response.status_code, 400)

    def test_post_no_movie_id(self):
        response = self.client.post(
            reverse('comments'), {'text': EXAMPLE_NON_EMPTY_COMMENT})
        self.assertEqual(response.status_code, 400)

    def test_post_no_text(self):
        response = self.client.post(reverse('comments'), {'movie_id': 1})
        self.assertEqual(response.status_code, 400)

    def test_post_empty_text(self):
        response = self.client.post(
            reverse('comments'), {'movie_id': 1, 'text': ''})
        self.assertEqual(response.status_code, 400)

    def test_post_movie_not_found(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        movie = Movie.objects.last()
        response = self.client.post(
            reverse('comments'),
            {'movie_id': movie.pk + 1, 'text': EXAMPLE_NON_EMPTY_COMMENT}
        )
        self.assertEqual(response.status_code, 404)

    def test_post_saves_to_database(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        movie, _ = self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        comment = Comment.objects.last()
        self.assertEqual(comment.movie_id, movie)
        self.assertEqual(comment.text, EXAMPLE_NON_EMPTY_COMMENT)
        self.assertAlmostEqual(comment.added, timezone.now(),
                               delta=timezone.timedelta(minutes=1))

    def test_post_response(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        movie, response = self._post_comment_to_last_movie(
            EXAMPLE_NON_EMPTY_COMMENT)
        comment_id = Comment.objects.last().pk
        expected_url = reverse('filtered_comments', args=(comment_id,))
        self.assertRedirects(response, expected_url)

        response = self.client.get(expected_url)
        self.assertContains(response, f'"movie_id": {movie.pk}')
        self.assertContains(response, f'"text": "{EXAMPLE_NON_EMPTY_COMMENT}"')
        self.assertContains(response, '"added":')

    def test_get_all(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        self._post_movie(MULTIWORD_MOVIE_TITLE)
        self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        response = self._get_all_comments()
        self.assertContains(response, EXAMPLE_NON_EMPTY_COMMENT, count=2)

    def test_get_all_for_specific_movie(self):
        self._post_movie(ONEWORD_MOVIE_TITLE)
        self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        self._post_movie(MULTIWORD_MOVIE_TITLE)
        movie, _ = self._post_comment_to_last_movie(EXAMPLE_NON_EMPTY_COMMENT)
        response = self.client.get(reverse('comments'), {'movie_id': movie.pk})
        self.assertContains(response, EXAMPLE_NON_EMPTY_COMMENT, count=1)


class CommentsInDatetimeRangeTests(MovieDatabaseViewTestCase):
    def test_all_in_range(self):
        mocked_datetimes = self._post_three_comments_with_mocked_datetime()
        comments = views.get_comments_in_datetime_range(
            mocked_datetimes[0],
            mocked_datetimes[-1]
        )
        self.assertEqual(len(comments), Comment.objects.count())

    def test_start_equals_end(self):
        mocked_datetimes = self._post_three_comments_with_mocked_datetime()
        start = end = random.choice(mocked_datetimes)
        comments = views.get_comments_in_datetime_range(
            start,
            end,
        )
        self.assertEqual(len(comments), 1)

    def test_none_in_range(self):
        mocked_datetimes = self._post_three_comments_with_mocked_datetime()
        start = end = mocked_datetimes[0] - timezone.timedelta(seconds=1)
        comments = views.get_comments_in_datetime_range(
            start,
            end,
        )
        self.assertEqual(len(comments), 0)

    def test_two_in_range(self):
        mocked_datetimes = self._post_three_comments_with_mocked_datetime()
        comments = views.get_comments_in_datetime_range(
            mocked_datetimes[0],
            mocked_datetimes[1],
        )
        self.assertEqual(len(comments), 2)

import json

from collections import Counter

import requests

from django.conf import settings
from django.core import serializers
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .models import (
    Comment,
    Movie,
)


def get_details_from_external_api(title, api_key=settings.OMDB_API_KEY):
    response = requests.get(settings.OMDB_API_URL, params={
        'apikey': api_key,
        't': title,
    })
    details = json.loads(response.content)
    if details['Response'] == 'True':
        return details
    raise Http404(details['Error'])


class FilteredMoviesView(View):
    def get(self, request, *args, **kwargs):
        movies = Movie.objects.filter(pk=kwargs['movie_id'])
        movies = serializers.serialize('json', movies)
        return HttpResponse(movies)


class MoviesView(View):
    def get(self, request, *args, **kwargs):
        movies = Movie.objects.all()
        movies = serializers.serialize('json', movies)
        return HttpResponse(movies)

    def post(self, request, *args, **kwargs):
        try:
            title = request.POST['title']
        except KeyError:
            return HttpResponseBadRequest()
        else:
            details = get_details_from_external_api(title)
            movie = Movie.objects.create(title=title, details=details)
            return HttpResponseRedirect(reverse('filtered_movies', args=(movie.id,)))


class FilteredCommentsView(View):
    def get(self, request, *args, **kwargs):
        comments = Comment.objects.filter(pk=kwargs['comment_id'])
        comments = serializers.serialize('json', comments)
        return HttpResponse(comments)


class CommentsView(View):
    def get(self, request, *args, **kwargs):
        movie_id = request.GET.get('movie_id')
        if movie_id:
            comments = Comment.objects.filter(movie_id=movie_id)
        else:
            comments = Comment.objects.all()
        comments = serializers.serialize('json', comments)
        return HttpResponse(comments)

    def post(self, request, *args, **kwargs):
        try:
            movie_id = request.POST['movie_id']
            text = request.POST['text']
            if not text:
                raise ValueError('`text` must not be empty')
        except (KeyError, ValueError):
            return HttpResponseBadRequest()
        else:
            movie = get_object_or_404(Movie, pk=movie_id)
            comment = Comment.objects.create(movie_id=movie, text=text)
            return HttpResponseRedirect(reverse('filtered_comments', args=(comment.id,)))


def get_comments_in_datetime_range(start, end):
    return Comment.objects.filter(added__gte=start, added__lte=end)


class TopView(View):
    def get(self, request, *args, **kwargs):
        try:
            start_timestamp = int(request.GET['start_timestamp'])
            end_timestamp = int(request.GET['end_timestamp'])
        except (KeyError, ValueError):
            return HttpResponseBadRequest()
        else:
            comments = get_comments_in_datetime_range(
                timezone.datetime.fromtimestamp(
                    start_timestamp, tz=timezone.get_current_timezone()),
                timezone.datetime.fromtimestamp(
                    end_timestamp, tz=timezone.get_current_timezone()),
            )

            total_comments_by_movie_id = Counter()
            for comment in comments:
                total_comments_by_movie_id[comment.movie_id.pk] += 1
            # Specification requires that movies without any comments must be
            # included in the ranking
            for movie in Movie.objects.exclude(comment__in=comments):
                total_comments_by_movie_id[movie.pk] = 0

            position_by_total_comments = {k: v for v, k in enumerate(
                sorted(set(total_comments_by_movie_id.values()), reverse=True),
                start=1)}

            top = [{'movie_id': m,
                    'total_comments': c,
                    'rank': position_by_total_comments[c]}
                   for m, c in total_comments_by_movie_id.most_common()]

            return JsonResponse(top, safe=False)

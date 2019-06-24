import json

import requests

from django.conf import settings
from django.core import serializers
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
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

import json

import requests

from django.conf import settings
from django.core import serializers
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect
)
from django.urls import reverse
from django.views import View

from .models import Movie


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

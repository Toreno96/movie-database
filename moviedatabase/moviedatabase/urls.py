from django.urls import include, path

from . import views

urlpatterns = [
    path('movies/', include([
        path('', views.MoviesView.as_view(), name='movies'),
        path('<int:movie_id>/', views.FilteredMoviesView.as_view(),
             name='filtered_movies'),
    ])),
    path('comments/', include([
        path('', views.CommentsView.as_view(), name='comments'),
        path('<int:comment_id>/', views.FilteredCommentsView.as_view(),
             name='filtered_comments'),
    ])),
]

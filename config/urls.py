from django.contrib import admin

from django.conf import settings

from django.conf.urls.static import static

from django.urls import (
    include,
    path
)

from django.views.generic import RedirectView


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        RedirectView.as_view(
            pattern_name=
                'accounts:dashboard',
            permanent=False
        )
    ),

    path(
        '',
        include(
            'accounts.urls'
        )
    ),

    path(
        'notices/',
        include(
            'notices.urls'
        )
    ),

    path(
        'api/',
        include(
            'api.urls'
        )
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


handler400 = (
    'accounts.views.error_400'
)

handler403 = (
    'accounts.views.error_403'
)

handler404 = (
    'accounts.views.error_404'
)

handler500 = (
    'accounts.views.error_500'
)
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import response
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.mobile.serializers import common as api_serializers
from geotrek.flatpages.models import FlatPage
from geotrek.trekking.models import DifficultyLevel, Practice, Accessibility, Route, Theme, TrekNetwork
from geotrek.tourism.models import InformationDesk
from geotrek.zoning.models import City


class SettingsView(APIView):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        return response.Response({
            'filters': [
                {
                    "id": "difficulty",
                    "type": "contains"
                },
                {
                    "id": "lengths",
                    "type": "interval"
                },
                {
                    "id": "cities",
                    "type": "contains"
                },
                {
                    "id": "accessibilities",
                    "type": "contains"
                },
                {
                    "id": "practice",
                    "type": "contains"
                },
                {
                    "id": "durations",
                    "type": "interval"
                },
                {
                    "id": "themes",
                    "type": "contains"
                },
                {
                    "id": "route",
                    "type": "contains"
                }
            ],
            'data': [
                {
                    'id': 'length',
                    'name': _('Length'),
                    'values': [
                        {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
                        {"id": 2, "name": "10 - 30", "interval": [9999, 29999]},
                        {"id": 3, "name": "30 - 50", "interval": [30000, 50000]},
                        {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
                    ]

                },
                {
                    'id': 'duration',
                    'name': _('Duration'),
                    'values': [
                        {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
                        {"id": 2, "name": "1h - 2h30", "interval": [1, 2.5]},
                        {"id": 3, "name": "2h30 - 5h", "interval": [2.5, 5]},
                        {"id": 4, "name": "5h - 9h", "interval": [5, 9]},
                        {"id": 5, "name": "> 9h", "interval": [9, 9999999]}
                    ]

                },
                {
                    'id': 'difficulty',
                    'name': _('Difficulty'),
                    'values': api_serializers.DifficultySerializer(DifficultyLevel.objects.all().order_by('pk'),
                                                                   many=True,
                                                                   context={'request': request}).data
                },
                {
                    'id': 'practice',
                    'name': _('Practice'),
                    'values': api_serializers.PracticeSerializer(Practice.objects.all().order_by('pk'),
                                                                 many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'accessibilities',
                    'name': _('Accessibilities'),
                    'values': api_serializers.PracticeSerializer(Accessibility.objects.all().order_by('pk'), many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'route',
                    'name': _('Route'),
                    'values': api_serializers.RouteSerializer(Route.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'themes',
                    'name': _('Themes'),
                    'values': api_serializers.ThemeSerializer(Theme.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'networks',
                    'name': _('Networks'),
                    'values': api_serializers.NetworkSerializer(TrekNetwork.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'information_desks',
                    'name': _('Information Desks'),
                    'values': api_serializers.InformationDeskSerializer(InformationDesk.objects.all().order_by('pk'),
                                                                        many=True,
                                                                        context={'request': request}).data,
                },
                {
                    'id': 'cities',
                    'name': _('Cities'),
                    'values': api_serializers.CitySerializer(City.objects.all().order_by('pk'), many=True,
                                                             context={'request': request}).data
                }
            ]
        })


class FlatPageViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = api_serializers.FlatPageListSerializer
    serializer_detail_class = api_serializers.FlatPageDetailSerializer
    queryset = FlatPage.objects.all().order_by('pk')

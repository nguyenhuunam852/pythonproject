

from rest_framework import serializers
from .models import Urlspage


class PageSerializer(serializers.ModelSerializer):
  class Meta:
    model = Urlspage
    fields = ('id', 'name', 'is_valid', 'created_at')
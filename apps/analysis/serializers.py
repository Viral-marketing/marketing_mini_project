from rest_framework import serializers

from apps.analysis.models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            "user",
            "type",
            "description",
            "period_start",
            "period_end",
            "result_image",
            "result_json",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "description",
            "result_image",
            "result_json",
            "created_at",
            "updated_at",
        ]

class AnalysisPostSerializer(AnalysisSerializer):
    class Meta(AnalysisSerializer.Meta):
        fields=["about","period_start","period_end"]
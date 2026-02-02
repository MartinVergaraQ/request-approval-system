from rest_framework import serializers
from .models import Request, RequestHistory


class RequestHistorySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = RequestHistory
        fields = ["id", "action", "note", "actor_username", "created_at"]


class RequestSerializer(serializers.ModelSerializer):
    history = RequestHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "title",
            "amount",
            "description",
            "status",
            "created_by",
            "approver",
            "created_at",
            "updated_at",
            "history",
        ]
        read_only_fields = ["status", "created_by", "created_at", "updated_at"]

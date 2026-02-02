from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Request, RequestHistory, RequestStatus
from .serializers import RequestSerializer


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Request.objects.filter(created_by=user) | Request.objects.filter(approver=user)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return qs.distinct().order_by("-created_at")

    def perform_create(self, serializer):
        req = serializer.save(created_by=self.request.user)
        RequestHistory.objects.create(request=req, action="CREATE", actor=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        req = self.get_object()
        if req.status != RequestStatus.DRAFT:
            return Response({"detail": "Solo BORRADOR se puede enviar."}, status=400)
        if not req.approver:
            return Response({"detail": "Debes asignar un aprobador antes de enviar."}, status=400)

        req.status = RequestStatus.SUBMITTED
        req.save(update_fields=["status"])
        RequestHistory.objects.create(request=req, action="SUBMIT", actor=request.user)
        return Response(RequestSerializer(req).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        req = self.get_object()
        if req.status != RequestStatus.SUBMITTED:
            return Response({"detail": "Solo ENVIADA se puede aprobar."}, status=400)

        # MVP: si hay approver asignado, solo ese usuario puede aprobar
        if req.approver and req.approver_id != request.user.id:
            return Response({"detail": "No eres el aprobador asignado."}, status=403)
        if not req.approver:
            return Response({"detail": "La solicitud no tiene aprobador asignado."}, status=400)

        req.status = RequestStatus.APPROVED
        req.save(update_fields=["status"])
        RequestHistory.objects.create(request=req, action="APPROVE", actor=request.user)
        return Response(RequestSerializer(req).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        req = self.get_object()
        note = (request.data.get("note") or "").strip()

        if req.status != RequestStatus.SUBMITTED:
            return Response({"detail": "Solo ENVIADA se puede rechazar."}, status=400)
        if not note:
            return Response({"detail": "El rechazo requiere motivo."}, status=400)
        if req.approver and req.approver_id != request.user.id:
            return Response({"detail": "No eres el aprobador asignado."}, status=403)

        req.status = RequestStatus.REJECTED
        req.save(update_fields=["status"])
        RequestHistory.objects.create(request=req, action="REJECT", actor=request.user, note=note)
        return Response(RequestSerializer(req).data)

    def update(self, request, *args, **kwargs):
        req = self.get_object()
        if req.status != RequestStatus.DRAFT:
            return Response({"detail": "Solo BORRADOR se puede editar."}, status=400)
        if req.created_by_id != request.user.id:
            return Response({"detail": "Solo el creador puede editar."}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

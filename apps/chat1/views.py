import json
from datetime import datetime

from apps.api.views import BestPraticsList
from apps.chat1.models import Messages
from apps.service_core.models import Attendance
from apps.professional.models import Professional
from apps.customer.models import Customer
from apps.service_core.views import Notification
from apps.message_core.models import PushToken

from . import serializers

from django.contrib.auth.models import User
from django.db import models
from django.http import QueryDict

from rest_framework.views import APIView, Response
from rest_framework import filters, generics, pagination, status
from rest_framework.response import Response


class MessangerList(BestPraticsList, generics.ListCreateAPIView):
    """
    Lists the Messages for the current Customer or Professional in either App, filtering by their id
    """
    serializer_class = serializers.MessageSerializer

    def post(self, request, *args, **kwargs):
        query_params = self.request.query_params
        attendance_id = query_params.get('attendance', None)
        attendance = Attendance.objects.filter(pk=attendance_id)
        if not attendance.exists():
            return Response({'status': 'NOT_FOUND'}, status.HTTP_404_NOT_FOUND)

        attendance = attendance[0]
        customer = Customer.objects.filter(id=attendance.customer_id)
        professional = Professional.objects.filter(id=attendance.professional_id)
        to = None
        if (customer.exists() and len(customer) > 0 and customer[0].user_id == self.request.user.id):
            to = professional[0]

        elif (professional.exists() and len(professional) > 0 and professional[0].user_id == self.request.user.id):
            to = customer[0]

        if to == None:
            return Response({'status': 'UNAUTHORIZED'}, status.HTTP_401_UNAUTHORIZED)

        model = Messages()
        model.attendance = attendance
        model.user = self.request.user
        model.date = datetime.now()
        model.message = request.data["message"]
        model.save()

        push_tokens = PushToken.objects.filter(user_id=to.user_id)
        notification = Notification()
        if push_tokens:
            for push_token in push_tokens:
                notification.push(
                    data={'type': 'chat1', 'attendance_id': attendance_id},
                    to=push_token.token,
                    title='Biuri',
                    body=request.data['message']
                )


        return Response()



    def get_queryset(self):
        #message_error = {}
        query_params = self.request.query_params
        attendance_id = query_params.get('attendance', None)
        last_updated = query_params.get('last_updated', None)
        last_updated = datetime.strptime(last_updated,"%Y-%m-%dT%H:%M:%S.%f" )
        attendance = Attendance.objects.filter(id=attendance_id)
        # if not attendance.exists():
        #     message_error['status'] = 'HTTP_404_NOT_FOUND'
        #     return Response(message_error, status.HTTP_404_NOT_FOUND)
        attendance = attendance[0]
        customer = Customer.objects.filter(id=attendance.customer_id)
        professional = Professional.objects.filter(id=attendance.professional_id)
        if (customer.exists() and len(customer) > 0 and customer[0].user_id == self.request.user.id) or\
         (professional.exists() and len(professional) > 0 and professional[0].user_id == self.request.user.id):
            message = Messages.objects.filter(attendance_id=attendance_id, date__gt=last_updated)
            return message

        # message_error['status'] = 'HTTP_401_UNAUTHORIZED'
        # return Response(message_error, status.HTTP_401_UNAUTHORIZED)

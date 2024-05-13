from django.db import models
import datetime, random, string, uuid

from django.db import models, IntegrityError
from django.db.models import Sum, Q
from django.contrib.auth.models import User

from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from simple_history.models import HistoricalRecords

from apps.common.models import BestPraticesModel, UserAddress

class Messages(BestPraticesModel):
    """
    Model for Messages object
    """

    attendance = models.ForeignKey('service_core.Attendance', null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(null=False)
    message = models.TextField(null=False, blank=True)

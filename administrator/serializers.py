from rest_framework import serializers
from .models import EnrollmentConfirmation
from django.utils.timezone import now
from homepage.models import System_users
import calendar

class EnrollmentStatsSerializer(serializers.Serializer):
    labels = serializers.ListField()
    data = serializers.ListField()

    @staticmethod
    def get_monthly_enrollment_percentage():
        current_year = now().year
        months = [calendar.month_abbr[i] for i in range(1, 13)]
        enrollments_percentage = []

        total_students = System_users.objects.filter(userrole="Student", is_active=True).count()

        for month in range(1, 13):
            enrolled_count = EnrollmentConfirmation.objects.filter(
                status='Approve',
                date_updated__year=current_year,
                date_updated__month=month
            ).count()

            percentage = (enrolled_count / total_students * 100) if total_students > 0 else 0
            enrollments_percentage.append(round(percentage, 2))

        return {"labels": months, "data": enrollments_percentage}


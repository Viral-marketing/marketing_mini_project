from django.core.mail import send_mail
from django.conf import settings
import json

class SendCustomEmail:
    @staticmethod
    def send_analysis(user,data,subject):
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        message = f"{formatted_data}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user['email']]
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )

    @staticmethod
    def send_analysis_for_spending(user,data):
        subject = "요청하신 소비분석 결과입니다."
        SendCustomEmail.send_analysis(user,data,subject)

    @staticmethod
    def send_analysis_for_income(user,data):
        subject = "요청하신 수입 분석 결과입니다."
        SendCustomEmail.send_analysis(user, data, subject)

    @staticmethod
    def send_analysis_daily_spending(user,data):
        subject = "[일간] 소비 분석 결과입니다."
        SendCustomEmail.send_analysis(user, data, subject)

    @staticmethod
    def send_analysis_daily_income(user,data):
        subject = "[일간] 수입 분석 결과 입니다."
        SendCustomEmail.send_analysis(user, data, subject)
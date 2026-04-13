import json

from django.conf import settings
from django.core.mail import send_mail


class SendCustomEmail:
    @staticmethod
    def send_analysis(user, data, subject):
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        message = f"{formatted_data}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user["email"]]
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
            # 만일 하나의 요청이 실패했을때 무시할지 안할지를 정함
        #     만일 False로 하면 하나의 요청이 실패하면 백그라운드 요청 전체 종료
        #     만일 True로 하면 실패한 요청은 무시하고 다음 요청 진행
        )

    @staticmethod
    def send_analysis_for_spending(user, data):
        subject = "요청하신 소비분석 결과입니다."
        SendCustomEmail.send_analysis(user, data, subject)

    @staticmethod
    def send_analysis_for_income(user, data):
        subject = "요청하신 수입 분석 결과입니다."
        SendCustomEmail.send_analysis(user, data, subject)

    @staticmethod
    def send_analysis_daily_spending(user, data):
        subject = "[일간] 소비 분석 결과입니다."
        SendCustomEmail.send_analysis(user, data, subject)

    @staticmethod
    def send_analysis_daily_income(user, data):
        subject = "[일간] 수입 분석 결과 입니다."
        SendCustomEmail.send_analysis(user, data, subject)

import io # 사진(이미지)을 하드에 저장하지 않고 메모리에 잠시 담아두는 바구니 역할
from django.utils import timezone

from matplotlib import pyplot as plt # 그래프를 그리는 스케피북 도구
import pandas as pd # 데이터를 표 형태로 요약해주는 라이브러리

from celery import shared_task # 데코레이터로 해당 함수를 celery_worker의 작업으로 인식됨
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from apps.analysis.models import Analysis
from apps.transactions.models import Transaction



@shared_task
def process_spending_analysis(user_email,user_id,data):
    """
    1. 데이터 분석 (Pandas)
    2. 시각화 이미지 생성 (Matplotlib)
    3. Analysis 모델에 이미지 저장
    4. 이메일 알림 전송(send_mail)
    """

    plt.switch_backend('Agg') # celery_worker서버에는 GUI가 없으니 추가한 설정
    # plt.rc("font",family="NanumBarunGothic") # 한글 폰트 설정 필요 시
    queryset = Transaction.objects.filter(
        user_id=user_id,
        created_at__range=[data['period_start'],data['period_end']],
        # Django의 queryset 필터 문법(컬럼명 뒤에 __두개 붙어셔 필터링 옵션 추가
    )
    # 기본
    if not queryset.exists():
        return "No data"

    df = pd.DataFrame(list(queryset.values('transaction_type','transaction_amount')))

    summary = df.groupby('transaction_type')['transaction_amount'].sum()

    plt.figure(figsize=(8,6))
    summary.plot(kind='pie',autopct='%1.1f%%',startangle=140)
    plt.title('spending report')
    plt.ylabel('')

    buffer = io.BytesIO()
    plt.savefig(buffer,format='png')
    image_data = buffer.getvalue()

    type = data['type']
    about = data['about']
    period_start = data['period_start']
    period_end = data['period_end']

    analysis = Analysis.objects.create(
        user_id=user_id,
        type=type,
        about=about,
        description=f"{user_email}님의 분석",
        period_start=period_start,
        period_end=period_end,
    )
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{user_id}_{timestamp}.png"
    analysis.result_image.save(filename,ContentFile(image_data))

    email = EmailMessage(
        subject="[가계부] 분석리포트가 도착했습니다",
        body="그래프를 확인해보세요",
        to=[user_email]
    )
    email.attach('report.png',image_data,'image/png')
    email.send()

    plt.close()
    return f"Task completed for {user_email}"
    ##########################################################################
    # # [1] 서버환경을 위한 Matplotlib 설정 (GUI 에러 방지)
    # plt.switch_backend("Agg")
    # # [2] 데이터 분석 (예시 :카테고리별 합계)
    # # df = pd.DataFrame(list(Transaction.objects.filter(user_id=user_id).values()))
    # # analysis_data = df.groupby("category)["amount"].sum()
    #
    # # 테스트용 가상데이터
    # labels = ["식비","교통","쇼핑","기타"]
    # values = [300000,50000,150000,20000]
    #
    # # [3]시각화 이미지 생성
    # plt.figure(figsize=(6,6))
    # plt.pie(values, labels=labels,autopct="%1.1f%%",startingle=140)
    # plt.title(f"{timezone.now().strftime("%Y-%m")} 지출 분석 리포트")
    #
    # # [4] 메모리에 이미지 저장 및 Analysis 모델 업데이트
    # buffer = io.BytesIO()
    # plt.savefig(buffer,format="png")
    # content_file  = ContentFile(buffer.getvalue())
    #
    # # Analysis 모델 인스턴스 생성 및 이미지 필드 저장
    # # analysis_obj = Analysis.objects.filter(user_id=user_id)
    # # analysis_obj.image(f"analysis_{user_id}_{timezone.now().date()}.png", content_file)
    #
    # # [5] 이메일 알림 전송
    # email = EmailMessage(
    #     subject = f"[가계부] {timezone.now().month}월 소비 분석 결과 입니다",
    #     body = "요청하신 소비 패턴 분석 그래프를 첨부해 드립니다",
    #     to=[user_email],
    # )
    # email.attach("spending_report.png",buffer.getvalue(),"image/png")
    # email.send()
    #
    # # 메모리 저장
    # buffer.close()
    # plt.close()
    # return f"success: Analysis saved and email sent to {user_email}"

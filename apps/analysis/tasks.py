from celery import shared_task
import pandas as pd
from datetime import datetime, timedelta

from django.core.mail import send_mail

from apps.analysis.models import Analysis
from apps.transactions.models import Transaction


@shared_task
def process_spending_analysis(user,data):

    queryset = Transaction.objects.filter(
        user_id=user['id'],created_at__range=(data['period_start'],data['period_end'])
    )

    # 제시한 기간에 맞는 거래내역이 었을때 No data 출력
    if not queryset.exists():
        return "No data"

    # 각각의 instance들을 transaction_type과 transaction_amount로 이루어진 표 행태로 저장
    df = pd.DataFrame(list(queryset.values("transaction_type","transaction_amount")))
    # 직렬화로 인해 string으로 형변환된 Decimal를 계산을 위해 float로 형변환
    df["transaction_amount"] = pd.to_numeric(df["transaction_amount"],errors="coerce").astype(float)
    # 전체 instance들을 groupby로 transaction_type에 대한 transaction_amount의 총합을 표 형태로 저장
    summary = df.groupby("transaction_type")["transaction_amount"].sum()

    # 완성된 결과를 Analysis에 instance 생성
    Analysis.objects.create(
        user_id=user["id"],
        type = data["type"],
        about= data["about"],
        period_start= data["period_start"],
        period_end= data["period_end"],
        description=f"{user['name']}의 {data['period_start']}~{data['period_end']} {data['about']}분석결과",
        result_image = None, # 추후 추가할 기능으로 남겨둠
        result_json= summary.to_dict(), # JSONField로 인해 바로 파싱 할수 있도록 dict형식으로 저장
    )

    return summary.to_dict()


@shared_task
def daily_analysis_spending():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()

    yesterday = datetime.now() - timedelta(days=1)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999)

    for user in users:
       user_info = {
           "id" : user.id,
           "name":user.name,
           "email":user.email
       }

       analysis_data = {
           "type" : "daily",
           "about": "TOTAL_SPENDING",
           "period_start" : start_date.isoformat(),
           "period_end" : end_date.isoformat(),
       }
       process_spending_analysis.delay(user_info,analysis_data)
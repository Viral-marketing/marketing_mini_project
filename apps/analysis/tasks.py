from celery import shared_task
import pandas as pd
from datetime import datetime, timedelta

from apps.analysis.models import Analysis
from apps.transactions.models import Transaction
from apps.analysis.utils import SendCustomEmail

@shared_task
def process_analysis(user,data):
    # transaction_type 필터링
    if data["about"] == "TOTAL_SPENDING": # 소비일때는 WITHDRAW인 것만
        queryset = Transaction.objects.filter(
            user_id=user['id'],transaction_type="WITHDRAW",
            created_at__range=(data['period_start'],data['period_end'])
        )
    elif data["about"] == "TOTAL_INCOME": # 수입 일때는 DEPOSIT인 것만
        queryset = Transaction.objects.filter(
            user_id=user['id'], transaction_type="DEPOSIT",
            created_at__range=(data['period_start'], data['period_end'])
        )
    else:
        return f"TOTAL_SPENDING(지출)과 TOTAL_INCOME(수입) 중 하나를 선택해주세요"



    # 제시한 기간에 맞는 거래내역이 었을때 No data 출력
    if not queryset.exists():
        return "No data"

    # 각각의 instance들을 transaction_type과 transaction_amount로 이루어진 표 행태로 저장
    df = pd.DataFrame(list(queryset.values("transaction_type","transaction_amount")))

    # 직렬화로 인해 string으로 형변환된 Decimal를 계산을 위해 float로 형변환
    # coerce는 숫자형으로 형변환이 안되는 string이나 특수문자를 NaN(Not a Number)로 처리해서 500에러를 방지한다
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
        description=f"{user['name']}의 [{data['period_start']} ~ {data['period_end']}] {data['about']}분석결과",
        result_image = None, # 추후 추가할 기능으로 남겨둠
        result_json= summary.to_dict(), # JSONField로 인해 바로 파싱 할수 있도록 dict형식으로 저장
    )
    # 이메일 발송
    if data['type'] == "CUSTOM": # custom일때는 '요청하신'으로 시작하는 이메일 제목 전송
        if data['about'] == "TOTAL_SPENDING":
            # 이메일 전송할때 json.dumps로 직령화를 하는 과정에서 전체 summary객체를 넘기면 typeerror가 발생함
            # 직렬화를 위해 dict로 형변환 후 이메일 전송함수에 넘겨줌
            SendCustomEmail.send_analysis_for_spending(user,summary.to_dict())
        if data['about'] == "TOTAL_INCOME":
            SendCustomEmail.send_analysis_for_income(user,summary.to_dict())
    elif data['type'] == "DAILY": # 정기 전송 메일 분리
        if data['about'] == "TOTAL_SPENDING":
            SendCustomEmail.send_analysis_daily_spending(user,summary.to_dict())
        if data['about'] == "TOTAL_INCOME":
            SendCustomEmail.send_analysis_daily_income(user,summary.to_dict())

    return summary.to_dict()


@shared_task
def daily_analysis():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()

    yesterday = datetime.now() - timedelta(days=1)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999)
    daily_analysis_spending(users,start_date,end_date)
    daily_analysis_for_income(users,start_date,end_date)

def daily_analysis_spending(users,start_date,end_date):
    for user in users:
       user_info = {
           "id" : user.id,
           "name":user.name,
           "email":user.email
       }

       analysis_data = {
           "type" : "DAILY",
           "about": "TOTAL_SPENDING",
           "period_start" : start_date.isoformat(),
           "period_end" : end_date.isoformat(),
       }
       process_analysis.delay(user_info,analysis_data)

def daily_analysis_for_income(users,start_date,end_date):
    for user in users:
       user_info = {
           "id" : user.id,
           "name":user.name,
           "email":user.email
       }

       analysis_data = {
           "type" : "DAILY",
           "about": "TOTAL_INCOME",
           "period_start" : start_date.isoformat(),
           "period_end" : end_date.isoformat(),
       }
       process_analysis.delay(user_info,analysis_data)


from django.db import models
from django.contrib.auth import get_user_model
from apps.common.constants import ANALYSIS_TYPES, ANALYSIS_ABOUT

User = get_user_model()

class Analysis(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="analysis")
    type = models.CharField(choices=ANALYSIS_TYPES,default="DAILY",max_length=10)
    about = models.CharField(choices=ANALYSIS_ABOUT,default="TOTAL_SPENDING",max_length=50)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    description = models.TextField()
    result_image = models.ImageField(upload_to="analysis/",default="analysis/default.png")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.get_type_display}{self.get_about_display}분석"

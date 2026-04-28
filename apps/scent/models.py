from django.db import models


class CombinedSearchModel(models.Model):
    class Meta:
        app_label = "scent"
        managed = False
        verbose_name = "통합 검색"
        verbose_name_plural = "통합 검색"

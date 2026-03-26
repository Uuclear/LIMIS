from django.db import models
from django.conf import settings


class BaseManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    """All business models inherit from this."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人',
        related_name='%(class)s_created',
    )
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    objects = BaseManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

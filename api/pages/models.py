from django.db import models

# Create your models here.


class Page(models.Model):
    page_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        db_table = 'pages'


class PageTree(models.Model):
    ancestor = models.ForeignKey(
        Page, related_name='ancestor_set', on_delete=models.CASCADE)
    descendant = models.ForeignKey(
        Page, related_name='descendant_set', on_delete=models.CASCADE)

    class Meta:
        db_table = 'page_trees'

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructor', '0002_choice_lesson_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]


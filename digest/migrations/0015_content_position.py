import re

from django.db import migrations, models


def _offset(raw_text, source_text, title):
    # Frozen matching logic: do not depend on application code in migrations.
    for candidate in (source_text, title):
        if candidate and candidate.strip():
            pattern = r"\s+".join(re.escape(word) for word in candidate.split())
            matches = list(re.finditer(pattern, raw_text))
            if len(matches) == 1:
                return matches[0].start()
    return None


def populate_positions(apps, schema_editor):
    alias = schema_editor.connection.alias
    Digest = apps.get_model("digest", "DailyDigest")
    for digest in Digest.objects.using(alias).all().iterator():
        for name, title_field in (("Article", "title"), ("LearningItem", "heading")):
            Model = apps.get_model("digest", name)
            items = list(Model.objects.using(alias).filter(digest_id=digest.pk).order_by("pk"))
            located = []
            for item in items:
                offset = _offset(digest.raw_text, item.source_text, getattr(item, title_field))
                # Unrecoverable historical entries follow matched ones in explicit PK order.
                located.append((offset is None, offset if offset is not None else item.pk, item.pk, item))
            for position, (_, _, _, item) in enumerate(sorted(located, key=lambda row: row[:3]), 1):
                item.position = position
            Model.objects.using(alias).bulk_update(items, ["position"])


class Migration(migrations.Migration):
    dependencies = [("digest", "0014_source_text")]

    operations = [
        migrations.AddField("article", "position", models.PositiveIntegerField(null=True)),
        migrations.AddField("learningitem", "position", models.PositiveIntegerField(null=True)),
        migrations.RunPython(populate_positions, migrations.RunPython.noop),
        migrations.AlterField("article", "position", models.PositiveIntegerField()),
        migrations.AlterField("learningitem", "position", models.PositiveIntegerField()),
        migrations.AlterModelOptions("article", {"ordering": ["digest__date", "position"]}),
        migrations.AlterModelOptions("learningitem", {"ordering": ["digest__date", "position"]}),
        migrations.AddConstraint("article", models.UniqueConstraint(fields=("digest", "position"), name="article_digest_position_unique")),
        migrations.AddConstraint("learningitem", models.UniqueConstraint(fields=("digest", "position"), name="learningitem_digest_position_unique")),
    ]

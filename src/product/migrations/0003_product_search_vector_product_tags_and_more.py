# Generated by Django 5.0.1 on 2024-05-06 12:48

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


def update_search_vector(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    from django.contrib.postgres.search import SearchVector

    Product.objects.update(search_vector=SearchVector("tags"))


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0002_category_product_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="tags",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="product_search__4bea98_gin"
            ),
        ),
        migrations.RunSQL(
            sql="""
                    CREATE TRIGGER search_vector_trigger
                    BEFORE INSERT OR UPDATE OF tags, search_vector
                    ON product
                    FOR EACH ROW EXECUTE PROCEDURE
                    tsvector_update_trigger(
                        search_vector, 'pg_catalog.english', tags
                    );
                    UPDATE product SET search_vector = NULL;
                    """,
            reverse_sql="""
                    DROP TRIGGER IF EXISTS search_vector_trigger
                    ON product;
                    """,
        ),
        migrations.RunPython(
            update_search_vector, reverse_code=migrations.RunPython.noop
        ),
    ]
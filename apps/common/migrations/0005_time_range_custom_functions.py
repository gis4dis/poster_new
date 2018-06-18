from django.db import migrations

def create_duration_function():
    sql_statements = """
CREATE OR REPLACE FUNCTION duration(TSTZRANGE) RETURNS INTERVAL AS '
    SELECT UPPER($1) - LOWER($1);
' LANGUAGE SQL STABLE;
"""
    return sql_statements

class Migration(migrations.Migration):
    dependencies = [
        ('common', '0004_property_default_mean'),
    ]

    operations = [
        migrations.RunSQL(create_duration_function())
    ]

from eSparkTalent.settings import (
    talent_email,
    AWS_STORAGE_BUCKET_NAME,
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
)
from b2sdk.v2 import B2Api
from django.db.models.fields.files import FileField
import tempfile


def remove_bucket_file(file_name):
    old_file = file_name
    b2_api = B2Api()
    b2_api.authorize_account(
        "production",
        application_key_id=AWS_ACCESS_KEY_ID,
        application_key=AWS_SECRET_ACCESS_KEY,
    )
    bucket = b2_api.get_bucket_by_name(AWS_STORAGE_BUCKET_NAME)
    if old_file:
        try:
            for file_version in bucket.list_file_versions(file_name=old_file):
                bucket.delete_file_version(file_name=old_file, file_id=file_version.id_)
            return None
        except Exception as e:
            return e


def download_file_from_bucket(file_name):
    b2_api = B2Api()
    b2_api.authorize_account(
        "production",
        application_key_id=AWS_ACCESS_KEY_ID,
        application_key=AWS_SECRET_ACCESS_KEY,
    )

    bucket = b2_api.get_bucket_by_name(AWS_STORAGE_BUCKET_NAME)

    try:
        file = bucket.download_file_by_name(file_name=file_name)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file)

        return temp_file
    except Exception as e:
        return None

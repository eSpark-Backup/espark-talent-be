from eSparkTalent.settings import (
    talent_email,
    AWS_STORAGE_BUCKET_NAME,
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
)
from b2sdk.v2 import B2Api
from django.db.models.fields.files import FileField

def remove_bucket_files(file_name):
    previous_profile_picture = file_name
    b2_api = B2Api()
    b2_api.authorize_account(
        "production",
        application_key_id=AWS_ACCESS_KEY_ID,
        application_key=AWS_SECRET_ACCESS_KEY,
    )
    bucket = b2_api.get_bucket_by_name(AWS_STORAGE_BUCKET_NAME)
    if previous_profile_picture:
        try:
            for file_version in bucket.list_file_versions(
                file_name=previous_profile_picture
            ):
                bucket.delete_file_version(
                    file_name=previous_profile_picture, file_id=file_version.id_
                )
            return None
        except Exception as e:
            return e
from django.apps import AppConfig
import threading


class EsparktalentapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eSparkTalentAPI'

    def ready(self):
        from .threads import Check_Punches
        thread = threading.Thread(target=Check_Punches().check_punch)
        thread.start()
from .models import OAuth
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class OAuthAuthenticationBackend(object):
    def authenticate(self, token=None, uid=None, expire_in=None):
        """
        check if uid aleady exists, create user if not exist
        """
        if token and uid:
            expired = self._get_expired_time(expire_in)
            try:
                user = User.objects.get(oauth__uid=uid)
                user.oauth.token = token
                user.oauth.expired = expired
                user.oauth.save()
            except User.DoesNotExist:
                user = User()
                user.username = "weibo_%s" % uid
                user.save()

                user.oauth = OAuth(user=user, token=token, uid=uid, expired=expired)
                user.oauth.save()

            return user

        return None

    def _get_expired_time(self, expire_in):
        return timezone.now() + timedelta(seconds=expire_in)

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            # check if OAuth has expired
            if user.oauth.expired >= timezone.now(): 
                return user
        except User.DoesNotExist:
            return None

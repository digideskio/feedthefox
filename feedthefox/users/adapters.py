from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from feedthefox.users.mozillians import MozilliansClient


class FeedTheFoxAdapter(DefaultAccountAdapter):
    """Customize the default allauth account adapter."""

    def is_open_for_signup(self, request):
        """Disable signup since everything will go through Persona."""

        return False


class FeedTheFoxSocialAdapter(DefaultSocialAccountAdapter):

    def __init__(self, *args, **kwargs):
        """Initialize mozillians.org api client."""

        super(FeedTheFoxSocialAdapter, self).__init__(*args, **kwargs)
        self.mozillians_client = MozilliansClient(settings.MOZILLIANS_API_URL,
                                                  settings.MOZILLIANS_API_KEY)

    def is_open_for_signup(self, request, sociallogin):
        """ Enable signup only through social accounts."""

        return True

    def populate_user(self, request, sociallogin, data):
        """Populate user with data from mozillians.org."""

        mozillian_attrs = ['country', 'photo', 'ircname', 'city']
        user = super(FeedTheFoxSocialAdapter, self).populate_user(request,
                                                                  sociallogin,
                                                                  data)
        try:
            mozillian = self.mozillians_client.lookup_user({'email': user.email})
        except:
            mozillian = None

        if mozillian:
            user.username = mozillian['username']
            for attr in mozillian_attrs:
                if mozillian[attr].get('privacy') == 'Public':
                    setattr(user, attr, mozillian[attr].get('value'))
            if mozillian['full_name']['privacy'] == 'Public':
                first_name, last_name = mozillian['full_name']['value'].split(' ', 1)
            else:
                first_name = 'Anonymous'
                last_name = 'Mozillian'
            user.first_name = first_name
            user.last_name = last_name
        else:
            user.is_active = False
        return user
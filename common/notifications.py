from django.template.loader import render_to_string
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from common.models import Monitor
from notifications.backends import BACKEND
from notifications.models import SystemMsgSubscription
from notifications.notifications import SystemMessage
from system.models import UserInfo


class ServerPerformanceMessage(SystemMessage):
    category = 'Monitor'
    category_label = _('Monitor')
    message_type_label = _('Server performance')

    def __init__(self, terms_with_errors):
        self.terms_with_errors = terms_with_errors

    def get_html_msg(self) -> dict:
        subject = gettext("Server health check warning")
        context = {
            'terms_with_errors': self.terms_with_errors
        }
        message = render_to_string('monitor/_msg_terminal_performance.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def post_insert_to_db(cls, subscription: SystemMsgSubscription):
        admins = UserInfo.objects.filter(is_superuser=True, is_active=True)
        subscription.users.add(*admins)
        subscription.receive_backends = [BACKEND.EMAIL]
        subscription.save()

    @classmethod
    def gen_test_msg(cls):
        pass


class ServerPerformanceCheckUtil(object):
    items_mapper = {
        'disk_used': {
            'default': 0,
            'max_threshold': 80,
            'alarm_msg_format': _('Disk used more than {max_threshold}%: => {value}')
        },
        'memory_used': {
            'default': 0,
            'max_threshold': 85,
            'alarm_msg_format': _('Memory used more than {max_threshold}%: => {value}'),
        },
        'cpu_load': {
            'default': 0,
            'max_threshold': 5,
            'alarm_msg_format': _('CPU load more than {max_threshold}: => {value}'),
        },
    }

    def __init__(self):
        self.terms_with_errors = []
        self._terminals = []

    def check_and_publish(self):
        self.check()
        self.publish()

    def check(self):
        self.terms_with_errors = []
        self.initial_terminals()

        for term in self._terminals:
            errors = self.check_terminal(term)
            if not errors:
                continue
            self.terms_with_errors.append((term, errors))

    def check_terminal(self, term):
        errors = []
        for item, data in self.items_mapper.items():
            error = self.check_item(term, item, data)
            if not error:
                continue
            errors.append(error)
        return errors

    @staticmethod
    def check_item(term, item, data):
        default = data['default']
        max_threshold = data['max_threshold']
        value = getattr(term, item, default)

        if isinstance(value, bool) and value != max_threshold:
            return
        elif isinstance(value, (int, float)) and value < max_threshold:
            return
        msg = data['alarm_msg_format']
        error = msg.format(max_threshold=max_threshold, value=value, name='api')
        return error

    def publish(self):
        if not self.terms_with_errors:
            return
        ServerPerformanceMessage(self.terms_with_errors).publish()

    def initial_terminals(self):
        self._terminals = [Monitor.objects.last()]
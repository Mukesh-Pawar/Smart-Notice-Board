import logging
import os

logger = logging.getLogger(__name__)


def format_notice_for_sms(notice, max_length=160):
    text = f'{notice.priority}: {notice.title} - {notice.message}'
    if len(text) <= max_length:
        return text
    return text[:max_length - 3].rstrip() + '...'


def send_sms(phone_number, message):
    """Hardware-independent GSM abstraction.

    The first release deliberately logs the outgoing message when GSM_ENABLED
    is false. A SIM800L/SIM900 adapter can later replace this function without
    changing Django views or notice business logic.
    """
    if not os.getenv('GSM_ENABLED', 'False').lower() in {'1', 'true', 'yes', 'on'}:
        logger.info('GSM disabled; simulated SMS to %s: %s', phone_number, message)
        return {'success': True, 'mocked': True, 'message': message}

    # Safe boundary for future serial/modem implementation.
    # No real credentials or serial commands are embedded in the project.
    port = os.getenv('GSM_SERIAL_PORT')
    if not port:
        logger.warning('GSM_ENABLED is true but GSM_SERIAL_PORT is not configured.')
        return {'success': False, 'mocked': False, 'error': 'GSM serial port is not configured.'}
    logger.info('GSM integration boundary reached for port %s; hardware adapter required.', port)
    return {'success': False, 'mocked': False, 'error': 'Hardware adapter is not configured.'}


def send_notice_via_gsm(notice):
    """Prepare a notice for future board/SMS delivery without blocking web UX."""
    message = format_notice_for_sms(notice)
    target = os.getenv('GSM_SIM_NUMBER')
    if target:
        return send_sms(target, message)
    logger.info('No GSM_SIM_NUMBER configured. Notice %s prepared but not transmitted.', notice.pk)
    return {'success': True, 'mocked': True, 'message': message}

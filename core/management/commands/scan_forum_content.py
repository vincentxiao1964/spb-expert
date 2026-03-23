import re

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import MemberMessage, MessageReply


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true')
        parser.add_argument('--limit', type=int, default=2000)
        parser.add_argument('--keywords', type=str, default='')

    def handle(self, *args, **options):
        delete = bool(options['delete'])
        limit = int(options['limit'])
        keywords_raw = (options['keywords'] or '').strip()

        default_keywords = [
            '成人',
            '色情',
            '色情网',
            '博彩',
            '赌博',
            '约炮',
            '裸聊',
            '枪',
            '弹药',
            '毒品',
        ]
        keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()] or default_keywords
        pattern = re.compile('|'.join(re.escape(k) for k in keywords), re.IGNORECASE)

        hits = []

        for msg in MemberMessage.objects.order_by('-created_at')[:limit]:
            content = msg.content or ''
            if pattern.search(content):
                hits.append(('topic', msg.id, msg.user_id, msg.created_at, content[:120].replace('\n', ' ')))

        for rep in MessageReply.objects.order_by('-created_at')[:limit]:
            content = rep.content or ''
            if pattern.search(content):
                hits.append(('reply', rep.id, rep.user_id, rep.created_at, content[:120].replace('\n', ' ')))

        hits.sort(key=lambda x: x[3], reverse=True)

        self.stdout.write(f'hits={len(hits)} keywords={keywords}')
        for kind, obj_id, user_id, created_at, snippet in hits[:200]:
            self.stdout.write(f'[{kind}] id={obj_id} user_id={user_id} at={created_at} snippet="{snippet}"')

        if not delete or not hits:
            return

        with transaction.atomic():
            topic_ids = [h[1] for h in hits if h[0] == 'topic']
            reply_ids = [h[1] for h in hits if h[0] == 'reply']
            if reply_ids:
                MessageReply.objects.filter(id__in=reply_ids).delete()
            if topic_ids:
                MemberMessage.objects.filter(id__in=topic_ids).delete()

        self.stdout.write('deleted=1')


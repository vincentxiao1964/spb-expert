
import os

file_path = r'd:\spb-expert11\frontend\src\pages\order\detail.vue'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements for i18n
replacements = [
    ('Logistics Info', "{{ $t('order.logistics') }}"),
    ("'Unknown'", "'Unknown'"), # Keep as is or translate? Let's leave for now or use $t('common.unknown') if existed
    ('Carrier:', "{{ $t('order.carrier') }}:"),
    ('Track #:', "{{ $t('order.tracking_no') }}:"),
    ('Customs:', "{{ $t('order.customs') }}:"),
    ('No tracking events yet.', "{{ $t('order.no_events') }}"),
    ('Original Total', "{{ $t('order.original_total') }}"),
    ('Discount', "{{ $t('order.discount') }}"),
    ('Final Total', "{{ $t('order.final_total') }}"),
    ('No:', "{{ $t('order.no') }}:")
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully updated detail.vue for i18n")

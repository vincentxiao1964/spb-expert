
import os

file_path = r'd:\spb-expert11\frontend\src\pages\procurement\detail.vue'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements for i18n
replacements = [
    ("Budget:", "{{ $t('procurement.budget') }}:"),
    ("'Negotiable'", "$t('procurement.negotiable')"),
    ("Deadline:", "{{ $t('procurement.deadline') }}:"),
    ("Requirements:", "{{ $t('procurement.requirements') }}:"),
    ("Sample Required", "{{ $t('procurement.sample_required_badge') }}"),
    (">Submit Quotation<", ">{{ $t('procurement.submit_quotation') }}<"),
    ('placeholder="Your Price"', ':placeholder="$t(\'procurement.price_placeholder\')"'),
    ('placeholder="Message to buyer (e.g. delivery time, specs)"', ':placeholder="$t(\'procurement.message_placeholder\')"'),
    ("Sample Provided?", "{{ $t('procurement.sample_provided_question') }}"),
    (">Submit Quote<", ">{{ $t('procurement.submit_btn') }}<"),
    (">Your Quotation<", ">{{ $t('procurement.your_quotation') }}<"),
    ("Price:", "{{ $t('procurement.price') }}:"),
    ("Status:", "{{ $t('procurement.status') }}:"),
    ("Received Quotations", "{{ $t('procurement.received_quotations') }}"),
    (">Accept<", ">{{ $t('procurement.accept') }}<"),
    # Careful with replacements that might match multiple things incorrectly
]

# We need to be careful with "Sample Required" inside v-if
# Original: <view class="sample-badge" v-if="item.is_sample_required">\n                Sample Required\n            </view>
# My replacement: {{ $t(...) }}
# That works.

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully updated procurement/detail.vue for i18n")

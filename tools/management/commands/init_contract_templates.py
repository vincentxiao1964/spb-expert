import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from tools.models import ContractTemplate
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize Contract Templates with real content'

    def handle(self, *args, **options):
        templates = [
            # Domestic S&P
            {
                'title': '国内船舶买卖合同 (示范文本)',
                'category': ContractTemplate.Category.SALE_PURCHASE,
                'scope': ContractTemplate.Scope.DOMESTIC,
                'sub_type': ContractTemplate.SubType.SNP_GENERAL,
                'content': """船舶买卖合同

甲方（买方）：_________
乙方（卖方）：_________

一、买卖标的
船名：_________  船型：_________
船籍：_________  船级：_________
总长：_________  船宽：_________
总吨：_________  载重吨：_________

二、质量要求
1．卖方向买方出售的船舶，其质量必须符合交通管理部门制定的船舶标准；
2．卖方保证出售船舶所具的性能与说明书相符，并须在交付前先行试航。

三、价款
本合同标的船舶的价款为_________元。

四、保证金
买方应在合同签订日后的_________日内支付合同价款百分之_________的保证金。

五、交接船舶
1．船舶在_________地点进行交接。
2．移交时间为_________年_________月_________日。
3．船舶按买方看验船时的状况移交，自然损耗除外。

六、所有权转移
卖方在收到全部船价款后，应向买方出具购船发票，并将船舶所有权移交给买方。
"""
            },
            # International S&P
            {
                'title': 'Memorandum of Agreement (SALEFORM 2012)',
                'category': ContractTemplate.Category.SALE_PURCHASE,
                'scope': ContractTemplate.Scope.INTERNATIONAL,
                'sub_type': ContractTemplate.SubType.SNP_GENERAL,
                'content': """MEMORANDUM OF AGREEMENT (SALEFORM 2012)

1. Purchase Price
The Purchase Price is _________

2. Deposit
As security for the correct fulfillment of this Agreement the Buyers shall lodge a deposit of 10% (ten per cent) of the Purchase Price.

3. Payment
The Purchase Price shall be paid in full free of bank charges to the Sellers' Bank on delivery of the Vessel.

4. Inspection
The Buyers have inspected and accepted the Vessel's classification records. The Buyers have also inspected the Vessel at/in _________ and have accepted the Vessel following such inspection.

5. Notices, Time and Place of Delivery
The Vessel shall be delivered and taken over safely afloat at a safe port or safe anchorage at _________ in the Sellers' option.

6. Documentation
The Sellers shall provide for delivery of the Vessel:
(i) Legal Bill(s) of Sale.
(ii) Certificate of Ownership.
(iii) Confirmation of Class.
"""
            },
            # Domestic Time Charter
            {
                'title': '国内水路定期租船合同 (示范文本)',
                'category': ContractTemplate.Category.CHARTER_PARTY,
                'scope': ContractTemplate.Scope.DOMESTIC,
                'sub_type': ContractTemplate.SubType.TIME_CHARTER,
                'content': """定期租船合同

出租人：_________
承租人：_________

1. 船舶规范
船名：_________  总吨：_________
净吨：_________  载重量：_________

2. 租期
本合同租期为_________，自船舶交付之日起算。

3. 租金支付
租金率按每_________元支付，每半个月预付一次。

4. 燃油与港口费用
承租人应提供并支付所有燃油、港口费用、引航费、代理费等营运费用。

5. 停租
若由于船员不齐、物料不足、船壳或机器损坏导致船舶无法正常营运，则租金应按比例停付。
"""
            },
            # International Time Charter (NYPE 2015)
            {
                'title': 'NYPE 2015 (Time Charter)',
                'category': ContractTemplate.Category.CHARTER_PARTY,
                'scope': ContractTemplate.Scope.INTERNATIONAL,
                'sub_type': ContractTemplate.SubType.TIME_CHARTER,
                'content': """NEW YORK PRODUCE EXCHANGE FORM 2015 (NYPE 2015)

1. Owners to Provide
The Owners shall provide and pay for all provisions, wages and all other expenses of the crew, for the insurance of the Vessel.

2. Charterers to Provide
The Charterers shall provide and pay for all the fuel except as otherwise agreed, Port Charges, Pilotages, Agencies, Commissions.

3. Rate of Hire
The Charterers shall pay for the use and hire of the said Vessel at the rate of _________ per day.

4. Bunkers
The Charterers shall supply bunkers of the agreed specifications and grades.

5. Off Hire
In the event of the loss of time from deficiency of men or stores, fire, breakdown or damages to hull, machinery or equipment, the payment of hire shall cease for the time thereby lost.
"""
            },
            # International Bareboat (BARECON 2017)
            {
                'title': 'BARECON 2017 (Bareboat Charter)',
                'category': ContractTemplate.Category.CHARTER_PARTY,
                'scope': ContractTemplate.Scope.INTERNATIONAL,
                'sub_type': ContractTemplate.SubType.BAREBOAT_CHARTER,
                'content': """STANDARD BAREBOAT CHARTER (BARECON 2017)

1. Delivery
The Owners shall before and at the time of delivery exercise due diligence to make the Vessel seaworthy.

2. Maintenance and Operation
The Charterers shall maintain the Vessel in a good state of repair, in efficient operating condition and in accordance with good commercial maintenance practice.

3. Hire
The Charterers shall pay to the Owners for the hire of the Vessel at the lump sum rate of _________ per calendar month.

4. Insurance
The Vessel shall be kept insured by the Charterers at their expense against marine, hull and machinery and war risks.

5. Redelivery
The Charterers shall at the expiration of the Charter period redeliver the Vessel to the Owners in the same or as good structure and condition as that in which she was delivered.
"""
            },
            # International Voyage (GENCON 1994)
            {
                'title': 'GENCON 1994 (Voyage Charter)',
                'category': ContractTemplate.Category.CHARTER_PARTY,
                'scope': ContractTemplate.Scope.INTERNATIONAL,
                'sub_type': ContractTemplate.SubType.VOYAGE_CHARTER,
                'content': """UNIFORM GENERAL CHARTER (GENCON 1994)

1. Voyage
The Vessel shall proceed to the loading port or place stated in Box 10 or so near thereto as she may safely get and lie always afloat.

2. Freight
The freight shall be paid in the manner prescribed in Box 13 in cash without discount on right and true delivery of the cargo.

3. Laytime
Separate laytime for loading and discharging shall be allowed as stated in Box 16.

4. Demurrage
Demurrage at the loading and discharging port is potentially payable by the Charterers to the Owners.

5. Owners' Responsibility Clause
The Owners are to be responsible for loss of or damage to the goods or for delay in delivery of the goods only in case the loss, damage or delay has been caused by personal want of due diligence on the part of the Owners.
"""
            },
        ]

        for t_data in templates:
            content = t_data.pop('content')
            template, created = ContractTemplate.objects.get_or_create(
                title=t_data['title'],
                defaults=t_data
            )
            
            # Update existing or create new file
            file_name = f"{t_data['scope']}_{t_data['category']}_{t_data['sub_type']}.txt".lower()
            if template.file:
                # Remove old file if exists
                if os.path.exists(template.file.path):
                    os.remove(template.file.path)
            
            template.file.save(file_name, ContentFile(content))
            template.save()
            self.stdout.write(self.style.SUCCESS(f"Updated template: {template.title}"))


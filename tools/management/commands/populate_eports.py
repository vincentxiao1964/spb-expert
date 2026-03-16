from django.core.management.base import BaseCommand
from tools.models import Port

class Command(BaseCommand):
    help = 'Populate ports from e-ports.com.cn list'

    def handle(self, *args, **options):
        ports_data = [
          {
            "en": "Rotterdam",
            "zh": "荷兰·鹿特丹",
            "country_zh": "荷兰",
            "name_zh": "鹿特丹"
          },
          {
            "en": "Piraeus",
            "zh": "希腊·比雷埃夫斯",
            "country_zh": "希腊",
            "name_zh": "比雷埃夫斯"
          },
          {
            "en": "St. Petersburg",
            "zh": "俄罗斯·圣彼得堡",
            "country_zh": "俄罗斯",
            "name_zh": "圣彼得堡"
          },
          {
            "en": "Istanbul",
            "zh": "土耳其·伊斯坦布尔",
            "country_zh": "土耳其",
            "name_zh": "伊斯坦布尔"
          },
          {
            "en": "Los Angeles",
            "zh": "美国·洛杉矶",
            "country_zh": "美国",
            "name_zh": "洛杉矶"
          },
          {
            "en": "New York",
            "zh": "美国·纽约",
            "country_zh": "美国",
            "name_zh": "纽约"
          },
          {
            "en": "Houston",
            "zh": "美国·休斯顿",
            "country_zh": "美国",
            "name_zh": "休斯顿"
          },
          {
            "en": "Antwerp",
            "zh": "比利时·安特卫普",
            "country_zh": "比利时",
            "name_zh": "安特卫普"
          },
          {
            "en": "Balboa",
            "zh": "巴拿马·巴尔博亚",
            "country_zh": "巴拿马",
            "name_zh": "巴尔博亚"
          },
          {
            "en": "Santos",
            "zh": "巴西·桑托斯",
            "country_zh": "巴西",
            "name_zh": "桑托斯"
          },
          {
            "en": "Gibraltar",
            "zh": "直布罗陀",
            "country_zh": "直布罗陀", # Territory
            "name_zh": "直布罗陀"
          },
          {
            "en": "Suez",
            "zh": "埃及·苏伊士",
            "country_zh": "埃及",
            "name_zh": "苏伊士"
          },
          {
            "en": "Fujairah",
            "zh": "阿拉伯·富查伊拉",
            "country_zh": "阿联酋", # Correct country
            "name_zh": "富查伊拉"
          },
          {
            "en": "Durban",
            "zh": "南非·德班",
            "country_zh": "南非",
            "name_zh": "德班"
          },
          {
            "en": "Singapore",
            "zh": "新加坡",
            "country_zh": "新加坡",
            "name_zh": "新加坡"
          },
          {
            "en": "Tokyo",
            "zh": "日本·东京",
            "country_zh": "日本",
            "name_zh": "东京"
          },
          {
            "en": "Osaka",
            "zh": "日本·大阪",
            "country_zh": "日本",
            "name_zh": "大阪"
          },
          {
            "en": "Busan",
            "zh": "韩国·釜山",
            "country_zh": "韩国",
            "name_zh": "釜山"
          },
          {
            "en": "Qingdao",
            "zh": "中国·青岛",
            "country_zh": "中国",
            "name_zh": "青岛"
          },
          {
            "en": "Zhoushan",
            "zh": "中国·舟山",
            "country_zh": "中国",
            "name_zh": "舟山"
          },
          {
            "en": "Shanghai",
            "zh": "中国·上海",
            "country_zh": "中国",
            "name_zh": "上海"
          },
          {
            "en": "Hong Kong",
            "zh": "中国·香港",
            "country_zh": "中国",
            "name_zh": "香港"
          },
          {
            "en": "Kaohsiung",
            "zh": "中国·高雄",
            "country_zh": "中国",
            "name_zh": "高雄"
          }
        ]

        # Country EN map (simple)
        country_en_map = {
            "荷兰": "Netherlands",
            "希腊": "Greece",
            "俄罗斯": "Russia",
            "土耳其": "Turkey",
            "美国": "USA",
            "比利时": "Belgium",
            "巴拿马": "Panama",
            "巴西": "Brazil",
            "直布罗陀": "Gibraltar",
            "埃及": "Egypt",
            "阿联酋": "UAE",
            "南非": "South Africa",
            "新加坡": "Singapore",
            "日本": "Japan",
            "韩国": "South Korea",
            "中国": "China"
        }

        count = 0
        for p in ports_data:
            # Clean up zh names
            name_zh = p['name_zh']
            country_zh = p['country_zh']
            
            # Special handling
            if "·" in p['zh']:
                parts = p['zh'].split('·')
                if len(parts) == 2:
                    country_zh = parts[0]
                    name_zh = parts[1]
            
            country_en = country_en_map.get(country_zh, "Unknown")
            
            # Update or create
            # Note: We rely on name_en being unique.
            # If port exists, we update zh names if they are empty
            try:
                port, created = Port.objects.get_or_create(
                    name_en=p['en'],
                    defaults={
                        'name_zh': name_zh,
                        'country_en': country_en,
                        'country_zh': country_zh,
                        'latitude': 0, # Placeholder
                        'longitude': 0 # Placeholder
                    }
                )
                
                if not created:
                    if not port.name_zh:
                        port.name_zh = name_zh
                    if not port.country_zh:
                        port.country_zh = country_zh
                    port.save()
                    self.stdout.write(f"Updated {port.name_en}")
                else:
                    self.stdout.write(f"Created {port.name_en}")
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {p['en']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Processed {count} ports."))

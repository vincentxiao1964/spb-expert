from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.store.models import Category
from apps.services.models import ServiceCategory
from apps.crew.models import JobPosition

class Command(BaseCommand):
    help = 'Populates initial categories for Store and Services'

    def handle(self, *args, **options):
        self.stdout.write('Starting data population...')
        
        # --- Store Categories (Equipment & Stores) ---
        store_data = [
            {
                "name": "船舶设备与配件", "name_en": "Marine Equipment & Spare Parts", 
                "slug": "marine-equipment-spare-parts",
                "children": [
                    {
                        "name": "动力系统设备及备件", "slug": "propulsion-system",
                        "children": ["主机", "发电机", "增压器", "分油机", "空压机", "泵类", "阀件", "滤清器", "轴系", "螺旋桨", "齿轮箱及配件"]
                    },
                    {
                        "name": "甲板机械", "slug": "deck-machinery",
                        "children": ["锚机", "绞车", "绞盘", "克令吊", "舵机", "舱口盖", "液压系统及配件"]
                    },
                    {
                        "name": "电气与自动化", "slug": "electrical-automation",
                        "children": ["配电板", "配电箱", "船用电缆", "灯具", "开关", "传感器", "机舱报警", "PLC", "变频器"]
                    },
                    {
                        "name": "导航与通讯", "slug": "navigation-communication",
                        "children": ["雷达", "GPS", "罗经", "AIS", "VHF", "卫通", "测深仪", "EPIRB", "SART"]
                    },
                    {
                        "name": "消防设备", "slug": "fire-fighting",
                        "children": ["消防泵", "水带", "水枪", "灭火器", "CO₂系统", "泡沫系统", "消防箱"]
                    },
                    {
                        "name": "救生设备", "slug": "life-saving",
                        "children": ["救生艇", "救生筏", "救生衣", "救生圈", "抛绳设备", "救助艇配件"]
                    },
                    {
                        "name": "船体舾装与钢结构", "slug": "hull-outfitting",
                        "children": ["船用门", "窗", "舱口盖", "栏杆", "梯子", "踏步", "密封件", "锌块", "防腐材料"]
                    },
                    {
                        "name": "管系与阀门", "slug": "piping-valves",
                        "children": ["船用钢管", "不锈钢管", "法兰", "弯头", "截止阀", "止回阀", "球阀", "蝶阀", "安全阀"]
                    },
                    {
                        "name": "舱室与生活设备", "slug": "accommodation",
                        "children": ["船用空调", "冰箱", "厨房设备", "卫生洁具", "家具", "通风设备"]
                    },
                    {
                        "name": "维修工具与量具", "slug": "tools-measuring",
                        "children": ["焊接", "切割", "打磨", "扭矩扳手", "压力表", "万用表", "探伤工具"]
                    }
                ]
            },
            {
                "name": "船舶物料", "name_en": "Ship Stores", 
                "slug": "ship-stores",
                "children": [
                    {
                        "name": "甲板物料", "slug": "deck-stores",
                        "children": ["缆绳", "钢丝绳", "纤维绳", "引缆", "撇缆绳", "船用帆布", "防雨罩", "苫布", "绑带", "除锈工具", "铲刀", "钢丝刷", "打磨片", "油漆", "稀料", "防锈漆", "防污漆", "船壳漆", "甲板漆", "滚筒", "毛刷", "油灰刀", "搅拌器", "拖布", "拖把", "水桶", "扫帚", "垃圾斗", "安全绳", "安全带", "安全帽", "防护鞋", "手套", "护目镜", "卸扣", "卡头", "花篮螺丝", "链条", "防滑垫"]
                    },
                    {
                        "name": "机舱物料", "slug": "engine-stores",
                        "children": ["润滑油", "机油", "齿轮油", "液压油", "冷却液", "清洗剂", "除油剂", "除垢剂", "除锈剂", "松动剂", "密封胶", "玻璃胶", "耐高温胶", "生料带", "盘根", "填料", "O型圈", "垫片", "石棉板", "四氟垫", "砂纸", "百洁布", "擦拭布", "棉纱", "破布", "螺栓", "螺母", "平垫", "弹垫", "膨胀螺丝", "焊条", "焊丝", "焊粉", "割嘴", "焊枪配件", "皮带", "软管", "卡箍", "快速接头"]
                    },
                    {
                        "name": "厨房与生活物料", "slug": "provision-cabin-stores",
                        "children": ["大米", "面粉", "食用油", "调味品", "速冻食品", "罐头", "饮用水", "饮料", "一次性餐具", "纸巾", "垃圾袋", "洗洁精", "清洁消毒剂", "洗衣液", "肥皂", "洗发水", "沐浴用品", "床单", "被罩", "枕套", "毛巾", "浴巾"]
                    },
                    {
                        "name": "劳保与安全物料", "slug": "safety-protective-gear",
                        "children": ["工作服", "防寒服", "雨衣", "雨鞋", "防护手套", "耐油手套", "电焊手套", "防毒口罩", "防尘口罩", "防护面罩", "应急药品", "创可贴", "消毒棉", "急救包", "防滑垫", "防撞条", "安全标识牌"]
                    },
                    {
                        "name": "航海与文书物料", "slug": "navigation-stationery",
                        "children": ["航海日志", "轮机日志", "车钟记录", "报表单据", "海图", "航海图书", "航路指南", "Tide Tables", "笔", "本", "文件夹", "打印纸", "油墨", "碳带", "印章用品", "胶水", "订书机", "装订用品"]
                    },
                    {
                        "name": "防污与环保物料", "slug": "anti-pollution",
                        "children": ["吸油毡", "吸油索", "围油栏", "溢油应急套件", "垃圾分类袋", "污水袋", "船舶垃圾处理袋", "油水分离器配件", "滤油材料", "消毒药剂"]
                    },
                    {
                        "name": "应急与杂项物料", "slug": "emergency-miscellaneous",
                        "children": ["手电筒", "应急灯", "电池", "充电器", "工具包", "工具箱", "零件盒", "扎带", "铁丝", "铜丝", "铝丝", "船用标识", "贴纸", "告示牌", "标语"]
                    }
                ]
            }
        ]

        # --- Service Categories ---
        service_data = [
            {
                "name": "船舶检验与船级社服务", "slug": "classification-survey",
                "children": ["船舶入级检验", "船舶法定检验", "船舶年度检验", "设备检验与取证", "船舶公证检验", "无损检测", "测厚检验", "船舶适航证书办理"]
            },
            {
                "name": "船舶设计与工程服务", "slug": "design-engineering",
                "children": ["船舶总体设计", "船体结构设计", "轮机设计", "电气自动化设计", "内装设计", "图纸送审", "改装方案设计", "船舶稳性计算"]
            },
            {
                "name": "船舶修理与航修服务", "slug": "repair-voyage-repair",
                "children": [
                    {
                        "name": "航修（海上/航行中抢修）", "slug": "voyage-repair",
                        "children": ["海上应急抢修", "靠泊航修", "设备故障紧急处理", "水下检查与简易维修"]
                    },
                    {
                        "name": "厂修服务", "slug": "dockyard-repair",
                        "children": ["船体维修", "甲板机械维修", "主机维修", "管系维修", "电气设备维修", "舵系维修"]
                    },
                    {
                        "name": "坞修服务", "slug": "dry-docking",
                        "children": ["进坞出坞服务", "船体清洁", "螺旋桨检修", "防污漆施工"]
                    }
                ]
            },
            {
                "name": "轮机与动力系统服务", "slug": "engine-power-system",
                "children": ["主机保养", "发电机维修", "增压器维修", "分油机检修", "燃油系统维修", "机舱辅机维保"]
            },
            {
                "name": "电气与自动化服务", "slug": "electrical-automation-service",
                "children": ["电气系统检修", "配电板维护", "自动化系统调试", "监测报警系统服务", "变频器维修", "电路改造"]
            },
            {
                "name": "导航与通导设备服务", "slug": "navigation-communication-service",
                "children": ["雷达安装", "AIS检修", "测深仪校准", "导航设备检测", "EPIRB检测"]
            },
            {
                "name": "消防与救生设备服务", "slug": "fire-lifesaving-service",
                "children": ["消防系统检测", "灭火器充装", "CO₂系统检测", "救生艇年检", "救生设备证书"]
            },
            {
                "name": "船舶涂装与防腐服务", "slug": "painting-corrosion",
                "children": ["船体除锈", "油漆施工", "防腐工程", "特殊区域防腐"]
            },
            {
                "name": "水下工程服务", "slug": "underwater-works",
                "children": ["水下检查", "水下清洗", "水下堵漏", "海底阀门操作"]
            },
            {
                "name": "船舶维保与托管服务", "slug": "maintenance-management",
                "children": ["维保方案制定", "定点维保", "船舶管家", "状态监测"]
            },
            {
                "name": "备件供应与技术支持", "slug": "spares-technical-support",
                "children": ["备件代采", "备件送检", "进口设备支持", "安装指导"]
            },
            {
                "name": "船舶咨询与认证服务", "slug": "consulting-certification",
                "children": ["船舶技术咨询", "改装评估", "合规检查", "体系辅导"]
            },
            {
                "name": "海商与海事技术服务", "slug": "maritime-technical",
                "children": ["事故分析", "损坏评估", "海事公证", "买卖尽调"]
            }
        ]

        # --- Crew Categories ---
        crew_data = [
            {
                "name": "甲板部 (Deck Department)", "slug": "deck-department",
                "children": ["船长 (Captain)", "大副 (Chief Officer)", "二副 (2nd Officer)", "三副 (3rd Officer)", "水手长 (Bosun)", "一水 (AB)", "二水 (OS)", "甲板实习生 (Deck Cadet)"]
            },
            {
                "name": "轮机部 (Engine Department)", "slug": "engine-department",
                "children": ["轮机长 (Chief Engineer)", "大管轮 (2nd Engineer)", "二管轮 (3rd Engineer)", "三管轮 (4th Engineer)", "电机员 (ETO)", "机工长 (No.1 Oiler)", "机工 (Oiler)", "抹油 (Wiper)", "铜匠 (Fitter)", "轮机实习生 (Engine Cadet)"]
            },
            {
                "name": "事务部 (Catering Department)", "slug": "catering-department",
                "children": ["大厨 (Chief Cook)", "二厨 (2nd Cook)", "服务生 (Messman/Steward)"]
            }
        ]

        # --- Helper Function ---
        def create_categories(model_class, data_list, parent=None):
            for item in data_list:
                name = item.get("name")
                slug = item.get("slug")
                if not slug:
                    # Simple slug generation fallback
                    slug = f"cat-{abs(hash(name))}"
                
                # Check if exists
                cat, created = model_class.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'parent': parent
                    }
                )
                
                if created:
                    self.stdout.write(f"Created {model_class.__name__}: {name}")
                else:
                    self.stdout.write(f"Exists {model_class.__name__}: {name}")
                    # Update parent if needed
                    if cat.parent != parent:
                        cat.parent = parent
                        cat.save()

                # Handle Children
                children = item.get("children", [])
                if children:
                    # If children is a list of strings (leaf nodes)
                    if isinstance(children[0], str):
                        for child_name in children:
                            child_slug = f"{slug}-{abs(hash(child_name))}"[:50] # Simple unique slug
                            child_cat, child_created = model_class.objects.get_or_create(
                                slug=child_slug,
                                defaults={
                                    'name': child_name,
                                    'parent': cat
                                }
                            )
                            if child_created:
                                self.stdout.write(f"  -> Created Child: {child_name}")
                    # If children is a list of dicts (nested)
                    elif isinstance(children[0], dict):
                        create_categories(model_class, children, parent=cat)

        # --- Execution ---
        self.stdout.write("--- Populating Store Categories ---")
        create_categories(Category, store_data)

        self.stdout.write("--- Populating Service Categories ---")
        create_categories(ServiceCategory, service_data)
        
        self.stdout.write("--- Populating Crew Categories ---")
        create_categories(JobPosition, crew_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated categories.'))

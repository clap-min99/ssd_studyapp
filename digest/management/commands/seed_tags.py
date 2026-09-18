from django.core.management.base import BaseCommand
from digest.models import Tag

TAGS = [
    ('ftl', 'FTL', 'FTL(Flash Translation Layer), 웨어 레벨링, 가비지 컬렉션 등 SSD 내부 데이터 매핑/관리 기술', 'ssd'),
    ('nand', 'NAND', '3D NAND 셀 구조, QLC/PLC 등 낸드 공정 및 셀 기술', 'ssd'),
    ('interface', '인터페이스', 'PCIe, NVMe 등 SSD와 시스템 간 연결 인터페이스 표준', 'ssd'),
    ('controller', '컨트롤러', 'SSD 컨트롤러 칩 설계, ASIC/펌웨어 아키텍처', 'ssd'),
    ('reliability', '신뢰성', '결함분석, 수명, ECC 등 신뢰성 관련 이슈', 'ssd'),
    ('emerging', '차세대', 'CXL, PIM 등 차세대 메모리/컴퓨팅 기술', 'ssd'),
    ('market-ssd', '메모리 시장', '삼성, SK하이닉스, 마이크론 등 메모리 기업 실적/투자 동향', 'ssd'),
    ('autosar', 'AUTOSAR', 'AUTOSAR, ISO 26262 등 차량용 SW 플랫폼 및 표준', 'automotive'),
    ('adas', 'ADAS', '자율주행, ADAS 관련 기술 및 이슈', 'automotive'),
    ('semiconductor', '차량용 반도체', '차량용 반도체, ECU 관련 기술', 'automotive'),
    ('battery', '배터리', '배터리, BMS(배터리 관리 시스템) 관련 기술', 'automotive'),
    ('market-auto', '자동차 시장', '자동차 산업/시장 동향', 'automotive'),
]

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for slug, name, desc, cat in TAGS:
            Tag.objects.update_or_create(slug=slug, defaults={'name': name, 'description': desc, 'category': cat})
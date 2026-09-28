from django.core.management.base import BaseCommand
from digest.models import Tag

# (slug, name, description, category, order, prerequisite_slug)
# order=0 -> 정해진 학습 순서가 없는 일반 분류 태그 (커리큘럼 챕터 아님)
TAGS = [
    ('nand', 'NAND 기초', '셀 구조, SLC~QLC, P/E 사이클 등 3D NAND 셀/공정 기술', 'ssd', 1, None),
    ('interface', '호스트 인터페이스', 'PCIe, NVMe 등 SSD와 시스템 간 연결 인터페이스 표준', 'ssd', 2, 'nand'),
    ('ftl', 'FTL', 'FTL(Flash Translation Layer), 웨어 레벨링, 가비지 컬렉션 등 SSD 내부 데이터 매핑/관리 기술', 'ssd', 3, 'interface'),
    ('controller', '컨트롤러 아키텍처', 'SSD 컨트롤러 칩 설계, 채널/웨이 구조, 펌웨어 아키텍처', 'ssd', 4, 'ftl'),
    ('reliability', '신뢰성', '결함분석, 수명, ECC, LDPC 등 신뢰성 관련 이슈', 'ssd', 5, 'controller'),
    ('emerging', '차세대', 'CXL, ZNS, PIM 등 차세대 메모리/컴퓨팅 기술', 'ssd', 6, 'reliability'),
    ('market-ssd', '메모리 시장', '삼성, SK하이닉스, 마이크론 등 메모리 기업 실적/투자 동향', 'ssd', 0, None),
    ('vehicle-arch', '차량 전자 구조', 'ECU/MCU, Domain vs Zonal 아키텍처 등 차량 E/E 구조 기술', 'automotive', 1, None),
    ('vehicle-comm', '차량 통신', 'CAN, Automotive Ethernet, SOME/IP, DoIP 등 차량 내부 통신 기술', 'automotive', 2, 'vehicle-arch'),
    ('autosar', 'AUTOSAR & SDV 플랫폼', 'AUTOSAR Classic/Adaptive, SDV 소프트웨어 플랫폼과 OTA', 'automotive', 3, 'vehicle-comm'),
    ('functional-safety', '기능안전과 보안', 'ISO 26262/ASIL, TARA·UNECE R155 등 기능안전·사이버보안 표준', 'automotive', 4, 'autosar'),
    ('adas', 'ADAS/응용 SW', '자율주행, ADAS, 섀시 통합 제어 등 차량 응용 소프트웨어', 'automotive', 5, 'functional-safety'),
    ('semiconductor', '차량용 반도체', '차량용 반도체, 전력반도체 관련 기술', 'automotive', 0, None),
    ('battery', '배터리', '배터리, BMS(배터리 관리 시스템) 관련 기술', 'automotive', 0, None),
    ('market-auto', '자동차 시장', '자동차 산업/시장 동향', 'automotive', 0, None),
]

class Command(BaseCommand):
    help = "태그(=챕터) 시드 데이터를 채운다. 이름/설명/순서/선행 챕터를 갱신한다."

    def handle(self, *args, **kwargs):
        for slug, name, desc, cat, order, _ in TAGS:
            Tag.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'category': cat, 'order': order},
            )

        # prerequisite는 대상 Tag가 먼저 존재해야 하므로 전부 만든 뒤 별도로 연결한다
        for slug, *_rest, prereq_slug in TAGS:
            tag = Tag.objects.get(slug=slug)
            tag.prerequisite = Tag.objects.filter(slug=prereq_slug).first() if prereq_slug else None
            tag.save(update_fields=['prerequisite'])

        self.stdout.write(self.style.SUCCESS(f"{len(TAGS)}개 태그 시드 완료"))

# ========================
# 컨텍스트 → 향수 데이터 매핑 테이블
# ========================

SPACE_TO_PLACE: dict[str, list[str]] = {
    "bedroom": ["Bedroom", "Dressing Room", "Vanity", "Nursery"],
    "livingroom": ["Living Room", "Lounge", "Sunroom", "Dining Room"],
    "bathroom": ["Bathroom", "Powder Room"],
    "study": ["Study", "Library", "Office", "Reading Room", "Workspace"],
    "kitchen": ["Kitchen", "Dining Room"],
    "office": ["Office", "Workspace", "Studio"],
    "entryway": ["Entryway"],
}

# mood 매핑
MOOD_TO_TAGS: dict[str, list[str]] = {
    "calm": ["차분한", "잔잔한", "고요한", "안정적인", "조용한", "정갈한"],
    "cozy": ["포근한", "따뜻한", "아늑한", "부드러운", "온기있는"],
    "fresh": ["상쾌한", "산뜻한", "청량한", "가벼운", "싱그러운", "맑은", "깨끗한", "투명한"],
    "romantic": ["로맨틱", "달콤한", "사랑스러운", "플로럴", "섬세한"],
    "focus": ["드라이한", "절제된", "집중되는", "정돈된", "미니멀한", "깊은"],
    "energetic": ["활기 있는", "경쾌한", "밝은", "선명한", "활기있는"],
    "luxury": ["고급스러운", "우아한", "깊이감 있는", "성숙한", "이국적인", "특별한"],
    "sweet": ["달콤한", "사랑스러운", "과즙감 있는", "섬세한"],
}

# mood → 선호 카테고리 매핑
MOOD_TO_CATEGORY: dict[str, list[str]] = {
    "calm": ["woody", "musk"],
    "cozy": ["woody", "powdery", "amber"],
    "fresh": ["citrus", "aquatic", "green"],
    "romantic": ["floral"],
    "focus": ["woody", "green"],
    "energetic": ["citrus", "spicy"],
    "luxury": ["woody", "amber", "floral"],
    "sweet": ["floral", "fruity"],
}

# mood → 프로필 기준 매핑
MOOD_TO_PROFILE: dict[str, dict[str, int]] = {
    "calm": {"warmth": 50, "softness": 60},
    "cozy": {"warmth": 65, "softness": 70},
    "fresh": {"freshness": 70},
    "romantic": {"sweetness": 50, "softness": 60},
    "focus": {"depth": 70},
    "energetic": {"freshness": 60},
    "luxury": {"depth": 75, "warmth": 60},
    "sweet": {"sweetness": 55},
}

# intensity 매핑 (intensity 수치 기준)
INTENSITY_RANGE: dict[str, tuple[int, int]] = {
    "light": (0, 60),
    "medium": (55, 75),
    "strong": (70, 100),
}

# time → 선호 season 매핑
TIME_TO_SEASON: dict[str, list[str]] = {
    "morning": ["spring", "summer"],
    "daytime": ["spring", "summer"],
    "evening": ["autumn", "winter"],
    "night": ["autumn", "winter"],
}

# time → 프로필 기준 매핑
TIME_TO_PROFILE: dict[str, dict[str, int]] = {
    "morning": {"freshness": 60},
    "daytime": {"freshness": 50},
    "evening": {"warmth": 60, "depth": 55},
    "night": {"warmth": 65, "softness": 65},
}

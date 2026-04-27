import json
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types


class GeminiClient:
    def __init__(self, model_name: str | None = None) -> None:
        self.client = genai.Client(api_key=settings.HHJ_GEMINI_KEY)
        self.model_name = model_name or settings.GEMINI_MODEL

    def analyze_scent_from_image(self, image_bytes: bytes) -> dict[str, Any]:
        prompt = """
                너는 수석 조향사이자 이미지 무드 분석가야. 
                주어진 이미지를 분석하여 느껴지는 분위기와 가장 잘 어울리는 향기 정보를 분석해줘.

                [중요] 시스템 매칭 정확도를 위해, tags와 keywords는 반드시 아래 제공된 <허용된 목록>에 있는 단어 중에서만 정확히 일치하게 선택해야 해. 임의로 단어를 변형하거나 새로운 단어를 생성하지 마.

                <허용된 Tags 목록>
                가벼운, 강렬한, 개성 있는, 고급스러운, 고요한, 과즙감 있는, 깨끗한, 깊은, 깊이감 있는, 내추럴, 넓은, 달콤한, 데일리, 드라이한, 따뜻한, 로맨틱, 맑은, 묵직한, 미니멀한, 밝은, 부드러운, 사랑스러운, 산뜻한, 상쾌한, 선명한, 성숙한, 세련된, 섬세한, 스모키한, 스파이시한, 시원한, 싱그러운, 아늑한, 안정적인, 여유로운, 우아한, 은은한, 이국적인, 자연스러운, 잔잔한, 절제된, 정갈한, 정돈된, 조용한, 집중되는, 차분한, 청량한, 투명한, 특별한, 파우더리, 편안한, 포근한, 풍부한, 플로럴, 허브한, 환기되는, 활기 있는

                <허용된 Keywords 목록>
                가을밤, 개운함, 고급스러움, 고요함, 과즙상, 기분전환, 단정함, 달콤함, 데일리, 데이트, 드라이우드, 런드리, 로맨틱무드, 리프레시, 명상, 모닝루틴, 몰입, 무채색, 무화과, 밤공기, 보송보송, 봄꽃, 비누향, 비오는날, 비타민, 사색, 산책, 산뜻함, 살냄새, 상쾌함, 생기, 생화, 서재, 샤워코롱, 섬유유연제, 성숙함, 세련됨, 소녀감성, 수면, 순수, 스모키, 싱그러움, 아늑함, 아침햇살, 안정감, 에너지, 여리여리, 여름바다, 여유, 연말무드, 오리엔탈, 오후의휴식, 오피스, 온기, 우아함, 운동, 유니크, 이국적, 이불속, 장미정원, 저녁무드, 절제미, 청량함, 캠프파이어, 캐시미어니트, 크리미우디, 트렌디, 티타임, 파우더룸, 파우더리, 파티무드, 편안함, 포근함, 플랜테리어, 햇볕, 허브, 호불호없는, 호텔라운지, 황혼, 환기, 휴식

                반드시 아래의 JSON 형식으로만 응답해야 해. 다른 부가적인 설명은 절대 금지야.
                {
                    "tags": ["위 <허용된 Tags 목록> 중에서 이미지와 가장 잘 어울리는 태그를 정확히 2개 골라 배열(List)로 작성"],
                    "keywords": ["위 <허용된 Keywords 목록> 중에서 이미지 분위기를 나타내는 키워드를 정확히 3개 골라 배열(List)로 작성"],
                    "intensity": 1부터 5까지의 정수 (향의 강도, 1:매우 은은함, 5:매우 강렬함),
                    "comment": "이 향을 추천하는 이유와 이미지의 분위기에 대한 4~5줄의 감성적인 설명 (반드시 한국어로 작성)"
                }
                """

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        )

        contents: list[Any] = [
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ]

        result = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        text = result.text
        if not text:
            raise ValueError("AI 서버로부터 응답 텍스트를 받지 못했습니다.")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI가 올바른 JSON 형식을 반환하지 않았습니다. {e}")

        if not isinstance(parsed, dict):
            raise ValueError(f"AI 응답이 JSON 객체 형식이 아닙니다: {type(parsed)}")

        return parsed

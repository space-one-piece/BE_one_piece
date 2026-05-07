import io
import logging
from typing import Any

import cv2
import numpy as np
from colorthief import ColorThief  # type: ignore

logger = logging.getLogger(__name__)


class ColorAnalysisUtil:
    MAX_STD_DEV = 127.0
    HEX_FORMAT = "#{:02X}{:02X}{:02X}"

    @staticmethod
    def extract_colors(image_bytes: bytes) -> dict[str, Any]:
        try:
            image_stream = io.BytesIO(image_bytes)
            image_stream.seek(0)

            color_thief = ColorThief(image_stream)
            dominant_rgb = color_thief.get_color(quality=5)

            dominant_hex = ColorAnalysisUtil.HEX_FORMAT.format(*dominant_rgb)

            np_arr = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img_cv is None:
                raise ValueError("OpenCV에서 이미지를 디코딩할 수 없습니다.")

            hsv_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

            _, s, v = cv2.split(hsv_img)

            avg_saturation = (np.mean(s) / 255.0) * 100  # 평균채도
            avg_brightness = (np.mean(v) / 255.0) * 100  # 평균밝기

            gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            std_dev = float(np.std(gray_img))

            contrast_ratio = min((std_dev / ColorAnalysisUtil.MAX_STD_DEV) * 100, 100.0)

            return {
                "dominant_hex": dominant_hex,
                "contrast": round(contrast_ratio, 1),
                "brightness": round(avg_brightness, 1),
                "saturation": round(avg_saturation, 1),
            }

        except Exception as e:
            logger.error("컬러 데이터 추출 중 예기치 않은 에러 발생", exc_info=True)
            raise RuntimeError("컬러 데이터 추출에 실패했습니다.") from e

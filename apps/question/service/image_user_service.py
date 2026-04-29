import base64
import json

from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import image_url_edit
from apps.question.google_ai_studio import Gemini
from apps.question.models import QuestionsResults
from apps.question.service.service import QuestServices
from apps.users.models.models import User


class ImageUserService(QuestServices, Gemini):
    @classmethod
    def image_new(cls, user_id: int) -> str | None:
        quest_data = get_list_or_404(QuestionsResults, user=user_id)

        if quest_data is None:
            raise Http404

        json_data = [json.loads(item.questions_json) for item in quest_data if item.questions_json]

        prompt = f"""
                {json_data}
                with this data
                dreamy pastel abstract background, soft blurred gradient, 
                airy cloud-like color blending, very light pink, baby blue, 
                ivory, pale lavender, subtle creamy tones, smooth and hazy transitions, 
                ethereal atmosphere, minimal abstract wallpaper, soft focus, delicate glow, 
                clean and bright, no sharp edges, no objects, no text, high resolution sharp lines, 
                high contrast, vivid colors, strong shadows, detailed objects, flowers, people, text, 
                patterns, noise, grain, geometric shapes
            """
        image_data = cls.image_gemini(prompt)
        return image_data

    @classmethod
    def user_profile_save(cls, user_id: int, image_url: str) -> None:
        if image_url is None:
            raise Http404

        user_data = get_object_or_404(User, pk=user_id)
        user_data.profile_image_url = image_url_edit(image_url)
        user_data.save()

    @classmethod
    def web_share(cls, user_id: int, result_id: int, division: str) -> dict[str, str]:
        if result_id is None:
            raise Http404

        result_obj = cls.result_division(result_id, division)

        ai_comment = ""
        if division == "chatbot":
            if hasattr(result_obj, "reply"):
                ai_comment = result_obj.reply if result_obj.reply else ""
        else:
            if hasattr(result_obj, "answer_ai"):
                ai_comment = getattr(result_obj, "answer_ai", "")

        scent = getattr(result_obj, "scent", None)
        if not scent:
            raise Http404

        raw_profile = scent.profile
        profile_list = []
        if isinstance(raw_profile, dict):
            for name, value in raw_profile.items():
                profile_list.append({"name": name, "value": value})
        else:
            profile_list = raw_profile

        raw_notes = scent.scent_notes
        notes_list = []
        if isinstance(raw_notes, dict):
            for key in ["top", "middle", "base"]:
                note_item = raw_notes.get(key)
                if note_item:
                    notes_list.append(note_item)

        context = {
            "scent_name": scent.name,
            "scent_image_url": image_url_cloud(scent.thumbnail_url),
            "description": scent.description,
            "ai_comment": ai_comment,  # 수정된 부분
            "profiles": profile_list,
            "notes_list": notes_list,
        }

        html_string = render_to_string("share_template.html", context)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_string)
            page.wait_for_load_state("networkidle")
            image_bytes = page.screenshot(full_page=True, type="png")
            browser.close()

        data = {"image_data": base64.b64encode(image_bytes).decode("utf-8")}

        return data

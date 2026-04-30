import base64

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import image_url_edit
from apps.question.google_ai_studio import Gemini
from apps.question.models import QuestionsResults
from apps.question.service.service import QuestServices
from apps.users.models.models import User


class ImageUserService(QuestServices, Gemini):
    @classmethod
    def image_new(cls, user_id: int) -> str | None:
        quest_data = QuestionsResults.objects.filter(user_id=user_id).order_by("created_at").first()
        image_data = ImageAnalysis.objects.filter(user_id=user_id).order_by("created_at").first()
        chat_data = ChatbotRecommendation.objects.filter(user_id=user_id).order_by("created_at").first()

        result = [obj for obj in [quest_data, image_data, chat_data] if obj is not None]

        if not result:
            raise Http404

        last_data = max(result, key=lambda x: x.created_at)

        category_data = {
            "floral": "dusty rose, soft peony pink, pale lilac, creamy coral, hints of apricot",
            "fruity": "sweet peach, pastel raspberry, soft mango yellow, pale strawberry pink, hints of apricot",
            "woody": "soft sage green, warm taupe, dusty cedar, pale sand, muted amber, ivory",
            "citrus": "pale lemon yellow, bright lime zest, soft aqua, misty white, sheer mandarin",
            "musk": "milky white, soft pearl grey, ivory silk, misty lavender, creamy beige",
            "green": "fresh mint, soft leaf green, pale pistachio, misty teal, dew-drop white",
            "spicy": "muted terracotta, soft copper, warm cinnamon, dusty gold, creamy sand",
            "powdery": "pale violet, soft baby pink, misty white, pearl silver, vanilla cream",
            "aquatic": "soft ocean blue, misty cyan, pale turquoise, airy silver, sheer seafoam",
            "amber": "warm honey gold, soft amber orange, muted bronze, deep cream, sunset glow",
        }

        if isinstance(last_data, ImageAnalysis):
            last_sent_data = last_data.recommended_scent.eng_name if last_data.recommended_scent else ""
            color_palette = category_data[last_data.recommended_scent.categories] if last_data.recommended_scent else ""
        else:
            last_sent_data = last_data.scent.eng_name if last_data.scent else ""
            color_palette = category_data[last_data.scent.categories] if last_data.scent else ""

        prompt = f"""
                {last_sent_data}
                t's perfect for this scent. Dreamy pastel abstract background, soft blurry gradation, 
                Air cloud-like color blending, ({color_palette}), 
                ivory, subtle creamy tones, soft and blurry transitions, subtle atmosphere, 
                minimal abstract wallpaper, soft focus, delicate glow, clean and bright, no sharp edges, 
                no objects, no text, high resolution clear lines.
                [Negative Prompt]
                high contrast, vivid colors, strong shadows, detailed objects, flowers, people, 
                text, pattern, noise, particles, geometric shapes, watercolor splashes, paint splatter,
                 water stains, watercolor texture, brush strokes, paint drips, liquid drips, bleeding colors, 
                 messy edges, textured paper effect, drawing texture, sketchy lines, artistic mess.
            """
        generated_image_url: str | None = cls.image_gemini(prompt)
        return generated_image_url

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

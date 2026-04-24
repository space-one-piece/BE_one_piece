from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.question.gool_ai_studio import Gemini
from apps.question.models import QuestionsResults
from apps.question.service.service import Service
from apps.users.models.models import User


class ImageUserService(Service, Gemini):
    @classmethod
    def image_new(cls, user_id: int, results_id: int) -> str | None:
        quest_data = get_object_or_404(QuestionsResults, pk=results_id)

        if quest_data.user_id != user_id:
            raise Http404

        json_data = quest_data.questions_json

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
        user_data.profile_image_url = cls.image_url_edit(image_url)
        user_data.save()

from typing import Any

from apps.analysis.models import Scent


def get_scent_list(
    category: str | None = None,
    tag: str | None = None,
    is_bestseller: bool | None = None,
    ordering: str = "-created_at",
) -> list[Scent]:
    qs = Scent.objects.all()

    if category:
        qs = qs.filter(categories__icontains=category)
    if tag:
        qs = qs.filter(tags__contains=[tag])
    if is_bestseller is not None:
        qs = qs.filter(is_bestseller=is_bestseller)

    return list(qs.order_by(ordering))


def get_scent_detail(scent_id: int) -> Scent:
    return Scent.objects.get(id=scent_id)


def create_scent(data: dict[str, Any]) -> Scent:
    return Scent.objects.create(**data)


def update_scent(scent: Scent, data: dict[str, Any]) -> Scent:
    for key, value in data.items():
        setattr(scent, key, value)
    scent.save()
    return scent


def delete_scent(scent: Scent) -> None:
    scent.delete()

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Item


def build_briefing(db: Session, limit: int = 25) -> str:
    items = db.scalars(
        select(Item)
        .where(Item.status == "aperto")
        .order_by(Item.created_at.desc())
        .limit(limit)
    ).all()

    if not items:
        return "Non risultano attività aperte."

    urgent = [x for x in items if x.priority in {"urgente", "alta"}]
    calendar = [x for x in items if x.calendar_candidate]
    waiting = [x for x in items if x.item_type == "attesa"]
    other = [x for x in items if x not in urgent and x not in calendar and x not in waiting]

    lines = ["*AlexOS — situazione aperta*"]

    def add_section(title: str, values: list[Item]) -> None:
        if not values:
            return
        lines.append(f"\n*{title}*")
        for item in values[:10]:
            due = f" — {item.due_at}" if item.due_at else ""
            lines.append(f"• [{item.folder}] {item.title}{due}")

    add_section("Urgenti / importanti", urgent)
    add_section("Appuntamenti da confermare", calendar)
    add_section("In attesa da altri", waiting)
    add_section("Altre cose aperte", other)

    lines.append("\nNon è stato inviato alcun messaggio a terzi.")
    return "\n".join(lines)

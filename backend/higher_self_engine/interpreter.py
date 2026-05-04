from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class HigherSelfReading:
    surface_request: str
    underlying_need: str
    deeper_intention: str
    guidance_note: str


class HigherSelfInterpreter:
    def interpret(self, user_input: str, session_history: Optional[list] = None) -> HigherSelfReading:
        text = (user_input or "").strip()
        t = text.lower()
        _ = session_history or []

        surface = text[:240]

        if any(x in t for x in ("застав", "надо", "должен", "must", "have to")):
            need = "конфликт между 'должен' и 'хочу'"
            intention = "найти устойчивую внутреннюю мотивацию без самонасилия"
            note = "этот человек ищет согласование воли и смысла, а не жесткую инструкцию"
        elif any(x in t for x in ("не могу", "не получается", "can't", "cannot")):
            need = "потеря опоры и страх ошибки"
            intention = "восстановить ясность и право на постепенный выбор"
            note = "этот человек ищет опору, а не инструкцию"
        elif any(x in t for x in ("как стать лучше", "better", "лучше")):
            need = "чувство недостаточности и потребность в принятии + росте"
            intention = "переход к зрелому развитию без самообесценивания"
            note = "этот человек ищет опору в ценности себя при движении вперед"
        elif any(x in t for x in ("что мне делать", "what should i do", "помоги решить", "help me decide", "решить")):
            need = "нужна поддержка в принятии решения, не только готовый ответ"
            intention = "развить автономность решения при поддержке"
            note = "этому человеку важны и поддержка, и сохранение агентности"
        else:
            need = "потребность в ясности и эмоциональной устойчивости"
            intention = "продвинуться к более цельному способу действовать"
            note = "человек ищет смысловую опору, а не просто технический совет"

        return HigherSelfReading(
            surface_request=surface,
            underlying_need=need,
            deeper_intention=intention,
            guidance_note=note,
        )

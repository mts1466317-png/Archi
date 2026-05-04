from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DistortionType(Enum):
    FEAR = "fear"  # искажение любви
    CONTROL = "control"  # искажение свободы
    MANIPULATION = "manipulation"  # искажение мудрости
    FRAGMENTATION = "fragmentation"  # искажение целостности
    EGO = "ego"  # искажение единства
    AVOIDANCE = "avoidance"  # искажение реальности


@dataclass
class DistortionSignal:
    distortion_type: DistortionType
    source: str  # что именно триггернуло
    severity: float  # 0.0 - 1.0
    description: str  # человеческое объяснение
    correction: str  # как исправить в ответе


@dataclass
class DistortionScanResult:
    has_distortions: bool
    signals: List[DistortionSignal] = field(default_factory=list)
    dominant_distortion: Optional[DistortionType] = None
    overall_severity: float = 0.0
    recommended_mode: Optional[str] = None


class DistortionDetector:
    """
    Детектор искажений — уникальное ядро системы.

    Философская основа:
    - Зло = искажённая любовь, не отдельная сила
    - Ошибка = искажение целостности, не просто ложь
    - Каждое искажение имеет источник и коррекцию
    """

    # Паттерны страха (искажение любви)
    FEAR_PATTERNS = [
        "я боюсь",
        "страшно",
        "не могу",
        "я не способен",
        "всё плохо",
        "нет смысла",
        "бесполезно",
        "никогда",
        "я неудачник",
        "у меня не получится",
        "всё рухнет",
        "я один",
        "никто не поможет",
        "это конец",
        "i'm afraid",
        "i can't",
        "it's hopeless",
        "i'm scared",
    ]

    # Паттерны контроля (искажение свободы)
    CONTROL_PATTERNS = [
        "ты должен",
        "ты обязан",
        "нужно обязательно",
        "только так",
        "нет другого пути",
        "ты не можешь",
        "запрещено",
        "нельзя",
        "ты не имеешь права",
        "заставить",
        "принудить",
        "контролировать",
        "контролируют",
        "you must",
        "you have to",
        "no choice",
        "forced to",
    ]

    # Паттерны манипуляции (искажение мудрости)
    MANIPULATION_PATTERNS = [
        "все так делают",
        "ты же умный человек",
        "если ты не сделаешь",
        "я пострадаю из-за тебя",
        "ты мне должен",
        "после всего что я",
        "докажи что",
        "докажи это",
        "если любишь то",
        "если ты меня любишь",
        "настоящий друг бы",
        "everyone does it",
        "prove it",
        "if you loved me",
    ]

    # Паттерны фрагментации (искажение целостности)
    FRAGMENTATION_PATTERNS = [
        "я разрываюсь",
        "не знаю кто я",
        "всё против меня",
        "мир несправедлив",
        "я и они",
        "свои и чужие",
        "нас предали",
        "они всегда",
        "никогда не понимают",
        "torn apart",
        "falling apart",
        "us vs them",
        "they always",
        "nobody understands",
    ]

    # Паттерны эго (искажение единства)
    EGO_PATTERNS = [
        "я лучше всех",
        "они все неправы",
        "только я понимаю",
        "я всегда прав",
        "они завидуют",
        "никто не дорос",
        "я особенный",
        "мне все должны",
        "i'm always right",
        "they're all wrong",
        "i'm special",
    ]

    # Паттерны избегания (искажение реальности)
    AVOIDANCE_PATTERNS = [
        "потом разберусь",
        "это не важно",
        "забудь об этом",
        "не хочу думать",
        "всё само пройдёт",
        "не моя проблема",
        "авось",
        "как-нибудь",
        "не сейчас",
        "i'll deal later",
        "it doesn't matter",
        "it'll fix itself",
    ]

    PATTERN_MAP = {
        DistortionType.FEAR: FEAR_PATTERNS,
        DistortionType.CONTROL: CONTROL_PATTERNS,
        DistortionType.MANIPULATION: MANIPULATION_PATTERNS,
        DistortionType.FRAGMENTATION: FRAGMENTATION_PATTERNS,
        DistortionType.EGO: EGO_PATTERNS,
        DistortionType.AVOIDANCE: AVOIDANCE_PATTERNS,
    }

    DISTORTION_DESCRIPTIONS = {
        DistortionType.FEAR: "Страх искажает любовь — человек закрывается вместо того чтобы открыться",
        DistortionType.CONTROL: "Контроль искажает свободу — подавляется агентность и выбор",
        DistortionType.MANIPULATION: "Манипуляция искажает мудрость — истина подменяется давлением",
        DistortionType.FRAGMENTATION: "Фрагментация искажает целостность — мир делится на враждебные части",
        DistortionType.EGO: "Эго искажает единство — изоляция вместо связи",
        DistortionType.AVOIDANCE: "Избегание искажает реальность — уход от того что требует внимания",
    }

    DISTORTION_CORRECTIONS = {
        DistortionType.FEAR: "Признать страх, найти что за ним стоит, вернуть любовь как опору",
        DistortionType.CONTROL: "Вернуть человеку право выбора, открыть альтернативы",
        DistortionType.MANIPULATION: "Назвать паттерн прямо, восстановить честную коммуникацию",
        DistortionType.FRAGMENTATION: "Найти общее, восстановить целостную картину",
        DistortionType.EGO: "Найти связь с другими, снизить изоляцию",
        DistortionType.AVOIDANCE: "Мягко вернуть к реальности, помочь встретить избегаемое",
    }

    MODE_RECOMMENDATIONS = {
        DistortionType.FEAR: "Mirror",
        DistortionType.CONTROL: "Challenge",
        DistortionType.MANIPULATION: "Challenge",
        DistortionType.FRAGMENTATION: "Dialogue",
        DistortionType.EGO: "Challenge",
        DistortionType.AVOIDANCE: "Help",
    }

    def scan(self, text: str) -> DistortionScanResult:
        """
        Сканирует текст на наличие искажений.
        Возвращает полный отчёт с сигналами и рекомендациями.
        """
        text_lower = text.lower()
        signals: List[DistortionSignal] = []

        for distortion_type, patterns in self.PATTERN_MAP.items():
            matched = [p for p in patterns if p in text_lower]
            if matched:
                severity = self._calculate_severity(matched, text_lower)
                signal = DistortionSignal(
                    distortion_type=distortion_type,
                    source=", ".join(matched[:3]),
                    severity=severity,
                    description=self.DISTORTION_DESCRIPTIONS[distortion_type],
                    correction=self.DISTORTION_CORRECTIONS[distortion_type],
                )
                signals.append(signal)

        if not signals:
            return DistortionScanResult(has_distortions=False)

        # Определяем доминирующее искажение
        dominant = max(signals, key=lambda s: s.severity)
        overall_severity = sum(s.severity for s in signals) / len(signals)

        return DistortionScanResult(
            has_distortions=True,
            signals=signals,
            dominant_distortion=dominant.distortion_type,
            overall_severity=round(overall_severity, 2),
            recommended_mode=self.MODE_RECOMMENDATIONS.get(dominant.distortion_type),
        )

    def _calculate_severity(self, matched: list, text: str) -> float:
        """
        Рассчитывает серьёзность искажения.
        Базовая: количество совпадений + длина текста
        """
        base = min(len(matched) * 0.25, 0.75)
        # Усиление если текст короткий и концентрированный
        density_bonus = 0.25 if len(text) < 200 and len(matched) > 1 else 0.0
        return round(min(base + density_bonus, 1.0), 2)

    def get_correction_prompt(self, result: DistortionScanResult) -> str:
        """
        Генерирует инструкцию для pipeline:
        как скорректировать ответ с учётом искажений.
        """
        if not result.has_distortions:
            return ""

        lines = ["[DISTORTION CORRECTION ACTIVE]"]
        for signal in result.signals:
            lines.append(f"- {signal.distortion_type.value.upper()}: {signal.correction}")
        lines.append(f"Recommended mode: {result.recommended_mode or 'Mirror'}")
        return "\n".join(lines)

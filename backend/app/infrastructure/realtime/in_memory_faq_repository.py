from typing import List, Optional

from app.domain.entities.faq import FaqEntry


class InMemoryFaqRepository:
    def __init__(self, entries: Optional[List[FaqEntry]] = None) -> None:
        self._entries = entries or _default_entries()

    def list_entries(self) -> List[FaqEntry]:
        return list(self._entries)


def _default_entries() -> List[FaqEntry]:
    return [
        FaqEntry(
            id="order-status",
            question="estado de una orden",
            answer="Puedes revisar el estado de tu orden en el historial de compras.",
            keywords=["estado", "orden", "pedido"],
        ),
        FaqEntry(
            id="payment-methods",
            question="metodos de pago",
            answer="Aceptamos tarjeta, transferencia y pago en efectivo en tiendas autorizadas.",
            keywords=["metodo", "pago", "tarjeta", "transferencia"],
        ),
        FaqEntry(
            id="shipping-times",
            question="tiempos de envio",
            answer="Los envios tardan entre 2 y 5 dias habiles segun tu ubicacion.",
            keywords=["envio", "tiempo", "entrega", "dias"],
        ),
        FaqEntry(
            id="support-hours",
            question="horarios de atencion",
            answer="Atendemos de lunes a viernes de 9:00 a 18:00.",
            keywords=["horario", "atencion", "soporte"],
        ),
    ]

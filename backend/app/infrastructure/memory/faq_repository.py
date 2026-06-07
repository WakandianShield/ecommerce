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
        FaqEntry(
            id="vinyl-genres",
            question="generos de vinilos",
            answer=(
                "Tenemos vinilos de pop, rock ingles, rock espanol, rap, hip hop, trap, "
                "reggae, jazz, metal, grunge, post punk, trance, banda, mariachi, boleros "
                "y corridos. Revisa el catalogo para el listado actualizado."
            ),
            keywords=["generos", "genero", "categorias", "catalogo", "vinilos"],
        ),
        FaqEntry(
            id="stock-info",
            question="stock disponible",
            answer=(
                "En cada producto veras el stock actual. Si aparece agotado, "
                "vuelve a revisar mas tarde."
            ),
            keywords=["stock", "disponible", "agotado", "existencia"],
        ),
        FaqEntry(
            id="how-to-buy",
            question="como comprar",
            answer="Agrega el vinilo al carrito y completa el pago en checkout.",
            keywords=["comprar", "carrito", "checkout", "pagar"],
        ),
        FaqEntry(
            id="recommendations",
            question="recomendaciones",
            answer=(
                "Si buscas clasicos, mira pop y rock ingles; para ritmos urbanos, "
                "revisa rap, hip hop y trap."
            ),
            keywords=["recomendar", "recomendacion", "sugerir", "recomendaciones"],
        ),
        FaqEntry(
            id="vinyl-care",
            question="cuidado de vinilos",
            answer=(
                "Guarda tus vinilos en funda, evita el polvo y el calor, "
                "y manipula siempre por los bordes."
            ),
            keywords=["cuidar", "limpiar", "guardar", "vinilo", "vinilos"],
        ),
        FaqEntry(
            id="edition-details",
            question="detalles de edicion",
            answer="La descripcion del producto indica detalles de edicion y lanzamiento.",
            keywords=["edicion", "estado", "detalle", "lanzamiento"],
        ),
    ]

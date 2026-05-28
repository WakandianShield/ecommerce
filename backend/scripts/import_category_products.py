from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from sqlalchemy import select

from app.application.use_cases.product_service import ProductService
from app.domain.entities.product import ProductCreate, ProductUpdate
from app.domain.errors import ValidationError
from app.infrastructure.database.connection import SessionLocal, init_db
from app.infrastructure.database.models import ProductModel
from app.infrastructure.database.repositories import SqlAlchemyProductRepository


@dataclass
class ParsedProduct:
    name: str
    description: Optional[str]
    price_cents: Optional[int]
    category: Optional[str]
    image_url: Optional[str]


class CategoryPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.category_title: Optional[str] = None
        self.products: list[ParsedProduct] = []

        self._in_category_title = False
        self._category_buf: list[str] = []

        self._in_card = False
        self._card_depth = 0
        self._current: dict[str, Optional[str]] | None = None

        self._in_image_box = False
        self._image_box_depth = 0

        self._in_name = False
        self._name_buf: list[str] = []

        self._in_desc = False
        self._desc_buf: list[str] = []

        self._in_price = False
        self._price_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        classes = set((attr_map.get("class") or "").split())

        if tag == "h1" and "category-title" in classes:
            self._in_category_title = True
            self._category_buf = []

        if tag == "div" and "item-card" in classes:
            self._in_card = True
            self._card_depth = 1
            self._current = {
                "name": None,
                "description": None,
                "price_text": None,
                "image_url": None,
            }
            return

        if self._in_card and tag == "div":
            self._card_depth += 1

        if self._in_card and tag == "div" and "image-box" in classes:
            self._in_image_box = True
            self._image_box_depth = 1
            return

        if self._in_image_box and tag == "div":
            self._image_box_depth += 1

        if self._in_card and self._in_image_box and tag == "img":
            src = attr_map.get("src") or ""
            if src and self._current is not None:
                self._current["image_url"] = src

        if self._in_card and tag == "h4":
            self._in_name = True
            self._name_buf = []

        if self._in_card and tag == "p" and "product-desc" in classes:
            self._in_desc = True
            self._desc_buf = []

        if self._in_card and tag == "span" and "price" in classes:
            self._in_price = True
            self._price_buf = []

        if self._in_card and self._in_desc and tag == "br":
            self._desc_buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self._in_category_title:
            self.category_title = _normalize_text("".join(self._category_buf))
            self._in_category_title = False
            self._category_buf = []

        if self._in_card and tag == "h4" and self._in_name:
            if self._current is not None:
                self._current["name"] = _normalize_text("".join(self._name_buf))
            self._in_name = False
            self._name_buf = []

        if self._in_card and tag == "p" and self._in_desc:
            if self._current is not None:
                self._current["description"] = _normalize_description("".join(self._desc_buf))
            self._in_desc = False
            self._desc_buf = []

        if self._in_card and tag == "span" and self._in_price:
            if self._current is not None:
                self._current["price_text"] = _normalize_text("".join(self._price_buf))
            self._in_price = False
            self._price_buf = []

        if self._in_image_box and tag == "div":
            self._image_box_depth -= 1
            if self._image_box_depth <= 0:
                self._in_image_box = False
                self._image_box_depth = 0

        if self._in_card and tag == "div":
            self._card_depth -= 1
            if self._card_depth <= 0:
                self._finalize_card()
                self._in_card = False
                self._card_depth = 0
                self._current = None

    def handle_data(self, data: str) -> None:
        if self._in_category_title:
            self._category_buf.append(data)
        if self._in_name:
            self._name_buf.append(data)
        if self._in_desc:
            self._desc_buf.append(data)
        if self._in_price:
            self._price_buf.append(data)

    def _finalize_card(self) -> None:
        if not self._current:
            return
        name = (self._current.get("name") or "").strip()
        if not name:
            return
        price_text = self._current.get("price_text") or ""
        price_cents = _parse_price_cents(price_text)
        description = self._current.get("description")
        image_url = self._current.get("image_url")
        self.products.append(
            ParsedProduct(
                name=name,
                description=description,
                price_cents=price_cents,
                category=None,
                image_url=image_url,
            )
        )


def _normalize_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def _normalize_description(value: str) -> Optional[str]:
    parts = [part.strip() for part in value.replace("\xa0", " ").split("\n")]
    parts = [part for part in parts if part]
    return "\n".join(parts) if parts else None


def _parse_price_cents(value: str) -> Optional[int]:
    cleaned = re.sub(r"[^0-9.]", "", value or "")
    if not cleaned:
        return None
    try:
        amount = Decimal(cleaned)
    except Exception:
        return None
    cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return cents if cents > 0 else None


def _derive_category_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").title()


def parse_category_file(path: Path) -> tuple[str, list[ParsedProduct]]:
    parser = CategoryPageParser()
    content = path.read_text(encoding="utf-8")
    parser.feed(content)
    parser.close()
    category = parser.category_title or _derive_category_from_filename(path)
    products: list[ParsedProduct] = []
    for product in parser.products:
        products.append(
            ParsedProduct(
                name=product.name,
                description=product.description,
                price_cents=product.price_cents,
                category=category,
                image_url=product.image_url,
            )
        )
    return category, products


def collect_products(categories_dir: Path) -> list[ParsedProduct]:
    products: list[ParsedProduct] = []
    for path in sorted(categories_dir.glob("*.html")):
        _, items = parse_category_file(path)
        products.extend(items)
    return products


def upsert_products(
    products: Iterable[ParsedProduct],
    default_stock: int,
    is_active: bool,
    mode: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"Dry run: {len(list(products))} productos encontrados.")
        return

    init_db()

    created = 0
    updated = 0
    skipped = 0
    invalid = 0

    with SessionLocal() as session:
        repo = SqlAlchemyProductRepository(session)
        service = ProductService(repo)

        for product in products:
            if not product.price_cents:
                print(f"Omitido (sin precio): {product.name}")
                invalid += 1
                continue

            if not product.category:
                print(f"Omitido (sin categoria): {product.name}")
                invalid += 1
                continue

            stmt = select(ProductModel).where(
                ProductModel.name == product.name,
                ProductModel.category == product.category,
            )
            existing = session.execute(stmt).scalars().first()

            if existing and mode == "insert-only":
                skipped += 1
                continue

            try:
                if existing:
                    data = ProductUpdate(
                        description=product.description,
                        price_cents=product.price_cents,
                        stock=default_stock,
                        category=product.category,
                        image_url=product.image_url,
                        is_active=is_active,
                    )
                    service.update_product(existing.id, data)
                    updated += 1
                else:
                    data = ProductCreate(
                        name=product.name,
                        description=product.description,
                        price_cents=product.price_cents,
                        stock=default_stock,
                        category=product.category,
                        image_url=product.image_url,
                        is_active=is_active,
                    )
                    service.create_product(data)
                    created += 1
            except ValidationError as exc:
                print(f"Omitido (validacion): {product.name} -> {exc}")
                invalid += 1

    print(
        "Importacion completada. "
        f"Creados: {created}, Actualizados: {updated}, Omitidos: {skipped}, Invalidos: {invalid}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importa productos desde las paginas HTML de categories."
    )
    parser.add_argument(
        "--categories-dir",
        default=str(ROOT.parent / "frontend" / "categories"),
        help="Ruta al directorio frontend/categories",
    )
    parser.add_argument(
        "--stock",
        type=int,
        default=10,
        help="Stock inicial para cada producto",
    )
    parser.add_argument(
        "--inactive",
        action="store_true",
        help="Marca los productos como inactivos",
    )
    parser.add_argument(
        "--mode",
        choices=["upsert", "insert-only"],
        default="upsert",
        help="upsert actualiza si existe; insert-only solo inserta nuevos",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo muestra cuantos productos se detectan",
    )

    args = parser.parse_args()
    categories_dir = Path(args.categories_dir)
    if not categories_dir.exists():
        raise SystemExit(f"No existe el directorio: {categories_dir}")

    products = collect_products(categories_dir)
    if not products:
        print("No se encontraron productos en las paginas.")
        return

    upsert_products(
        products,
        default_stock=args.stock,
        is_active=not args.inactive,
        mode=args.mode,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pathlib import Path
import shutil
from sqlalchemy.orm import Session

from app.adapters.api.dependencies import get_db, require_roles
from app.adapters.api.schemas import ProductCreateIn, ProductOut, ProductUpdateIn
from app.application.use_cases.product_service import ProductService
from app.domain.entities.product import ProductCreate, ProductUpdate
from app.domain.errors import NotFoundError, ValidationError
from app.infrastructure.database.repositories import SqlAlchemyProductRepository


router = APIRouter(prefix="/products", tags=["products"])

upload_dir = Path(__file__).resolve().parents[4] / "uploads" / "products"
upload_dir.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    service = ProductService(SqlAlchemyProductRepository(db))
    products = service.list_products()
    return [ProductOut.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(SqlAlchemyProductRepository(db))
    try:
        product = service.get_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ProductOut.model_validate(product)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreateIn,
    profile=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = ProductService(SqlAlchemyProductRepository(db))
    data = ProductCreate(
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        stock=payload.stock,
        category=payload.category,
        image_url=payload.image_url,
        is_active=payload.is_active,
    )
    try:
        product = service.create_product(data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return ProductOut.model_validate(product)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    payload: ProductUpdateIn,
    profile=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = ProductService(SqlAlchemyProductRepository(db))
    data = ProductUpdate(
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        stock=payload.stock,
        category=payload.category,
        image_url=payload.image_url,
        is_active=payload.is_active,
    )
    try:
        product = service.update_product(product_id, data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ProductOut.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    profile=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = ProductService(SqlAlchemyProductRepository(db))
    try:
        service.delete_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return None


@router.post("/{product_id}/image", response_model=ProductOut)
def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    profile=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")
    filename = f"{product_id}{suffix}"
    path = upload_dir / filename
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    service = ProductService(SqlAlchemyProductRepository(db))
    data = ProductUpdate(image_url=f"/media/products/{filename}")
    try:
        product = service.update_product(product_id, data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ProductOut.model_validate(product)

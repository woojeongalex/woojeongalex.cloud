# FastAPI 패턴 (Thin Router)

## 업로드 + 파서 패턴 (James)

```python
@james_router.post("/upload", response_model=JamesUploadResponse)
async def upload_titanic_csv(
    file: UploadFile = File(...),
    james: JamesUseCase = Depends(get_james_use_case),
) -> JamesUploadResponse:
    file_name, rows = await read_james_upload(file)
    result = await james.upload(james_schemas_to_person_commands(rows), file_name)
    return JamesUploadResponse(**result)
```

## 조회 패턴 (Walter)

```python
@walter_router.get("/passengers", response_model=WalterPassengerPageResponse)
async def read_passengers(
    source_file: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    walter: WalterUseCase = Depends(get_walter_use_case),
) -> WalterPassengerPageResponse:
    page_dto = await walter.read_passengers(source_file, page, size)
    return walter_page_dto_to_response(page_dto)
```

## 데이터 흐름 (한 요청)

```
HTTP Request
  → router (스키마 바인딩)
  → parser (파일 업로드 시)
  → mapper (schema → Command/DTO)
  → handler (선택: DB/검증 예외)
  → UseCase/Interactor (Port 타입)
  → Repository Port 구현 (*PgRepository)
  → ORM → DB
  → mapper (Result DTO → Response schema)
  → HTTP Response
```

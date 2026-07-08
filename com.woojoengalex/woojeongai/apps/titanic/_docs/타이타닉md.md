[file-tag: code-generated-file-0-1778135193176849754]
```
# Define the content of the markdown file as requested by the user
md_content = """# Titanic API Project

이 문서는 FastAPI를 사용하여 작성된 타이타닉 데이터 API 서버의 소스 코드와 설명입니다.

## 1. 소스 코드 (`james.py`)

```

코드 출력

````
titanic_api_source.md

```python
from fastapi import FastAPI, Query

from .walter import Walter

app = FastAPI(title="Titanic API")


@app.get("/")
def health_check():
    return {"message": "제인스가 메인이다", "docs": "/docs"}

@app.get("/data")
def read_titanic_preview():
    w = Walter()
    return w.get_data()

@app.get("/titanic/preview")
def preview(limit: int = Query(default=10, ge=1, le=100)):
    w = Walter()
    return {"rows": w.get_data(limit=limit)}


if __name__ == "__main__":
    import uvicorn

    print("제임스가 메인이다. (uvicorn)")
    uvicorn.run("james:app", host="127.0.0.1", port=8000, reload=True)
````


## 2. API 엔드포인트 상세

- **`GET /`**: 서버 상태를 확인하는 헬스 체크 엔드포인트입니다.
    
- **`GET /data`**: `Walter` 클래스를 통해 전체 데이터를 조회합니다.
    
- **`GET /titanic/preview`**: 데이터의 일부를 미리 봅니다.
    
    - `limit`: 조회할 행의 개수를 지정합니다. (최소 1, 최대 100, 기본값 10)
        

## 3. 실행 및 주의사항

1. 이 코드를 실행하기 위해서는 같은 디렉토리에 `walter.py` 파일과 그 안에 `Walter` 클래스가 정의되어 있어야 합니다.
    
2. 소스 파일명을 `james.py`로 저장해야 `uvicorn.run("james:app", ...)` 명령이 정상적으로 작동합니다.
    
3. 실행 후 브라우저에서 `http://127.0.0.1:8000/docs`로 접속하면 Swagger UI를 통해 API를 직접 테스트해 볼 수 있습니다. """
    

# Save the content to a .md file

filename = "titanic_api_source.md" with open(filename, "w", encoding="utf-8") as f: f.write(md_content)

print(filename)

```
요청하신 FastAPI 소스 코드와 설명이 포함된 Markdown 파일이 준비되었습니다.

Your MD file is ready
[file-tag: code-generated-file-0-1778134981586858550]

### 파일 내용 요약:
* **소스 코드:** 제공해주신 `james.py`의 전체 코드가 포함되어 있습니다.
* **엔드포인트 설명:** 각 API 경로가 하는 역할이 정리되어 있습니다.
* **실행 가이드:** 파일명 설정 및 실행 방법에 대한 주의사항이 포함되어 있습니다.
```
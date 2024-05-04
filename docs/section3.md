### Section 3 - 상품 검색
1. 상품 검색시 filter() 사용의 문제점
- index를 제대로 활용할 수 없음
  - filter() -> 완벽하게 값이 일치해야 결과에 포함(단어 검색 불가능) 
  - __contains -> LIKE 문 사용, index 활용 불가능(예외: left-anchored search)
2. 검색 엔진의 원리
- 역인덱스(inverted index)
  - 각 단어가 어떤 문서에 포함되었는지 기록한 자료구조
  - 문장 분석: 토큰화(tokenizing), 형태소 분석(stemming)
    - 토큰화: 텍스트를 특정 단위로 분리, 정렬, 불용어(stopword) 제거
      - "진짜 맛있는 바나나입니다." -> ["진짜", "맛있는", "바나나"]
      - 한글 토큰화의 어려움: "아버지가방에들어가시다" -> "아버지가 방에 들어가시다" / "아버지 가방에 들어가시다"
    - 형태소 분석: 단어를 원형으로 변형(예: "맛있는" -> "맛있다") 
3. Full-text search 구현
```python
class Product(models.Model):
    # ...
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]
```
```python
# migrations
def update_search_vector(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    Product.objects.update(search_vector=SearchVector("name"))

class Migration(migrations.Migration):
    # ... 
  
    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER search_vector_trigger
                BEFORE INSERT OR UPDATE OF name, search_vector
                ON product
                FOR EACH ROW EXECUTE PROCEDURE
                tsvector_update_trigger(
                    search_vector, 'pg_catalog.english', name
                );
                UPDATE product SET search_vector = NULL;
                """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS search_vector_trigger
                ON product;
                """,
        ),
        migrations.RunPython(
            update_search_vector, reverse_code=migrations.RunPython.noop
        ),
    ]
```
4. 대용량 트래픽 처리 노하우
- 대용량 트래픽 처리란?
  - 많은 요청을 빠르고 효율적으로 처리하기 위한 방법
    - 인프라: Scale Up/Scale Out, 로드 밸런싱, Event-driven Architecture 등
    - 어플리케이션: 비동기 처리, 데이터베이스 쿼리/인덱스 튜닝, 데이터베이스 샤딩/파티셔닝, 캐싱, CDN 등  
- 어플리케이션에서 고민해야 되는 점
  - 새로운 컴퓨팅 자원의 투입 없이 어떻게 하면 효율적으로 요청을 처리할까?  
    - `얼마만큼 미리 계산해둘 것인가?`
    - 시간 복잡도 <-> 공간 복잡도 Trade-off

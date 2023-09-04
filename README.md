# notion-be
 imitate notion pages' backend service

# pages 
notion의 pages를 계층형 구조로 추상화하였다. 이를 RDB로 표현하기 위하여 closure pattern을 사용하였다.
[참고 : 계층 구조 모델을 DB에서 구현하는 방법](https://www.slideshare.net/billkarwin/models-for-hierarchical-data)

DB closure pattern의 장점은 다음과 같다.

- page에서는 page와 관련한 로직만 처리하고, **계층 구조는 별도의 테이블에서 관리 (역할 분담)** → 여러 기능들을 각각의 CRUD로 처리할 수 있음
- 재귀나 반복 없이 breadcrumbs select 가능

만약 parent_id를 갖는 테이블을 구성할 경우, 모든 breadcrumbs 가져오기 힘들다. 일일이 JOIN하거나(혹은 MySQL 재귀 함수 이용), 반복문으로 select 결과를 이용해야한다.

## DB schema

![schema](schema.png)

depth 컬럼을 추가하여 breadcrumbs를 구할 때 최소 탐색을 수행할 수 있다.

## raw sql in django

django model은 사용하되, sql을 직접 execute하기 위하여 `django.db`의 `connection` 을 이용하였다.
[참고 : django custom sql 공식문서](https://docs.djangoproject.com/en/4.2/topics/db/sql/#executing-custom-sql-directly)

## 특징
계층적인 데이터를 효과적으로 저장하고 쿼리하는 방식을 제공한다.

대상 테이블의 조상, 자식 노드의 id와 트리 노드의 깊이로 구현된다. 
- 깊이를 추가하여 직관성, 효율성 상승, 브레드크럼즈를 구현할 때 깊이를 기준으로 서브 페이지 판단

## 장점 

데이터베이스의 양이 많아지거나 계층 구조가 복잡해지더라도 성능은 일정한 수준 유지가 가능하다.

이를 통해 특정 페이지의 모든 상위 페이지와 서브 페이지를 쉽게 조회할 수 있다.

유연성이 뛰어나 복잡한 계층 구조를 쉽게 다룰 수 있다. 
- ex) 페이지 이동, 삭제

Django의 외래키를 사용하므로 Page가 삭제되면 관련된 PageTree 항목도 자동으로 삭제되어서 데이터 무결성이 뛰어나다.

## 단점
최악의 경우 최대 깊이인 O(n)이 걸릴 수 있으며, 저장 공간이 크다.

새로운 노드나 관계를 추가하거나 기존 노드를 이동시킬 때, 관련된 경로를 Closure Table에 적절하게 업데이트 해야한다.

## API

#### Page 생성

- method : POST

- request : `/api/page/`
- request body `application/json`
  - title : string
  - content : string
  - parent_id : int (-1인 경우, 부모 페이지 없는 새로운 페이지)

- response

  정상인 경우 OK

- logic 
  1. page 테이블에 게시글 생성 (title,content)
  2. 생성된 page 테이블 데이터로 page_trees 데이터 생성 (descendant_id,ancestor_id,depth)
  3. page_trees 테이블에서 parent_id를 자식으로 갖는 모든 page_id의 descendant_id에 current_id를 넣고 추가해준다.


- raw query 
  1. 게시글 생성 
    "INSERT INTO pages (title, content) VALUES (title,content);"
  2. page_trees (depth 확인 테이블) 생성
    "INSERT INTO page_trees (ancestor_id, descendant_id, depth)
        SELECT t.ancestor_id, current_id, depth+1
        FROM page_trees as t
        WHERE t.descendant_id = parent_id
        UNION ALL
        SELECT current_id, current_id, 0;"

#### 특정 Page 조회

- method : GET

- request : `/api/page/{page_id}/`

- response

  root page의 경우

  ```json
  {
      "page_id": 1,
      "title": "1st page",
      "content": "hello world",
      "sub_pages": [3,6,9],
      "breadcrumbs": [
          "1st page"
      ]
  }
  ```

  leaf page의 경우

  ```json
  {
      "page_id": 4,
      "title": "4th page",
      "content": "hello world",
      "sub_pages": [],
      "breadcrumbs": ["1st page","3rd page","4th page"]
  }
  ```


- logic 
  breadcrumbs 
    1. 조회된 페이지의 pk와  page_trees를 통해서 구한 ancestor_id로 조상 페이지를 조회
        조회된 페이지를 depth 기준으로 오름차순 정렬한 뒤 breadcrumb에 담는다.
  sub_page
    1.  페이지 id기반으로 동일한 ancestor_id와 depth 가지고 서브페이지를 조회
  
- raw query 
  1. 페이지 조회
    "SELECT * FROM pages WHERE page_id=page_id"

  2. 서브페이지 조회
    "SELECT descendant_id FROM page_trees WHERE ancestor_id = page_id and depth = {now depth};"

  3. 해당 페이지 조상페이지 제목 조회
      "SELECT title
        FROM pages
        WHERE page_id IN 
            (SELECT ancestor_id
            FROM page_trees t
            WHERE descendant_id=%s
            ORDER BY depth ASC);"
   
## 설계한 이유
select가 더 자주 호출 될 것이므로 select 시간을 줄이는 것에 집중하였고, 확장성을 고려하여 Closure Table을 선택하였다.

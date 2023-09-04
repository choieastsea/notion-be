from django.db import connection


def getTupleIdOfSelect(cursor):
    return tuple(row[0] for row in cursor.fetchall())


def getDictOfSelectOne(cursor):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))


def makeBreadCrumbs(parentList):
    print(parentList)
    return "/".join(map(str, parentList))


def createPage(page, parent_id):
    """
    1. page 테이블에 내용을 추가한다.
    2. page_trees 테이블에서 parent_id를 자식으로 갖는 모든 page_id의 descendant_id에 current_id를 넣고 추가해준다.
    """
    with connection.cursor() as cursor:
        # 1. page 추가
        cursor.execute("INSERT INTO pages (title, content) VALUES (%s,%s);",
                       [page.title, page.content])
        current_id = cursor.lastrowid
        if parent_id == -1:
            parent_id = current_id
        # 2. page_tree에 추가된 페이지를 자식으로 하는 페이지들의 관계 row 추가
        cursor.execute(
            """
            INSERT INTO page_trees (ancestor_id, descendant_id, depth)
                SELECT t.ancestor_id, %s, depth+1
                FROM page_trees as t
                WHERE t.descendant_id = %s
                UNION ALL
                SELECT %s, %s, 0;
            """, [current_id, parent_id, current_id, current_id])



def getDetailPage(page_id):
    """
    page_id : int, title: str, content : str, sub_page: page[], breadcrumbs: str
    """
    with connection.cursor() as cursor:
        # get basic page_info from page_id
        cursor.execute("SELECT * FROM pages WHERE page_id=%s", [page_id])
        result_dict = getDictOfSelectOne(cursor)
        # get subpages of page_id (descendant 찾기)
        cursor.execute(
            "SELECT descendant_id FROM page_trees WHERE ancestor_id = %s and depth = %s", [page_id, 1])
        result_dict['sub_pages'] = getTupleIdOfSelect(cursor)
        # get breadcrumbs (depth가 2,1,0인 부모의 제목을 찾기)
        cursor.execute(
            """
            SELECT title
            FROM pages
            WHERE page_id IN 
                (SELECT ancestor_id
                FROM page_trees t
                WHERE descendant_id=%s
                ORDER BY depth ASC)
            ;
            """, [page_id])
        result_dict['breadcrumbs'] = getTupleIdOfSelect(cursor)
        return result_dict

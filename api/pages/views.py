from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from . import db
# Create your views here.


class PageAPIDetail(APIView):
    """
    특정 page_id를 얻어오거나, 업데이트/삭제 하기 위한 api class
    """

    def get(self, request, page_id):
        result_dict = db.getDetailPage(page_id=page_id)
        return Response(result_dict, status=200)

    def put(self, request, page_id):
        """
        update post
        """
        return Response({"detail": "update"}, status=200)

    def delete(self, request, page_id):
        """
        delete post
        """
        return Response({"detail": "delete"}, status=200)


class PageAPIList(APIView):
    """
    page list를 가져오거나, 새로운 page를 만드는 api class
    """

    def get(self, request):
        return Response({"detail": "list"})

    def post(self, request):
        data = request.data
        title = data['title']
        content = data['content']
        parent_id = data['parent_id']
        db.createPage(page={"title": title, "content": content},
                      parent_id=parent_id)
        return Response({"detail": "create"})

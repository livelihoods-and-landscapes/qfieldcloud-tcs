from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from drf_yasg.utils import swagger_auto_schema

from qfieldcloud.core.models import (
    OrganizationMember, Organization)
from qfieldcloud.core.serializers import (
    OrganizationMemberSerializer)
from qfieldcloud.core import permissions_utils

User = get_user_model()


class ListCreateMembersViewPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        organization_name = permissions_utils.get_param_from_request(
            request, 'organization')

        try:
            organization = User.objects.get(username=organization_name)
        except ObjectDoesNotExist:
            return False

        if request.method == 'GET':
            return permissions_utils.can_list_members(user, organization)
        if request.method == 'POST':
            return permissions_utils.can_create_members(user, organization)
        return False


@method_decorator(
    name='get', decorator=swagger_auto_schema(
        operation_description="List members of an organization",
        operation_id="List memebers",))
@method_decorator(
    name='post', decorator=swagger_auto_schema(
        operation_description="Add a user as member of an organization",
        operation_id="Create member",))
class ListCreateMembersView(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated,
                          ListCreateMembersViewPermissions]
    serializer_class = OrganizationMemberSerializer

    def get_queryset(self):
        organization = self.request.parser_context['kwargs']['organization']
        organization_obj = User.objects.get(username=organization)

        return OrganizationMember.objects.filter(organization=organization_obj)

    def post(self, request, organization):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization_obj = Organization.objects.get(username=organization)
        member_obj = User.objects.get(username=request.data['member'])
        serializer.save(member=member_obj, organization=organization_obj)

        try:
            headers = {
                'Location': str(serializer.data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            headers = {}

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GetUpdateDestroyMemberViewPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        organization_name = permissions_utils.get_param_from_request(
            request, 'organization')
        member_name = permissions_utils.get_param_from_request(
            request, 'username')

        try:
            organization = Organization.objects.get(username=organization_name)
            member = User.objects.get(username=member_name)
        except ObjectDoesNotExist:
            return False

        if request.method == 'GET':
            return permissions_utils.can_get_member_role(
                user, organization, member)
        if request.method in ['PUT', 'PATCH']:
            return permissions_utils.can_update_member_role(
                user, organization, member)
        if request.method in ['DELETE']:
            return permissions_utils.can_delete_member_role(
                user, organization, member)
        return False


@method_decorator(
    name='get', decorator=swagger_auto_schema(
        operation_description="Get the role of a member of an organization",
        operation_id="Get memeber",))
@method_decorator(
    name='put', decorator=swagger_auto_schema(
        operation_description="Update a memeber of an organization",
        operation_id="Update member",))
@method_decorator(
    name='patch', decorator=swagger_auto_schema(
        operation_description="Partial update a member of an organization",
        operation_id="Patch member",))
@method_decorator(
    name='delete', decorator=swagger_auto_schema(
        operation_description="Remove a member from an organization",
        operation_id="Delete member",))
class GetUpdateDestroyMemberView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAuthenticated,
                          GetUpdateDestroyMemberViewPermissions]
    serializer_class = OrganizationMemberSerializer

    def get_object(self):
        organization = self.request.parser_context['kwargs']['organization']
        member = self.request.parser_context['kwargs']['username']

        organization_obj = Organization.objects.get(username=organization)
        member_obj = User.objects.get(username=member)
        return OrganizationMember.objects.get(
            organization=organization_obj,
            member=member_obj)

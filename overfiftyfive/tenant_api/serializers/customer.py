# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models.me import SharedMe
from shared_foundation.models.o55_user import O55User
from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.models import (
    Comment,
    CustomerComment,
    Customer
)


class CustomerListCreateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    comments = CustomerCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    class Meta:
        model = Customer
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # Misc (Read/Write)
            'is_senior',
            'is_support',
            'job_info_read',
            'how_hear',

            # Misc (Read Only)
            'comments',
            # 'organizations', #TODO: FIX

            # Misc (Write Only)
            'extra_comment',

            # Contact Point
            'area_served',
            'available_language',
            'contact_type',
            'email',
            'fax_number',
            # 'hours_available', #TODO: FIX
            'telephone',
            'telephone_extension',
            'mobile',

            # Postal Address
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # Geo-coordinate
            'elevation',
            'latitude',
            'longitude',
            # 'location' #TODO: FIX
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner', 'created_by', 'last_modified_by', 'comments'
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality:

        - Create a `User` object in the public database.

        - Create a `SharedMe` object in the public database.

        - Create a `Customer` object in the tenant database.

        - If user has entered text in the 'extra_comment' field then we will
          a `Comment` object and attach it to the `Customer` object.

        - We will attach the staff user whom created this `Customer` object.
        """
        # Create our user.
        email = validated_data['email']
        user = O55User.objects.create(
            first_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            email=email,
            username=get_unique_username_from_email(email),
            is_active=True,
            is_staff=False,
            is_superuser=False
        )

        # Attach the user to the `Customer` group.
        user.groups.add(CUSTOMER_GROUP_ID)

        # Create a user `Profile` object in our public schema.
        me = SharedMe.objects.update_or_create(
            user=user,
            franchise=self.context['franchise'],
            was_email_activated=True,
            defaults={
                'user': user,
                'franchise': self.context['franchise'],
                'was_email_activated': True,
            }
        )

        # Create our `Customer` object in our tenant schema.
        customer = Customer.objects.create(
            owner=user,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),

            # Misc
            # 'is_senior', #TODO: IMPLEMENT WHEN YOU ARE READY
            # 'is_support',
            # 'job_info_read',
            # 'how_hear',
            # 'organizations',
            #
            # # Contact Point
            # 'area_served',
            # 'available_language',
            # 'contact_type',
            email=validated_data['email'],
            # 'fax_number',
            # 'hours_available',
            # 'telephone',
            # 'telephone_extension',
            # 'mobile',
            #
            # # Postal Address
            # 'address_country',
            # 'address_locality',
            # 'address_region',
            # 'post_office_box_number',
            # 'postal_code',
            # 'street_address',
            # 'street_address_extra',
            #
            # # Geo-coordinate
            # 'elevation',
            # 'latitude',
            # 'longitude',
            # 'location'
        )

        # Attach our comment.
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['created_by'],
                last_modified_by=self.context['created_by'],
                text=extra_comment
            )
            customer_comment = CustomerComment.objects.create(
                customer=customer,
                comment=comment,
                created_by=self.context['created_by'],
            )

        # Update validation data.
        validated_data['comments'] = CustomerComment.objects.filter(customer=customer)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data


class CustomerRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    comments = CustomerCommentSerializer(many=True, read_only=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    class Meta:
        model = Customer
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # Misc (Read/Write)
            'is_senior',
            'is_support',
            'job_info_read',
            'how_hear',

            # Misc (Read Only)
            'comments',
            # 'organizations', #TODO: FIX

            # Misc (Write Only)
            'extra_comment',

            # Contact Point
            'area_served',
            'available_language',
            'contact_type',
            'email',
            'fax_number',
            # 'hours_available', #TODO: FIX
            'telephone',
            'telephone_extension',
            'mobile',

            # Postal Address
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # Geo-coordinate
            'elevation',
            'latitude',
            'longitude',
            # 'location' #TODO: FIX
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner', 'created_by', 'last_modified_by', 'comments'
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.owner.email)

        #---------------------------
        # Update `O55User` object.
        #---------------------------
        instance.owner.email = email
        instance.owner.username = get_unique_username_from_email(email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)
        instance.owner.save()

        #---------------------------
        # Update `Customer` object.
        #---------------------------
        instance.email = email
        # Profile
        instance.first_name = validated_data.get('given_name', None)
        instance.middle_name = validated_data.get('middle_name', None)
        instance.last_name = validated_data.get('last_name', None)
        instance.last_modified_by = self.context['last_modified_by']
        """
        'birthdate',
        'join_date',
        # Misc (Read/Write)
        'is_senior',
        'is_support',
        'job_info_read',
        'how_hear',

        # Misc (Read Only)
        'comments',
        'created_by',
        'last_modified_by',
        # 'organizations', #TODO: FIX

        # Misc (Write Only)
        'extra_comment',

        # Contact Point
        'area_served',
        'available_language',
        'contact_type',
        'email',
        'fax_number',
        # 'hours_available', #TODO: FIX
        'telephone',
        'telephone_extension',
        'mobile',

        # Postal Address
        'address_country',
        'address_locality',
        'address_region',
        'post_office_box_number',
        'postal_code',
        'street_address',
        'street_address_extra',

        # Geo-coordinate
        'elevation',
        'latitude',
        'longitude',
        # 'location' #TODO: FIX
        """
        #TODO: IMPLEMENT MORE...
        instance.save()

        #---------------------------
        # Attach our comment.
        #---------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['last_modified_by'],
                last_modified_by=self.context['last_modified_by'],
                text=extra_comment
            )
            customer_comment = CustomerComment.objects.create(
                customer=instance,
                comment=comment,
                created_by=self.context['last_modified_by'],
            )

        #---------------------------
        # Update validation data.
        #---------------------------
        validated_data['comments'] = CustomerComment.objects.filter(customer=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data

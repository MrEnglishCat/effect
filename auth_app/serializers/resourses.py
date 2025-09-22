# from rest_framework import serializers
#
# from auth_app.models import ResourcesModel
# from auth_app.serializers import ActionsSerializer
#
# class ResoursesSerializer(serializers.ModelSerializer):
#     actions = ActionsSerializer(many=True)
#     class Meta:
#         model = ResourcesModel
#         fields = '__all__'
#         read_only_fields = ('id',)
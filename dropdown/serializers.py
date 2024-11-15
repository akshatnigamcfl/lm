from rest_framework import serializers




class CommonDropdownSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True)
    value = serializers.CharField()


class DropdownOptionSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()

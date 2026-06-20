from rest_framework import serializers
from .models import ChatSession, ChatMessage, BookmarkedAnswer, SUBJECT_CHOICES


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class ChatSessionListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'subject', 'is_active', 'message_count',
                  'last_message', 'created_at', 'updated_at')

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.content[:100] if last else ''


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class BookmarkedAnswerSerializer(serializers.ModelSerializer):
    message_content = serializers.CharField(source='message.content', read_only=True)
    session_title = serializers.CharField(source='message.session.title', read_only=True)

    class Meta:
        model = BookmarkedAnswer
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class DoubtQuerySerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.ChoiceField(choices=[s[0] for s in SUBJECT_CHOICES], default='other')
    question = serializers.CharField()
    code_snippet = serializers.CharField(required=False, allow_blank=True)
    code_language = serializers.CharField(required=False, allow_blank=True)

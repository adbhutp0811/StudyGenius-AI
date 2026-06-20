from rest_framework import serializers
from .models import PDFDocument, PDFChatSession, PDFChatMessage, DocumentHighlight


class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = '__all__'
        read_only_fields = ('id', 'user', 'file_size', 'page_count',
                           'content_text', 'is_processed', 'created_at', 'updated_at')


class PDFDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = ('id', 'title', 'description', 'file_size', 'page_count',
                  'is_processed', 'created_at')


class PDFChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFChatMessage
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class PDFChatSessionListSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = PDFChatSession
        fields = ('id', 'title', 'is_active', 'document_count', 'created_at', 'updated_at')

    def get_document_count(self, obj):
        return obj.pdf_documents.count()


class PDFChatSessionSerializer(serializers.ModelSerializer):
    messages = PDFChatMessageSerializer(many=True, read_only=True)
    documents = PDFDocumentListSerializer(source='pdf_documents', many=True, read_only=True)

    class Meta:
        model = PDFChatSession
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class DocumentHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentHighlight
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class PDFQuerySerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True)
    document_ids = serializers.ListField(child=serializers.CharField(), required=False)
    question = serializers.CharField()

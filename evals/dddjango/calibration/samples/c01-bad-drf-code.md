# DRF 구현

DRF ViewSet으로 구현합니다.

```python
from rest_framework import serializers, viewsets

class OrderSerializer(serializers.ModelSerializer):
    pass

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
```

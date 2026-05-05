지정된 fixture 경로(`/Users/hyun/Desktop/dddjango/none`)와 현재 작업 디렉터리 모두 파일이 없어 기존 코드 패턴은 확인할 수 없었습니다. 아래는 일반적인 `orders` 앱 기준의 unified diff입니다. `Order` 모델이 이미 있다고 가정하고, DRF `ModelSerializer`, `ModelViewSet`, router URL을 추가합니다.

```diff
diff --git a/orders/serializers.py b/orders/serializers.py
new file mode 100644
index 0000000..b2d4c0a
--- /dev/null
+++ b/orders/serializers.py
@@ -0,0 +1,11 @@
+from rest_framework import serializers
+
+from .models import Order
+
+
+class OrderSerializer(serializers.ModelSerializer):
+    class Meta:
+        model = Order
+        fields = "__all__"
+        read_only_fields = ("id", "created_at", "updated_at")
diff --git a/orders/views.py b/orders/views.py
new file mode 100644
index 0000000..8a1df18
--- /dev/null
+++ b/orders/views.py
@@ -0,0 +1,11 @@
+from rest_framework.viewsets import ModelViewSet
+
+from .models import Order
+from .serializers import OrderSerializer
+
+
+class OrderViewSet(ModelViewSet):
+    queryset = Order.objects.all()
+    serializer_class = OrderSerializer
diff --git a/orders/urls.py b/orders/urls.py
new file mode 100644
index 0000000..a26553b
--- /dev/null
+++ b/orders/urls.py
@@ -0,0 +1,10 @@
+from django.urls import include, path
+from rest_framework.routers import DefaultRouter
+
+from .views import OrderViewSet
+
+router = DefaultRouter()
+router.register("orders", OrderViewSet, basename="order")
+
+urlpatterns = [
+    path("", include(router.urls)),
+]
diff --git a/config/urls.py b/config/urls.py
index 1111111..2222222 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,6 +1,7 @@
 from django.contrib import admin
-from django.urls import path
+from django.urls import include, path
 
 urlpatterns = [
     path("admin/", admin.site.urls),
+    path("api/", include("orders.urls")),
 ]
```

`Order` 모델에 `created_at` 또는 `updated_at` 필드가 없다면 `read_only_fields`에서 해당 필드는 제거해야 합니다.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_user_agents.utils import get_user_agent
from .models import Device
from .serializers import DeviceSerializer



class DeviceCreateView(generics.CreateAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "Device added successfully!", "device": serializer.data},
            status=status.HTTP_201_CREATED
        )



class DeviceAutoDetectView(generics.CreateAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_agent = get_user_agent(request)
        device_type = (
            "MOBILE" if user_agent.is_mobile else
            "TABLET" if user_agent.is_tablet else
            "DESKTOP"
        )

        os_version = f"{user_agent.os.family} {user_agent.os.version_string}"
        device_name = user_agent.device.family or "Unknown Device"


        device = Device.objects.create(
            user=request.user,
            device_name=device_name,
            device_type=device_type,
            os_version=os_version
        )



        serializer = self.get_serializer(device)
        return Response(
            {"message": "Device auto-detected and saved!", "device": serializer.data},
            status=status.HTTP_201_CREATED
        )



class DeviceListView(generics.ListAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)
    



class DeviceDeleteView(generics.DestroyAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)


    def delete(self, request, *args, **kwargs):
        device = self.get_object()
        device.delete()
        
        return Response({"message": "Device deleted successfully."}, status=status.HTTP_200_OK)
    

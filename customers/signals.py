# customers/signals.py
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Customer

@receiver(post_delete, sender=Customer)
def delete_profile_image_on_delete(sender, instance, **kwargs):
    """ลบรูปโปรไฟล์เมื่อลบข้อมูลลูกค้า"""
    image = getattr(instance, "profile_image", None)
    if image:
        image_path = image.path
        if os.path.isfile(image_path):
            os.remove(image_path)

@receiver(pre_save, sender=Customer)
def delete_old_profile_image_on_update(sender, instance, **kwargs):
    """ลบรูปโปรไฟล์เก่าก่อนที่จะอัปเดตข้อมูลลูกค้า"""
    if not instance.pk:
        return  # หากเป็นการสร้างลูกค้าใหม่ จะไม่มีการลบรูปภาพใดๆ

    try:
        old_instance = Customer.objects.get(pk=instance.pk)
    except Customer.DoesNotExist:
        return

    # ถ้ารูปใหม่ต่างจากรูปเดิม ให้ลบรูปเดิม
    old_image = getattr(old_instance, "profile_image", None)
    new_image = getattr(instance, "profile_image", None)
    if old_image and old_image != new_image:
        old_image_path = old_image.path
        if os.path.isfile(old_image_path):
            os.remove(old_image_path)


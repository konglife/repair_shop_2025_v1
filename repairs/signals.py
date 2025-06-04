# repairs/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import RepairJob, UsedPart
from inventory.models import Stock # Import Stock model
from repairs.utils.cost_calculation import update_repair_job_costs
# from customers.models import RepairHistory

# @receiver(post_save, sender=RepairJob)
# def create_repair_history(sender, instance, created, **kwargs):
#     # ดึง instance จากฐานข้อมูลเพื่อให้แน่ใจว่าใช้ค่าที่อัปเดตล่าสุด
#     repair_job = RepairJob.objects.get(pk=instance.pk)
#     print(f"Total cost from DB: {repair_job.total_cost}")  # ตรวจสอบค่าที่ดึงจากฐานข้อมูล
    
#     if created and repair_job.status == 'COMPLETED':
#         RepairHistory.objects.create(
#             customer=repair_job.customer,
#             description=repair_job.description,
#             date=repair_job.repair_date,
#             cost=repair_job.total_cost  # ดึงจาก total_cost ที่ถูกต้อง
#         )
#     elif not created:
#         previous_instance = RepairJob.objects.get(pk=instance.pk)
#         if previous_instance.status != 'COMPLETED' and repair_job.status == 'COMPLETED':
#             RepairHistory.objects.create(
#                 customer=repair_job.customer,
#                 description=repair_job.description,
#                 date=repair_job.repair_date,
#                 cost=repair_job.total_cost  # ดึงจาก total_cost ที่ถูกต้อง
#             )

# @receiver(post_delete, sender=RepairJob)
# def delete_repair_history(sender, instance, **kwargs):
#     # ลบข้อมูล RepairHistory ที่เกี่ยวข้องเมื่อมีการลบ RepairJob
#     RepairHistory.objects.filter(
#         customer=instance.customer,
#         description=instance.description,
#         date=instance.repair_date,
#         cost=instance.total_cost
#     ).delete()

@receiver(post_save, sender=UsedPart)
def used_part_post_save_stock_adjustment(sender, instance, created, **kwargs):
    # Only adjust stock if the repair job is already completed
    if instance.repair_job.status == 'COMPLETED':
        stock = Stock.objects.filter(product=instance.product).first()
        if stock:
            if created:
                # New UsedPart created, deduct full quantity
                stock.current_stock -= instance.quantity
            else:
                # UsedPart updated, calculate difference
                # Fetch the old instance to get the old quantity
                try:
                    old_instance = UsedPart.objects.get(pk=instance.pk)
                    old_quantity = old_instance.quantity
                except UsedPart.DoesNotExist:
                    old_quantity = 0 # Should not happen for an update

                quantity_difference = instance.quantity - old_quantity
                stock.current_stock -= quantity_difference
            stock.save()

@receiver(post_save, sender=UsedPart)
def used_part_post_save(sender, instance, created, **kwargs):
    """
    Signal ที่ทำงานหลังจากบันทึก UsedPart
    อัปเดตค่า parts_selling_total และ parts_cost_total ใน RepairJob
    """
    update_repair_job_costs(instance.repair_job)

@receiver(post_delete, sender=UsedPart)
def used_part_post_delete_stock_return(sender, instance, **kwargs):
    # Return stock only if the repair job was completed
    if instance.repair_job.status == 'COMPLETED':
        stock = Stock.objects.filter(product=instance.product).first()
        if stock:
            stock.current_stock += instance.quantity
            stock.save()

@receiver(post_delete, sender=UsedPart)
def used_part_post_delete(sender, instance, **kwargs):
    """
    Signal ที่ทำงานหลังจากลบ UsedPart
    อัปเดตค่า parts_selling_total และ parts_cost_total ใน RepairJob
    """
    if instance.repair_job:
        update_repair_job_costs(instance.repair_job)

@receiver(post_delete, sender=RepairJob)
def update_stock_on_delete_repair_job(sender, instance, **kwargs):
    # เมื่อ RepairJob ถูกลบ ให้คืนสต็อกของทุก UsedPart ที่เกี่ยวข้อง
    if instance.status == 'COMPLETED':
        for part in instance.used_parts.all():
            stock = Stock.objects.filter(product=part.product).first()
            if stock:
                stock.current_stock += part.quantity
                stock.save()

@receiver(pre_save, sender=RepairJob)
def pre_save_repair_job_status(sender, instance, **kwargs):
    if instance.pk: # Only on existing instances
        try:
            old_instance = RepairJob.objects.get(pk=instance.pk)
            instance._original_status = old_instance.status
        except RepairJob.DoesNotExist:
            instance._original_status = None # New instance, no old status
    else:
        instance._original_status = None # New instance, no old status

@receiver(post_save, sender=RepairJob)
def update_stock_on_repair_job_status_change(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_original_status', None)
    new_status = instance.status

    # If status changes to COMPLETED, deduct stock
    if old_status != 'COMPLETED' and new_status == 'COMPLETED':
        for part in instance.used_parts.all():
            stock = Stock.objects.filter(product=part.product).first()
            if stock:
                stock.current_stock -= part.quantity
                stock.save()
    # If status changes from COMPLETED to non-COMPLETED (e.g., IN_PROGRESS), return stock
    elif old_status == 'COMPLETED' and new_status != 'COMPLETED':
        for part in instance.used_parts.all():
            stock = Stock.objects.filter(product=part.product).first()
            if stock:
                stock.current_stock += part.quantity
                stock.save()

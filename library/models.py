from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


class Faculty(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name() or self.user.username} ({self.department})"


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):

    STATUS_CHOICES = [
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='borrow_records'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_records'
    )

    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Borrowed'
    )

    @property
    def late_days(self):
        ref_date = self.return_date or timezone.now().date()
        if self.due_date and ref_date > self.due_date:
            return (ref_date - self.due_date).days
        return 0

    def __str__(self):
        return f"{self.student} - {self.book} - {self.status}"


class Fine(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    borrow_record = models.OneToOneField(
        BorrowRecord,
        on_delete=models.CASCADE,
        related_name='fine'
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fines'
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def late_days(self):
        return self.borrow_record.late_days

    def __str__(self):
        return f"Fine: {self.student.student_id} - {self.borrow_record.book.title} - ₹{self.amount} ({self.status})"


class BookReservation(models.Model):

    TIME_SLOT_CHOICES = [
        ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
        ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
        ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
        ('12:00 PM - 01:00 PM', '12:00 PM - 01:00 PM'),
        ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
        ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
        ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
    ]

    STATUS_CHOICES = [
        ('Reserved', 'Reserved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    reservation_date = models.DateField()

    time_slot = models.CharField(
        max_length=50,
        choices=TIME_SLOT_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Reserved'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.student} - {self.book} - "
            f"{self.reservation_date} - {self.time_slot}"
            
        )
class ReadingRoomBooking(models.Model):

    TIME_SLOT_CHOICES = [
        ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
        ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
        ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
        ('12:00 PM - 01:00 PM', '12:00 PM - 01:00 PM'),
        ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
        ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
        ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
    ]

    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='reading_room_bookings'
    )

    booking_date = models.DateField()

    time_slot = models.CharField(
        max_length=50,
        choices=TIME_SLOT_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Booked'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['booking_date', 'time_slot'],
                condition=models.Q(status='Booked'),
                name='unique_active_cabin_booking'
            )
        ]
        ordering = ['-booking_date', 'time_slot']

    def __str__(self):
        return f"{self.student} - {self.booking_date} - {self.time_slot} ({self.status})"
from django.contrib import admin
from .models import Book, Student, Faculty, BorrowRecord, ReadingRoomBooking, Fine

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'quantity')
    search_fields = ('title', 'author', 'category')
    list_filter = ('category',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_name', 'get_email', 'branch')
    search_fields = ('student_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'branch')
    list_filter = ('branch',)

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'get_name', 'get_email', 'department', 'phone')
    search_fields = ('faculty_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'department')
    list_filter = ('department',)

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issue_date', 'due_date', 'return_date', 'status')
    list_filter = ('status', 'issue_date', 'due_date', 'return_date')
    search_fields = ('student__student_id', 'student__user__username', 'book__title')


@admin.register(ReadingRoomBooking)
class ReadingRoomBookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'booking_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'time_slot')
    search_fields = ('student__student_id', 'student__user__username', 'booking_date')


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_book', 'amount', 'status', 'payment_date', 'created_at')
    list_filter = ('status', 'payment_date', 'created_at')
    search_fields = ('student__student_id', 'student__user__username', 'borrow_record__book__title')

    def get_book(self, obj):
        return obj.borrow_record.book.title
    get_book.short_description = 'Book'


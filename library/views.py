from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Book, Student, Faculty, BorrowRecord, BookReservation, ReadingRoomBooking, Fine
from .forms import StudentRegistrationForm, BookForm, FacultyCreationForm, FacultyEditForm, StudentEditForm


# ============================================================
# ADMIN AND ROLE CHECKS
# ============================================================

def is_admin(user):
    return user.is_authenticated and (
        user.is_staff or user.is_superuser
    )

def is_faculty(user):
    return user.is_authenticated and hasattr(user, 'faculty_profile')

STUDENT_ONLY_MESSAGE = "Book borrowing and Reading Cabin booking are available only for students."


# ============================================================
# HOME
# ============================================================

def home(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'library/home.html')


# ============================================================
# STUDENT REGISTRATION
# ============================================================

def register_student(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f"Account created successfully for {user.username}! "
                "You can now login."
            )

            return redirect('login')

        messages.error(
            request,
            "Registration failed. Please correct the errors below."
        )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'library/register.html',
        {'form': form}
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    f"Welcome back, {user.username}!"
                )

                return redirect('dashboard')

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    else:
        form = AuthenticationForm()

    return render(
        request,
        'library/login.html',
        {'form': form}
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect('home')


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    if is_admin(request.user):

        books = Book.objects.all().order_by('title')

        total_titles = books.count()

        total_quantity = (
            books.aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

        active_borrows = BorrowRecord.objects.filter(
            status='Borrowed'
        ).count()

        total_students = Student.objects.count()
        total_faculty = Faculty.objects.count()
        total_pending_fines = Fine.objects.filter(status='Pending').count()
        pending_fines_amount = Fine.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0

        active_reservations = BookReservation.objects.filter(
            status='Reserved'
        ).count()

        q = request.GET.get('q', '')

        if q:

            books = books.filter(
                Q(title__icontains=q) |
                Q(author__icontains=q) |
                Q(category__icontains=q)
            )

        context = {
            'books': books,
            'total_titles': total_titles,
            'total_quantity': total_quantity,
            'active_borrows': active_borrows,
            'total_students': total_students,
            'total_faculty': total_faculty,
            'total_pending_fines': total_pending_fines,
            'pending_fines_amount': pending_fines_amount,
            'active_reservations': active_reservations,
            'query': q,
            'is_admin_user': True,
        }

        return render(
            request,
            'library/admin_dashboard.html',
            context
        )

    # ========================================================
    # STUDENT / FACULTY DASHBOARD
    # ========================================================

    student = getattr(request.user, 'student_profile', None)
    faculty = getattr(request.user, 'faculty_profile', None)

    if not student and not faculty:
        messages.warning(
            request,
            "You are logged in but do not have a Student Profile."
        )

        student = Student.objects.create(
            user=request.user,
            student_id=f"TEMP_{request.user.id}",
            branch="Unassigned"
        )

    books = Book.objects.all().order_by('title')

    q = request.GET.get('q', '')

    if q:

        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(category__icontains=q)
        )

    borrowed_books_ids = []
    reserved_books_ids = []
    my_active_count = 0
    my_total_count = 0
    my_reservation_count = 0
    my_cabin_count = 0
    my_pending_fines_count = 0
    my_pending_fines_amount = 0

    if student:
        borrowed_books_ids = BorrowRecord.objects.filter(
            student=student,
            status='Borrowed'
        ).values_list(
            'book_id',
            flat=True
        )

        reserved_books_ids = BookReservation.objects.filter(
            student=student,
            status='Reserved'
        ).values_list(
            'book_id',
            flat=True
        )

        my_active_count = BorrowRecord.objects.filter(
            student=student,
            status='Borrowed'
        ).count()

        my_total_count = BorrowRecord.objects.filter(
            student=student
        ).count()

        my_reservation_count = BookReservation.objects.filter(
            student=student,
            status='Reserved'
        ).count()

        my_cabin_count = ReadingRoomBooking.objects.filter(
            student=student,
            status='Booked'
        ).count()

        my_pending_fines_count = Fine.objects.filter(
            student=student,
            status='Pending'
        ).count()

        my_pending_fines_amount = Fine.objects.filter(
            student=student,
            status='Pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'books': books,
        'borrowed_books_ids': borrowed_books_ids,
        'reserved_books_ids': reserved_books_ids,
        'my_active_count': my_active_count,
        'my_total_count': my_total_count,
        'my_reservation_count': my_reservation_count,
        'my_cabin_count': my_cabin_count,
        'my_pending_fines_count': my_pending_fines_count,
        'my_pending_fines_amount': my_pending_fines_amount,
        'query': q,
        'is_admin_user': False,
        'is_faculty_user': bool(faculty),
        'faculty': faculty,
        'student': student,
    }

    return render(
        request,
        'library/student_dashboard.html',
        context
    )


# ============================================================
# ADD BOOK
# ============================================================

@user_passes_test(is_admin)
def add_book(request):

    if request.method == 'POST':

        form = BookForm(request.POST)

        if form.is_valid():

            book = form.save()

            messages.success(
                request,
                f"Book '{book.title}' added successfully!"
            )

            return redirect('dashboard')

        messages.error(
            request,
            "Failed to add book. Please correct the errors."
        )

    else:
        form = BookForm()

    return render(
        request,
        'library/book_form.html',
        {
            'form': form,
            'title': 'Add New Book'
        }
    )


# ============================================================
# EDIT BOOK
# ============================================================

@user_passes_test(is_admin)
def edit_book(request, id):

    book = get_object_or_404(
        Book,
        id=id
    )

    if request.method == 'POST':

        form = BookForm(
            request.POST,
            instance=book
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f"Book '{book.title}' updated successfully!"
            )

            return redirect('dashboard')

        messages.error(
            request,
            "Failed to update book."
        )

    else:

        form = BookForm(
            instance=book
        )

    return render(
        request,
        'library/book_form.html',
        {
            'form': form,
            'title': f'Edit: {book.title}'
        }
    )


# ============================================================
# DELETE BOOK
# ============================================================

@user_passes_test(is_admin)
def delete_book(request, id):

    book = get_object_or_404(
        Book,
        id=id
    )

    if request.method == 'POST':

        book.delete()

        messages.success(
            request,
            f"Book '{book.title}' deleted successfully."
        )

        return redirect('dashboard')

    return render(
        request,
        'library/book_confirm_delete.html',
        {'book': book}
    )


# ============================================================
# BORROW BOOK
# ============================================================

@login_required
def borrow_book(request, id):

    if is_admin(request.user):

        messages.error(
            request,
            "Admins cannot borrow books."
        )

        return redirect('dashboard')

    if is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    book = get_object_or_404(
        Book,
        id=id
    )

    try:
        student = request.user.student_profile

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('dashboard')

    already_borrowed = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status='Borrowed'
    ).exists()

    if already_borrowed:

        messages.warning(
            request,
            f"You have already borrowed '{book.title}' "
            "and haven't returned it yet."
        )

        return redirect('dashboard')

    if book.quantity <= 0:

        messages.error(
            request,
            f"Sorry, '{book.title}' is currently out of stock."
        )

        return redirect('dashboard')

    book.quantity -= 1
    book.save()

    due_date = timezone.now().date() + timedelta(days=14)

    BorrowRecord.objects.create(
        student=student,
        book=book,
        due_date=due_date,
        status='Borrowed'
    )

    # Complete active reservation if it exists
    BookReservation.objects.filter(
        student=student,
        book=book,
        status='Reserved'
    ).update(
        status='Completed'
    )

    messages.success(
        request,
        f"You have successfully borrowed '{book.title}'! Due date: {due_date}."
    )

    return redirect('dashboard')


# ============================================================
# RETURN BOOK
# ============================================================

@login_required
def return_book(request, record_id):

    if is_admin(request.user):

        messages.error(
            request,
            "Admins cannot return books."
        )

        return redirect('dashboard')

    if is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    try:
        student = request.user.student_profile

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('dashboard')

    record = get_object_or_404(
        BorrowRecord,
        id=record_id,
        student=student,
        status='Borrowed'
    )

    book = record.book

    book.quantity += 1
    book.save()

    record.status = 'Returned'
    record.return_date = timezone.now().date()
    record.save()

    # Calculate fine for late return (₹5 per day late)
    FINE_PER_DAY = 5
    if record.due_date and record.return_date > record.due_date:
        late_days = (record.return_date - record.due_date).days
        fine_amount = late_days * FINE_PER_DAY

        if fine_amount > 0:
            Fine.objects.update_or_create(
                borrow_record=record,
                defaults={
                    'student': student,
                    'amount': fine_amount,
                    'status': 'Pending'
                }
            )
            messages.warning(
                request,
                f"You have returned '{book.title}' {late_days} day(s) late. A fine of ₹{fine_amount} has been issued."
            )
            return redirect('dashboard')

    messages.success(
        request,
        f"You have returned '{book.title}'. Thank you!"
    )

    return redirect('dashboard')


# ============================================================
# RESERVE BOOK / BOOK SLOT
# ============================================================

@login_required
def reserve_book(request, id):

    if is_admin(request.user):

        messages.error(
            request,
            "Admins cannot reserve books."
        )

        return redirect('dashboard')

    if is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    book = get_object_or_404(
        Book,
        id=id
    )

    try:
        student = request.user.student_profile

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('dashboard')

    if request.method == 'POST':

        reservation_date = request.POST.get(
            'reservation_date'
        )

        time_slot = request.POST.get(
            'time_slot'
        )

        # Check fields
        if not reservation_date or not time_slot:

            messages.error(
                request,
                "Please select a date and time slot."
            )

            return redirect(
                'reserve_book',
                id=book.id
            )

        # Validate date
        try:

            selected_date = timezone.datetime.strptime(
                reservation_date,
                '%Y-%m-%d'
            ).date()

            if selected_date < timezone.now().date():

                messages.error(
                    request,
                    "Please select today or a future date."
                )

                return redirect(
                    'reserve_book',
                    id=book.id
                )

        except ValueError:

            messages.error(
                request,
                "Invalid reservation date."
            )

            return redirect(
                'reserve_book',
                id=book.id
            )

        # Check if already borrowed
        already_borrowed = BorrowRecord.objects.filter(
            student=student,
            book=book,
            status='Borrowed'
        ).exists()

        if already_borrowed:

            messages.warning(
                request,
                f"You already borrowed '{book.title}'."
            )

            return redirect('dashboard')

        # Check active reservation
        already_reserved = BookReservation.objects.filter(
            student=student,
            book=book,
            status='Reserved'
        ).exists()

        if already_reserved:

            messages.warning(
                request,
                f"You already have an active reservation "
                f"for '{book.title}'."
            )

            return redirect('my_reservations')

        # Create reservation
        BookReservation.objects.create(
            student=student,
            book=book,
            reservation_date=selected_date,
            time_slot=time_slot,
            status='Reserved'
        )

        messages.success(
            request,
            f"'{book.title}' reserved successfully!"
        )

        return redirect('my_reservations')

    context = {
        'book': book,
        'time_slots': BookReservation.TIME_SLOT_CHOICES,
        'today': timezone.now().date().isoformat(),
    }

    return render(
        request,
        'library/reserve_book.html',
        context
    )


# ============================================================
# MY RESERVATIONS
# ============================================================

@login_required
def my_reservations(request):

    if is_admin(request.user):

        reservations = BookReservation.objects.all().order_by(
            '-created_at'
        )

    elif is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    else:

        try:
            student = request.user.student_profile

        except Student.DoesNotExist:

            messages.error(
                request,
                "Student profile not found."
            )

            return redirect('dashboard')

        reservations = BookReservation.objects.filter(
            student=student
        ).order_by(
            '-created_at'
        )

    return render(
        request,
        'library/my_reservations.html',
        {
            'reservations': reservations,
            'is_admin_user': is_admin(request.user)
        }
    )


# ============================================================
# CANCEL RESERVATION
# ============================================================

@login_required
def cancel_reservation(request, reservation_id):

    if is_admin(request.user):

        messages.error(
            request,
            "Admins cannot cancel reservations."
        )

        return redirect('my_reservations')

    if is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    try:
        student = request.user.student_profile

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('dashboard')

    reservation = get_object_or_404(
        BookReservation,
        id=reservation_id,
        student=student,
        status='Reserved'
    )

    reservation.status = 'Cancelled'
    reservation.save()

    messages.success(
        request,
        f"Reservation for '{reservation.book.title}' cancelled."
    )

    return redirect('my_reservations')


# ============================================================
# BORROW HISTORY
# ============================================================

@login_required
def borrow_history(request):

    if is_admin(request.user):

        history = BorrowRecord.objects.all().order_by(
            '-issue_date'
        )

    elif is_faculty(request.user):

        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )

        return redirect('dashboard')

    else:

        try:
            student = request.user.student_profile

        except Student.DoesNotExist:

            messages.error(
                request,
                "Student profile not found."
            )

            return redirect('dashboard')

        history = BorrowRecord.objects.filter(
            student=student
        ).order_by(
            '-issue_date'
        )

    return render(
        request,
        'library/borrow_history.html',
        {
            'history': history,
            'is_admin_user': is_admin(request.user)
        }
    )


# ============================================================
# READING CABIN / ROOM BOOKING
# ============================================================

@login_required
def book_reading_room(request):

    if is_admin(request.user):
        messages.error(
            request,
            "Admins cannot book reading cabins."
        )
        return redirect('dashboard')

    if is_faculty(request.user):
        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )
        return redirect('dashboard')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect('dashboard')

    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        time_slot = request.POST.get('time_slot')

        if not booking_date or not time_slot:
            messages.error(
                request,
                "Please select both a date and a time slot."
            )
            return redirect('reading_room_booking')

        # Validate date
        try:
            selected_date = timezone.datetime.strptime(
                booking_date,
                '%Y-%m-%d'
            ).date()

            if selected_date < timezone.now().date():
                messages.error(
                    request,
                    "Please select today or a future date."
                )
                return redirect('reading_room_booking')

        except ValueError:
            messages.error(
                request,
                "Invalid reservation date format."
            )
            return redirect('reading_room_booking')

        # Validate time slot choice
        valid_slots = [choice[0] for choice in ReadingRoomBooking.TIME_SLOT_CHOICES]
        if time_slot not in valid_slots:
            messages.error(
                request,
                "Invalid time slot selected."
            )
            return redirect('reading_room_booking')

        # Check if slot is already booked for this date by another student
        slot_already_booked = ReadingRoomBooking.objects.filter(
            booking_date=selected_date,
            time_slot=time_slot,
            status='Booked'
        ).exists()

        if slot_already_booked:
            messages.error(
                request,
                f"The slot '{time_slot}' on {selected_date} is already booked. Please choose another slot or date."
            )
            return redirect('reading_room_booking')

        # Check if this student already booked this slot on this date
        already_booked_by_me = ReadingRoomBooking.objects.filter(
            student=student,
            booking_date=selected_date,
            time_slot=time_slot,
            status='Booked'
        ).exists()

        if already_booked_by_me:
            messages.warning(
                request,
                f"You already have an active booking for '{time_slot}' on {selected_date}."
            )
            return redirect('my_reading_room_bookings')

        # Create booking
        ReadingRoomBooking.objects.create(
            student=student,
            booking_date=selected_date,
            time_slot=time_slot,
            status='Booked'
        )

        messages.success(
            request,
            f"Reading Cabin slot '{time_slot}' on {selected_date} successfully booked!"
        )
        return redirect('my_reading_room_bookings')

    context = {
        'time_slots': ReadingRoomBooking.TIME_SLOT_CHOICES,
        'today': timezone.now().date().isoformat(),
    }
    return render(
        request,
        'library/book_reading_room.html',
        context
    )


# ============================================================
# MY READING CABIN BOOKINGS
# ============================================================

@login_required
def my_reading_room_bookings(request):

    if is_admin(request.user):
        bookings = ReadingRoomBooking.objects.all().order_by(
            '-booking_date',
            '-created_at'
        )
    elif is_faculty(request.user):
        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )
        return redirect('dashboard')
    else:
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            messages.error(
                request,
                "Student profile not found."
            )
            return redirect('dashboard')

        bookings = ReadingRoomBooking.objects.filter(
            student=student
        ).order_by(
            '-booking_date',
            '-created_at'
        )

    return render(
        request,
        'library/my_reading_room_bookings.html',
        {
            'bookings': bookings,
            'is_admin_user': is_admin(request.user),
        }
    )


# ============================================================
# CANCEL READING CABIN BOOKING
# ============================================================

@login_required
def cancel_reading_room_booking(request, booking_id):

    if is_admin(request.user):
        messages.error(
            request,
            "Admins cannot cancel student cabin bookings here."
        )
        return redirect('my_reading_room_bookings')

    if is_faculty(request.user):
        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )
        return redirect('dashboard')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect('dashboard')

    booking = get_object_or_404(
        ReadingRoomBooking,
        id=booking_id,
        student=student,
        status='Booked'
    )

    booking.status = 'Cancelled'
    booking.save()

    messages.success(
        request,
        f"Cabin booking for {booking.booking_date} ({booking.time_slot}) has been cancelled."
    )
    return redirect('my_reading_room_bookings')


# ============================================================
# MODULE 2: FACULTY MANAGEMENT (ADMIN)
# ============================================================

@user_passes_test(is_admin)
def manage_faculty(request):
    q = request.GET.get('q', '').strip()
    faculty_list = Faculty.objects.all().select_related('user').order_by('-created_at')

    if q:
        faculty_list = faculty_list.filter(
            Q(faculty_id__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(department__icontains=q)
        )

    return render(
        request,
        'library/faculty_list.html',
        {
            'faculty_list': faculty_list,
            'query': q,
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def add_faculty(request):
    if request.method == 'POST':
        form = FacultyCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Faculty member '{user.get_full_name() or user.username}' registered successfully!"
            )
            return redirect('manage_faculty')
        else:
            messages.error(
                request,
                "Failed to register faculty. Please correct the errors."
            )
    else:
        form = FacultyCreationForm()

    return render(
        request,
        'library/faculty_form.html',
        {
            'form': form,
            'title': 'Add New Faculty',
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def edit_faculty(request, id):
    faculty = get_object_or_404(Faculty, id=id)

    if request.method == 'POST':
        form = FacultyEditForm(request.POST, faculty=faculty)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Faculty details for '{faculty.faculty_id}' updated successfully!"
            )
            return redirect('manage_faculty')
        else:
            messages.error(
                request,
                "Failed to update faculty details."
            )
    else:
        form = FacultyEditForm(faculty=faculty)

    return render(
        request,
        'library/faculty_form.html',
        {
            'form': form,
            'faculty': faculty,
            'title': f'Edit Faculty: {faculty.faculty_id}',
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def delete_faculty(request, id):
    faculty = get_object_or_404(Faculty, id=id)

    if request.method == 'POST':
        user = faculty.user
        faculty_id = faculty.faculty_id
        user.delete()  # Cascades to delete faculty profile
        messages.success(
            request,
            f"Faculty record '{faculty_id}' has been deleted."
        )
        return redirect('manage_faculty')

    return render(
        request,
        'library/faculty_confirm_delete.html',
        {
            'faculty': faculty,
            'is_admin_user': True,
        }
    )


# ============================================================
# MODULE 2: STUDENT MANAGEMENT (ADMIN)
# ============================================================

@user_passes_test(is_admin)
def manage_students(request):
    q = request.GET.get('q', '').strip()
    students = Student.objects.all().select_related('user').order_by('-id')

    if q:
        students = students.filter(
            Q(student_id__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(branch__icontains=q)
        )

    return render(
        request,
        'library/student_list.html',
        {
            'students': students,
            'query': q,
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        form = StudentEditForm(request.POST, student=student)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Student profile for '{student.student_id}' updated successfully!"
            )
            return redirect('manage_students')
        else:
            messages.error(
                request,
                "Failed to update student details."
            )
    else:
        form = StudentEditForm(student=student)

    return render(
        request,
        'library/student_form.html',
        {
            'form': form,
            'student': student,
            'title': f'Edit Student: {student.student_id}',
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        user = student.user
        student_id = student.student_id
        user.delete()  # Cascades to student profile
        messages.success(
            request,
            f"Student record '{student_id}' has been deleted."
        )
        return redirect('manage_students')

    return render(
        request,
        'library/student_confirm_delete.html',
        {
            'student': student,
            'is_admin_user': True,
        }
    )


# ============================================================
# MODULE 4: FINE MANAGEMENT
# ============================================================

@login_required
def my_fines(request):
    if is_admin(request.user):
        return redirect('manage_fines')

    if is_faculty(request.user):
        messages.info(
            request,
            STUDENT_ONLY_MESSAGE
        )
        return redirect('dashboard')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect('dashboard')

    fines = Fine.objects.filter(student=student).select_related(
        'borrow_record', 'borrow_record__book'
    ).order_by('-created_at')

    total_fines_amount = fines.aggregate(total=Sum('amount'))['total'] or 0
    pending_fines_amount = fines.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    paid_fines_amount = fines.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0

    return render(
        request,
        'library/my_fines.html',
        {
            'fines': fines,
            'total_fines_amount': total_fines_amount,
            'pending_fines_amount': pending_fines_amount,
            'paid_fines_amount': paid_fines_amount,
            'is_admin_user': False,
        }
    )


@user_passes_test(is_admin)
def manage_fines(request):
    status_filter = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    fines = Fine.objects.all().select_related(
        'student', 'student__user', 'borrow_record', 'borrow_record__book'
    ).order_by('-created_at')

    if status_filter in ['Pending', 'Paid']:
        fines = fines.filter(status=status_filter)

    if q:
        fines = fines.filter(
            Q(student__student_id__icontains=q) |
            Q(student__user__username__icontains=q) |
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q) |
            Q(borrow_record__book__title__icontains=q)
        )

    all_fines = Fine.objects.all()
    total_fines_count = all_fines.count()
    total_pending_count = all_fines.filter(status='Pending').count()
    total_pending_amount = all_fines.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    total_paid_amount = all_fines.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0

    return render(
        request,
        'library/admin_fines.html',
        {
            'fines': fines,
            'status_filter': status_filter,
            'query': q,
            'total_fines_count': total_fines_count,
            'total_pending_count': total_pending_count,
            'total_pending_amount': total_pending_amount,
            'total_paid_amount': total_paid_amount,
            'is_admin_user': True,
        }
    )


@user_passes_test(is_admin)
def pay_fine_admin(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)

    if request.method == 'POST':
        fine.status = 'Paid'
        fine.payment_date = timezone.now().date()
        fine.save()
        messages.success(
            request,
            f"Fine of ₹{fine.amount} for student {fine.student.student_id} marked as Paid."
        )

    return redirect('manage_fines')
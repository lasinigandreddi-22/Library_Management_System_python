from django.urls import path

from . import views


urlpatterns = [

    # Home
    path(
        '',
        views.home,
        name='home'
    ),

    # Authentication
    path(
        'register/',
        views.register_student,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # Admin - Books
    path(
        'books/add/',
        views.add_book,
        name='add_book'
    ),

    path(
        'books/<int:id>/edit/',
        views.edit_book,
        name='edit_book'
    ),

    path(
        'books/<int:id>/delete/',
        views.delete_book,
        name='delete_book'
    ),

    # Student - Borrow
    path(
        'books/<int:id>/borrow/',
        views.borrow_book,
        name='borrow_book'
    ),

    # Student - Return
    path(
        'borrow/<int:record_id>/return/',
        views.return_book,
        name='return_book'
    ),

    # Book Reservation / Slot
    path(
        'books/<int:id>/reserve/',
        views.reserve_book,
        name='reserve_book'
    ),

    path(
        'reservations/',
        views.my_reservations,
        name='my_reservations'
    ),

    path(
        'reservations/<int:reservation_id>/cancel/',
        views.cancel_reservation,
        name='cancel_reservation'
    ),

    # Borrow History
    path(
        'borrow-history/',
        views.borrow_history,
        name='borrow_history'
    ),

    # Reading Cabin / Room Slot Booking
    path(
        'reading-cabin/book/',
        views.book_reading_room,
        name='reading_room_booking'
    ),

    path(
        'reading-cabin/my-bookings/',
        views.my_reading_room_bookings,
        name='my_reading_room_bookings'
    ),

    path(
        'reading-cabin/<int:booking_id>/cancel/',
        views.cancel_reading_room_booking,
        name='cancel_reading_room_booking'
    ),

    # Module 2: Faculty Management
    path(
        'faculty/',
        views.manage_faculty,
        name='manage_faculty'
    ),
    path(
        'faculty/add/',
        views.add_faculty,
        name='add_faculty'
    ),
    path(
        'faculty/<int:id>/edit/',
        views.edit_faculty,
        name='edit_faculty'
    ),
    path(
        'faculty/<int:id>/delete/',
        views.delete_faculty,
        name='delete_faculty'
    ),

    # Module 2: Student Management
    path(
        'students/',
        views.manage_students,
        name='manage_students'
    ),
    path(
        'students/<int:id>/edit/',
        views.edit_student,
        name='edit_student'
    ),
    path(
        'students/<int:id>/delete/',
        views.delete_student,
        name='delete_student'
    ),

    # Module 4: Fine Management
    path(
        'my-fines/',
        views.my_fines,
        name='my_fines'
    ),
    path(
        'fines/',
        views.manage_fines,
        name='manage_fines'
    ),
    path(
        'fines/<int:fine_id>/pay/',
        views.pay_fine_admin,
        name='pay_fine_admin'
    ),
]
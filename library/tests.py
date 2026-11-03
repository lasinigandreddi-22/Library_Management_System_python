from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Book, Student, Faculty, BorrowRecord, ReadingRoomBooking, Fine

class LibrarySystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create standard admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@library.com',
            password='adminpassword'
        )

        # Create standard student user and profile
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@library.com',
            password='studentpassword',
            first_name='John',
            last_name='Doe'
        )
        self.student_profile = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            branch='Computer Science'
        )

        # Create standard faculty user and profile
        self.faculty_user = User.objects.create_user(
            username='faculty1',
            email='faculty1@library.com',
            password='facultypassword',
            first_name='Alan',
            last_name='Turing'
        )
        self.faculty_profile = Faculty.objects.create(
            user=self.faculty_user,
            faculty_id='FAC999',
            department='Computer Science'
        )

        # Create a sample book
        self.book = Book.objects.create(
            title='Intro to Algorithms',
            author='Thomas H. Cormen',
            category='Computer Science',
            quantity=5
        )

        # URLs
        self.home_url = reverse('home')
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.dashboard_url = reverse('dashboard')
        self.add_book_url = reverse('add_book')
        self.borrow_history_url = reverse('borrow_history')

    def test_homepage_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/home.html')

    def test_student_registration(self):
        # Register a new student
        response = self.client.post(self.register_url, {
            'username': 'student2',
            'email': 'student2@library.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'password123',
            'password_confirm': 'password123',
            'student_id': 'STU002',
            'branch': 'Information Technology'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(User.objects.filter(username='student2').exists())
        self.assertTrue(Student.objects.filter(student_id='STU002').exists())

    def test_student_login(self):
        response = self.client.post(self.login_url, {
            'username': 'student1',
            'password': 'studentpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.assertRedirects(response, self.dashboard_url)

    def test_book_crud_admin_only(self):
        # Unauthorized check: student user cannot add books
        self.client.login(username='student1', password='studentpassword')
        response = self.client.get(self.add_book_url)
        self.assertEqual(response.status_code, 302)  # Redirect due to user_passes_test
        
        # Admin check: admin can add books
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(self.add_book_url, {
            'title': 'Design Patterns',
            'author': 'Gang of Four',
            'category': 'Software Engineering',
            'quantity': 3
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title='Design Patterns').exists())

        # Admin check: admin can edit books
        book = Book.objects.get(title='Design Patterns')
        edit_url = reverse('edit_book', args=[book.id])
        response = self.client.post(edit_url, {
            'title': 'Design Patterns Updated',
            'author': 'Gang of Four',
            'category': 'Software Engineering',
            'quantity': 4
        })
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.title, 'Design Patterns Updated')
        self.assertEqual(book.quantity, 4)

        # Admin check: admin can delete books
        delete_url = reverse('delete_book', args=[book.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(title='Design Patterns Updated').exists())

    def test_borrow_and_return_flow(self):
        self.client.login(username='student1', password='studentpassword')
        
        # Test Borrow
        borrow_url = reverse('borrow_book', args=[self.book.id])
        response = self.client.get(borrow_url)
        self.assertEqual(response.status_code, 302)
        
        # Verify book quantity is decremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 4)
        
        # Verify BorrowRecord is created
        record = BorrowRecord.objects.get(student=self.student_profile, book=self.book)
        self.assertEqual(record.status, 'Borrowed')

        # Test Return
        return_url = reverse('return_book', args=[record.id])
        response = self.client.post(return_url)
        self.assertEqual(response.status_code, 302)
        
        # Verify book quantity is restored
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 5)
        
        # Verify BorrowRecord is updated
        record.refresh_from_db()
        self.assertEqual(record.status, 'Returned')
        self.assertIsNotNone(record.return_date)

    def test_out_of_stock_borrow(self):
        # Set quantity to 0
        self.book.quantity = 0
        self.book.save()

        self.client.login(username='student1', password='studentpassword')
        borrow_url = reverse('borrow_book', args=[self.book.id])
        response = self.client.get(borrow_url)
        self.assertEqual(response.status_code, 302)

        # Verify BorrowRecord was NOT created
        self.assertFalse(BorrowRecord.objects.filter(student=self.student_profile, book=self.book).exists())

    def test_student_dashboard_reading_cabin_elements(self):
        self.client.login(username='student1', password='studentpassword')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reading Cabin')
        self.assertContains(response, 'Book Reading Cabin')
        self.assertContains(response, 'My Cabin Bookings')
        self.assertContains(response, reverse('reading_room_booking'))
        self.assertContains(response, reverse('my_reading_room_bookings'))

    def test_reading_room_booking_flow(self):
        self.client.login(username='student1', password='studentpassword')
        booking_url = reverse('reading_room_booking')
        my_bookings_url = reverse('my_reading_room_bookings')

        # 1. GET booking page
        response = self.client.get(booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_reading_room.html')

        # 2. Reject past date
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        response = self.client.post(booking_url, {
            'booking_date': past_date,
            'time_slot': '09:00 AM - 10:00 AM'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReadingRoomBooking.objects.filter(booking_date=past_date).exists())

        # 3. Successful booking for tomorrow
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        response = self.client.post(booking_url, {
            'booking_date': tomorrow,
            'time_slot': '10:00 AM - 11:00 AM'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, my_bookings_url)

        booking = ReadingRoomBooking.objects.get(
            student=self.student_profile,
            booking_date=tomorrow,
            time_slot='10:00 AM - 11:00 AM'
        )
        self.assertEqual(booking.status, 'Booked')

        # 4. Prevent duplicate booking by another student for same date + time slot
        student2_user = User.objects.create_user(
            username='student_dup',
            password='password123'
        )
        student2_profile = Student.objects.create(
            user=student2_user,
            student_id='STU_DUP',
            branch='EE'
        )
        self.client.login(username='student_dup', password='password123')
        response = self.client.post(booking_url, {
            'booking_date': tomorrow,
            'time_slot': '10:00 AM - 11:00 AM'
        })
        self.assertEqual(response.status_code, 302)
        # Should not create a second booking
        self.assertEqual(
            ReadingRoomBooking.objects.filter(booking_date=tomorrow, time_slot='10:00 AM - 11:00 AM').count(),
            1
        )

        # 5. Cancel booking by student1
        self.client.login(username='student1', password='studentpassword')
        cancel_url = reverse('cancel_reading_room_booking', args=[booking.id])
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Cancelled')

        # 6. After cancellation, student2 CAN now book the freed slot
        self.client.login(username='student_dup', password='password123')
        response = self.client.post(booking_url, {
            'booking_date': tomorrow,
            'time_slot': '10:00 AM - 11:00 AM'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ReadingRoomBooking.objects.filter(
                student=student2_profile,
                booking_date=tomorrow,
                time_slot='10:00 AM - 11:00 AM',
                status='Booked'
            ).exists()
        )

    def test_faculty_creation(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(reverse('add_faculty'), {
            'username': 'prof_smith',
            'first_name': 'Alan',
            'last_name': 'Smith',
            'email': 'asmith@university.edu',
            'password': 'facultypassword1',
            'password_confirm': 'facultypassword1',
            'faculty_id': 'FAC001',
            'department': 'Computer Science',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='prof_smith').exists())
        self.assertTrue(Faculty.objects.filter(faculty_id='FAC001', department='Computer Science').exists())

    def test_faculty_unique_id(self):
        # Create initial faculty
        user1 = User.objects.create_user(username='fac1', password='pass')
        Faculty.objects.create(user=user1, faculty_id='FAC_DUP', department='Physics')

        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(reverse('add_faculty'), {
            'username': 'fac2',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'fac2@university.edu',
            'password': 'pass',
            'password_confirm': 'pass',
            'faculty_id': 'FAC_DUP',  # Duplicate
            'department': 'Chemistry'
        })
        # Should not create duplicate
        self.assertEqual(Faculty.objects.filter(faculty_id='FAC_DUP').count(), 1)

    def test_faculty_update_delete(self):
        user = User.objects.create_user(username='fac_edit', email='edit@u.edu', password='p')
        faculty = Faculty.objects.create(user=user, faculty_id='FAC_EDIT', department='Civil')

        self.client.login(username='admin', password='adminpassword')
        # Test Edit
        edit_url = reverse('edit_faculty', args=[faculty.id])
        response = self.client.post(edit_url, {
            'first_name': 'Robert',
            'last_name': 'Updated',
            'email': 'robert.updated@u.edu',
            'department': 'Mechanical',
            'phone': '9876543210'
        })
        self.assertEqual(response.status_code, 302)
        faculty.refresh_from_db()
        self.assertEqual(faculty.department, 'Mechanical')
        self.assertEqual(faculty.user.first_name, 'Robert')

        # Test Delete
        delete_url = reverse('delete_faculty', args=[faculty.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Faculty.objects.filter(faculty_id='FAC_EDIT').exists())

    def test_late_return_fine_calculation(self):
        self.client.login(username='student1', password='studentpassword')
        # Create borrow record with due date 3 days ago
        today = timezone.now().date()
        three_days_ago = today - timedelta(days=3)
        record = BorrowRecord.objects.create(
            student=self.student_profile,
            book=self.book,
            issue_date=today - timedelta(days=17),
            due_date=three_days_ago,
            status='Borrowed'
        )

        return_url = reverse('return_book', args=[record.id])
        response = self.client.post(return_url)
        self.assertEqual(response.status_code, 302)

        record.refresh_from_db()
        self.assertEqual(record.status, 'Returned')
        self.assertEqual(record.return_date, today)

        # Fine should be 3 late days * 5 = ₹15
        self.assertTrue(Fine.objects.filter(borrow_record=record).exists())
        fine = Fine.objects.get(borrow_record=record)
        self.assertEqual(fine.amount, 15)
        self.assertEqual(fine.status, 'Pending')
        self.assertEqual(fine.late_days, 3)

    def test_on_time_return_zero_fine(self):
        self.client.login(username='student1', password='studentpassword')
        today = timezone.now().date()
        # Due date is tomorrow (on-time)
        record = BorrowRecord.objects.create(
            student=self.student_profile,
            book=self.book,
            issue_date=today - timedelta(days=5),
            due_date=today + timedelta(days=1),
            status='Borrowed'
        )

        return_url = reverse('return_book', args=[record.id])
        response = self.client.post(return_url)
        self.assertEqual(response.status_code, 302)

        record.refresh_from_db()
        self.assertEqual(record.status, 'Returned')
        # No fine created for on-time return
        self.assertFalse(Fine.objects.filter(borrow_record=record).exists())

    def test_fine_payment_status(self):
        today = timezone.now().date()
        record = BorrowRecord.objects.create(
            student=self.student_profile,
            book=self.book,
            due_date=today - timedelta(days=2),
            return_date=today,
            status='Returned'
        )
        fine = Fine.objects.create(
            borrow_record=record,
            student=self.student_profile,
            amount=10,
            status='Pending'
        )

        self.client.login(username='admin', password='adminpassword')
        pay_url = reverse('pay_fine_admin', args=[fine.id])
        response = self.client.post(pay_url)
        self.assertEqual(response.status_code, 302)

        fine.refresh_from_db()
        self.assertEqual(fine.status, 'Paid')
        self.assertEqual(fine.payment_date, today)

    def test_student_can_view_own_fines(self):
        today = timezone.now().date()
        record = BorrowRecord.objects.create(
            student=self.student_profile,
            book=self.book,
            due_date=today - timedelta(days=4),
            return_date=today,
            status='Returned'
        )
        Fine.objects.create(
            borrow_record=record,
            student=self.student_profile,
            amount=20,
            status='Pending'
        )

        self.client.login(username='student1', password='studentpassword')
        response = self.client.get(reverse('my_fines'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/my_fines.html')
        self.assertContains(response, self.book.title)
        self.assertContains(response, '₹20')
        self.assertContains(response, 'Pending')

    def test_student_dashboard_displays_student_features(self):
        self.client.login(username='student1', password='studentpassword')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/student_dashboard.html')
        # Student-specific sections present
        self.assertContains(response, 'Borrow Book')
        self.assertContains(response, 'Book Reading Cabin')
        self.assertContains(response, 'My Cabin Bookings')
        self.assertContains(response, 'My Fines')
        self.assertContains(response, 'Active Borrows')
        # Faculty section not present
        self.assertNotContains(response, 'Faculty Workspace')

    def test_faculty_dashboard_displays_workspace_and_no_student_actions(self):
        self.client.login(username='faculty1', password='facultypassword')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/student_dashboard.html')
        # Faculty Workspace section present
        self.assertContains(response, 'Faculty Workspace')
        self.assertContains(response, 'Faculty Member | Computer Science')
        self.assertContains(response, 'FAC999')
        self.assertContains(response, 'Reference & Search')
        # Student-only actions NOT present
        self.assertNotContains(response, 'Borrow Book')
        self.assertNotContains(response, 'Book Reading Cabin')
        self.assertNotContains(response, 'My Cabin Bookings')
        self.assertNotContains(response, 'My Fines')
        self.assertNotContains(response, 'Active Borrows')
        # Books table is present with catalog search
        self.assertContains(response, self.book.title)

    def test_faculty_cannot_borrow_book_redirects(self):
        self.client.login(username='faculty1', password='facultypassword')
        borrow_url = reverse('borrow_book', args=[self.book.id])
        response = self.client.get(borrow_url, follow=True)
        self.assertRedirects(response, self.dashboard_url)
        self.assertContains(response, 'Book borrowing and Reading Cabin booking are available only for students.')
        self.assertFalse(BorrowRecord.objects.filter(book=self.book).exists())

    def test_faculty_cannot_book_reading_cabin_redirects(self):
        self.client.login(username='faculty1', password='facultypassword')
        booking_url = reverse('reading_room_booking')
        
        # GET request
        response = self.client.get(booking_url, follow=True)
        self.assertRedirects(response, self.dashboard_url)
        self.assertContains(response, 'Book borrowing and Reading Cabin booking are available only for students.')

        # POST request
        tomorrow = timezone.now().date() + timedelta(days=1)
        post_response = self.client.post(booking_url, {
            'booking_date': tomorrow.strftime('%Y-%m-%d'),
            'time_slot': '09:00 AM - 11:00 AM'
        }, follow=True)
        self.assertRedirects(post_response, self.dashboard_url)
        self.assertFalse(ReadingRoomBooking.objects.exists())

    def test_faculty_cannot_access_student_urls(self):
        self.client.login(username='faculty1', password='facultypassword')
        restricted_urls = [
            reverse('my_reading_room_bookings'),
            reverse('my_fines'),
            reverse('borrow_history'),
            reverse('my_reservations'),
        ]
        for url in restricted_urls:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, self.dashboard_url)
            self.assertContains(response, 'Book borrowing and Reading Cabin booking are available only for students.')

    def test_faculty_catalog_search(self):
        self.client.login(username='faculty1', password='facultypassword')
        response = self.client.get(self.dashboard_url + '?q=Algorithms')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro to Algorithms')

        empty_response = self.client.get(self.dashboard_url + '?q=QuantumMechanics1234')
        self.assertEqual(empty_response.status_code, 200)
        self.assertContains(empty_response, 'No matching books found.')




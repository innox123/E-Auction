from django.shortcuts import redirect



class UnadminUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user is authenticated and is a superuser
        if request.user.is_authenticated and request.user.is_superuser:
            # Check if the requested URL is /admin/dashboard/
            if request.path.startswith('/admin/dashboard/'):
                return response
            
            if request.path.startswith('/media/uploads/bank_slip/'):
                return response
            
            return redirect('main-admin')

        return response
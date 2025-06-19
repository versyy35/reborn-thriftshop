from .models import User, Seller, Buyer, Admin

class UserFactory:
    """
    A factory for creating users with different roles (Seller, Buyer).
    This encapsulates the object creation logic.
    """
    @staticmethod
    def create_user(role, **kwargs):
        """
        Creates a user and their corresponding profile (Seller or Buyer).
        
        :param role: The role of the user to create ('seller' or 'buyer').
        :param kwargs: The fields for the User model (e.g., username, password, email).
        :return: The created User object.
        :raises ValueError: If the role is invalid.
        """
        # Pop profile-specific data if any, to handle it separately.
        store_name = kwargs.pop('store_name', None)
        phone_number = kwargs.pop('phone_number', None)
        bio = kwargs.pop('bio', None)

        # Basic user creation
        user = User.objects.create_user(role=role, **kwargs)

        # Profile creation based on role
        if role == 'seller':
            Seller.objects.create(
                user=user,
                store_name=store_name,
                phone_number=phone_number,
                bio=bio
            )
        elif role == 'buyer':
            Buyer.objects.create(user=user)
        elif role == 'admin':
            Admin.objects.create(user=user)
        else:
            # If an invalid role is provided, we should delete the created user
            # to avoid orphaned user records.
            user.delete()
            raise ValueError(f"Invalid user role: {role}")
            
        return user

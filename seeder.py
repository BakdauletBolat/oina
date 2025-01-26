from django.utils import timezone

from faker import Faker

from users.models import User


class UserSeeder:
    faker = Faker()

    def run(self):
        for i in range(1,100):
            try:
                User.objects.create_user(
                    id=i,
                    username=self.faker.user_name(),
                    photo_url=self.faker.image_url(),
                    email=self.faker.email(),
                    password=self.faker.password(),
                    date_joined=timezone.now(),
                )
            except Exception as e:
                print('Already exists', e)

s = UserSeeder()
s.run()

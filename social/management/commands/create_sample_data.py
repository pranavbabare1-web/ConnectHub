"""
Management command to create sample test data for ConnectHub.
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.models import Profile, Post, Comment, Like, Follow


class Command(BaseCommand):
    help = 'Creates sample test data for ConnectHub'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        users_data = [
            {'username': 'alice', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@example.com', 'bio': 'Designer & dreamer ✨', 'location': 'San Francisco, CA'},
            {'username': 'bob', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob@example.com', 'bio': 'Full-stack developer 🚀', 'location': 'New York, NY'},
            {'username': 'carol', 'first_name': 'Carol', 'last_name': 'White', 'email': 'carol@example.com', 'bio': 'Photographer & traveller 📸', 'location': 'London, UK'},
        ]

        created_users = []
        for u in users_data:
            user, created = User.objects.get_or_create(username=u['username'])
            if created:
                user.first_name = u['first_name']
                user.last_name = u['last_name']
                user.email = u['email']
                user.set_password('password123')
                user.save()
                user.profile.bio = u['bio']
                user.profile.location = u['location']
                user.profile.save()
                self.stdout.write(f'  Created user: {u["username"]} (password: password123)')
            created_users.append(user)

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('  Created superuser: admin (password: admin123)')

        posts_data = [
            (created_users[0], "Just launched my new portfolio site! Months of work finally out in the world. 🎨", ),
            (created_users[1], "Hot take: dark mode should be the default everywhere. Fight me. 🌑"),
            (created_users[2], "Sunrise over the Thames this morning. Woke up at 5am and it was completely worth it. 🌅"),
            (created_users[0], "Design tip: whitespace isn't empty space — it's breathing room for your content."),
            (created_users[1], "Just fixed a bug that's been haunting me for three days. The feeling is indescribable. 🐛✅"),
        ]

        for user, content in posts_data:
            post, created = Post.objects.get_or_create(user=user, content=content)
            if created:
                self.stdout.write(f'  Created post by @{user.username}')

        # Follows
        follows = [(created_users[0], created_users[1]), (created_users[0], created_users[2]),
                   (created_users[1], created_users[0]), (created_users[2], created_users[0])]
        for follower, following in follows:
            Follow.objects.get_or_create(follower=follower, following=following)

        # Likes
        posts = list(Post.objects.all())
        for post in posts[:3]:
            for user in created_users:
                if user != post.user:
                    Like.objects.get_or_create(user=user, post=post)

        # Comments
        if posts:
            Comment.objects.get_or_create(user=created_users[1], post=posts[0], defaults={'text': 'Looks amazing! 🔥'})
            Comment.objects.get_or_create(user=created_users[2], post=posts[0], defaults={'text': 'Congrats! Sharing it with my network.'})

        self.stdout.write(self.style.SUCCESS('\n✓ Sample data created successfully!'))
        self.stdout.write('\nTest accounts:')
        self.stdout.write('  alice / password123')
        self.stdout.write('  bob / password123')
        self.stdout.write('  carol / password123')
        self.stdout.write('  admin / admin123 (superuser)')

import factory
from django.utils import timezone

from accounts.models import Account
from recommendations.models import (
    Badge,
    Bookmark,
    BookRecommendation,
    Category,
    CuratorFollow,
    DuplicateReport,
    RecommenderParticipant,
    ReputationEvent,
    Support,
)


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    display_name = factory.Sequence(lambda n: f"User {n}")
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class BookRecommendationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookRecommendation

    creator = factory.SubFactory(AccountFactory)
    page_type = BookRecommendation.PageType.STANDALONE_WORK
    title = factory.Sequence(lambda n: f"Book Title {n}")
    title_normalized = factory.LazyAttribute(lambda o: o.title.lower())
    author_names = factory.Sequence(lambda n: f"Author {n}")
    author_names_normalized = factory.LazyAttribute(lambda o: o.author_names.lower())
    status = BookRecommendation.Status.INACTIVE
    is_canonical = False


class DuplicateReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DuplicateReport

    reporter = factory.SubFactory(AccountFactory)
    recommendation = factory.SubFactory(BookRecommendationFactory)
    suspected_duplicate_of = None
    status = DuplicateReport.Status.PENDING


class RecommenderParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecommenderParticipant

    account = factory.SubFactory(AccountFactory)
    recommendation = factory.SubFactory(BookRecommendationFactory)
    locked_amount_lamports = 200_000_000
    initial_lock_at = factory.LazyFunction(timezone.now)
    is_active = False


class SupportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Support

    supporter = factory.SubFactory(AccountFactory)
    recommendation = factory.SubFactory(BookRecommendationFactory)
    supporter_number = factory.Sequence(lambda n: n + 1)
    amount_lamports = 10_000_000
    recommendation_cycle_number = 0


class BookmarkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bookmark

    account = factory.SubFactory(AccountFactory)
    recommendation = factory.SubFactory(BookRecommendationFactory)


class CuratorFollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CuratorFollow

    follower = factory.SubFactory(AccountFactory)
    followee = factory.SubFactory(AccountFactory)


class BadgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Badge

    account = factory.SubFactory(AccountFactory)
    recommendation = factory.SubFactory(BookRecommendationFactory)
    tier = Badge.Tier.BRONZE
    earned_at = factory.LazyFunction(timezone.now)


class ReputationEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReputationEvent

    account = factory.SubFactory(AccountFactory)
    event_type = ReputationEvent.EventType.DISCOVERY
    points = 10.00

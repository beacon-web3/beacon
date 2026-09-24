import pytest
from rest_framework.test import APIClient

from recommendations.models import DuplicateReport
from tests.recommendations.factories import (
    AccountFactory,
    DuplicateReportFactory,
    RecommendationFactory,
)

pytestmark = pytest.mark.django_db


class TestDuplicateReportCreate:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/report-duplicate/"

    def test_requires_authentication(self):
        rec = RecommendationFactory()

        response = APIClient().post(self._url(rec.id), {}, format="json")

        assert response.status_code == 403
        assert DuplicateReport.objects.count() == 0

    def test_404_for_missing(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(999999), {}, format="json")

        assert response.status_code == 404

    def test_creates_pending_report_with_empty_body(self):
        rec = RecommendationFactory()
        reporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=reporter)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 201
        report_data = response.data["duplicate_report"]
        assert report_data["status"] == "PENDING"
        assert report_data["reporter"]["username"] == reporter.username
        assert report_data["recommendation"]["id"] == rec.id
        assert report_data["suspected_duplicate_of"] is None
        assert report_data["reason"] == ""
        report = DuplicateReport.objects.get(reporter=reporter, recommendation=rec)
        assert report.status == DuplicateReport.Status.PENDING
        assert report.reason == ""

    def test_accepts_optional_reason_and_suspected_duplicate(self):
        rec = RecommendationFactory()
        original = RecommendationFactory()
        reporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=reporter)

        response = client.post(
            self._url(rec.id),
            {"suspected_duplicate_of": original.id, "reason": "Same ISBN."},
            format="json",
        )

        assert response.status_code == 201
        report_data = response.data["duplicate_report"]
        assert report_data["suspected_duplicate_of"]["id"] == original.id
        assert report_data["reason"] == "Same ISBN."
        report = DuplicateReport.objects.get(reporter=reporter, recommendation=rec)
        assert report.suspected_duplicate_of == original
        assert report.reason == "Same ISBN."

    def test_rejects_self_reference(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(
            self._url(rec.id),
            {"suspected_duplicate_of": rec.id},
            format="json",
        )

        assert response.status_code == 400
        assert "suspected_duplicate_of" in response.data
        assert DuplicateReport.objects.count() == 0

    def test_rejects_unknown_suspected_duplicate(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(
            self._url(rec.id),
            {"suspected_duplicate_of": 999999},
            format="json",
        )

        assert response.status_code == 400
        assert "suspected_duplicate_of" in response.data

    def test_conflict_when_already_filed_for_this_recommendation(self):
        rec = RecommendationFactory()
        reporter = AccountFactory()
        DuplicateReportFactory(reporter=reporter, recommendation=rec)
        client = APIClient()
        client.force_authenticate(user=reporter)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 409
        assert DuplicateReport.objects.filter(reporter=reporter).count() == 1

    def test_conflict_when_same_suspected_pair_reused(self):
        original = RecommendationFactory()
        first_target = RecommendationFactory()
        second_target = RecommendationFactory()
        reporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=reporter)

        first = client.post(
            self._url(first_target.id),
            {"suspected_duplicate_of": original.id},
            format="json",
        )
        second = client.post(
            self._url(second_target.id),
            {"suspected_duplicate_of": original.id},
            format="json",
        )

        assert first.status_code == 201
        assert second.status_code == 409
        assert DuplicateReport.objects.filter(reporter=reporter).count() == 1

    def test_concurrent_duplicate_create_returns_409_not_500(self):
        """A unique-constraint race between the pre-check and create() must
        surface as 409 (DB constraint is the safety net), not a 500."""
        from unittest.mock import patch

        from django.db import IntegrityError

        rec = RecommendationFactory()
        reporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=reporter)

        real_create = DuplicateReport.objects.create

        def _racing_create(**kwargs):
            # Simulate a concurrent request winning the unique constraint
            # between this request's exists() pre-check and its create().
            real_create(**kwargs)
            raise IntegrityError

        with patch.object(
            DuplicateReport.objects, "create", side_effect=_racing_create
        ):
            response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 409
        assert (
            DuplicateReport.objects.filter(
                reporter=reporter, recommendation=rec
            ).count()
            == 1
        )

    def test_is_idempotent_with_key(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        first = client.post(
            self._url(rec.id),
            {},
            format="json",
            HTTP_IDEMPOTENCY_KEY="report-key-1",
        )
        second = client.post(
            self._url(rec.id),
            {},
            format="json",
            HTTP_IDEMPOTENCY_KEY="report-key-1",
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert (
            first.data["duplicate_report"]["id"]
            == second.data["duplicate_report"]["id"]
        )
        assert DuplicateReport.objects.count() == 1


class TestDuplicateReportList:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/duplicate-reports/"

    def test_admin_can_list_reports(self):
        rec = RecommendationFactory()
        report = DuplicateReportFactory(recommendation=rec)
        admin = AccountFactory(is_staff=True)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(self._url(rec.id))

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == report.id
        assert response.data["results"][0]["status"] == "PENDING"

    def test_non_admin_forbidden(self):
        rec = RecommendationFactory()
        DuplicateReportFactory(recommendation=rec)
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.get(self._url(rec.id))

        assert response.status_code == 403

    def test_anonymous_forbidden(self):
        rec = RecommendationFactory()
        DuplicateReportFactory(recommendation=rec)

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 403

    def test_404_for_missing(self):
        admin = AccountFactory(is_staff=True)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(self._url(999999))

        assert response.status_code == 404

    def test_empty_list_when_no_reports(self):
        rec = RecommendationFactory()
        admin = AccountFactory(is_staff=True)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(self._url(rec.id))

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_lists_newest_first(self):
        from datetime import timedelta

        from django.utils import timezone

        rec = RecommendationFactory()
        older = DuplicateReportFactory(
            recommendation=rec,
            created_at=timezone.now() - timedelta(minutes=5),
        )
        newer = DuplicateReportFactory(
            recommendation=rec,
            created_at=timezone.now(),
        )
        admin = AccountFactory(is_staff=True)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(self._url(rec.id))

        ids = [row["id"] for row in response.data["results"]]
        assert ids == [newer.id, older.id]

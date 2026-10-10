import unittest
from datetime import datetime

from triage import categorize, report, sla_breaches, triage

T0 = datetime(2026, 10, 10, 9, 0)


def ticket(i, text, opened=T0):
    return {"id": i, "text": text, "opened": opened}


class TriageTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(categorize("I am locked out of my account"), "access")
        self.assertEqual(categorize("Outlook keeps crashing"), "email")
        self.assertEqual(categorize("VPN will not connect from home"), "network")
        self.assertEqual(categorize("my printer is jammed"), "hardware")
        self.assertIsNone(categorize("can you help with the thing"))

    def test_outage_outranks_other_words(self):
        # "email" appears too, but a company-wide outage must win.
        self.assertEqual(categorize("everyone lost email, server down"), "outage")

    def test_priority_tier_and_due_time(self):
        t = triage(ticket("1", "server down for all users"))
        self.assertEqual((t["priority"], t["tier"]), ("P1", 2))
        self.assertEqual(t["due"], datetime(2026, 10, 10, 10, 0))

    def test_unclassified_goes_to_review_not_guessed(self):
        t = triage(ticket("2", "something is weird"))
        self.assertTrue(t["needs_review"])
        self.assertEqual(t["category"], "unclassified")

    def test_sla_breach_detection_ignores_responded_tickets(self):
        tickets = [triage(ticket("a", "locked out")), triage(ticket("b", "locked out")), triage(ticket("c", "printer broken"))]
        later = datetime(2026, 10, 10, 14, 0)  # 5 hours later: access (4h) is late, hardware (24h) is not
        self.assertEqual(sla_breaches(tickets, later), ["a", "b"])
        self.assertEqual(sla_breaches(tickets, later, responded={"a"}), ["b"])

    def test_report(self):
        tickets = [triage(ticket("a", "locked out")), triage(ticket("b", "hmm"))]
        r = report(tickets, datetime(2026, 10, 10, 15, 0))
        self.assertEqual(r["by_category"], {"access": 1, "unclassified": 1})
        self.assertEqual(r["breached"], ["a"])
        self.assertEqual(r["needs_review"], ["b"])


if __name__ == "__main__":
    unittest.main()

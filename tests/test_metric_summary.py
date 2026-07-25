import unittest

from osna_pipeline.metrics import build_metric_summary


class MetricSummaryTests(unittest.TestCase):
    def test_excludes_invalid_pathways_and_counts_missing_values(self):
        timelines = [
            {
                "pathway_status": "complete",
                "transport_minutes": "10.0",
            },
            {
                "pathway_status": "incomplete",
                "transport_minutes": "",
            },
            {
                "pathway_status": "invalid",
                "transport_minutes": "999.0",
            },
        ]

        rows = build_metric_summary(timelines)
        transport = next(
            row for row in rows if row["metric_name"] == "transport_minutes"
        )

        self.assertEqual(transport["eligible_specimen_count"], "2")
        self.assertEqual(transport["observed_value_count"], "1")
        self.assertEqual(transport["missing_value_count"], "1")
        self.assertEqual(transport["excluded_invalid_specimen_count"], "1")
        self.assertEqual(transport["minimum"], "10.0")
        self.assertEqual(transport["median"], "10.0")
        self.assertEqual(transport["p90"], "10.0")
        self.assertEqual(transport["maximum"], "10.0")

    def test_calculates_a_linearly_interpolated_p90(self):
        timelines = [
            {
                "pathway_status": "complete",
                "transport_minutes": value,
            }
            for value in ("8.0", "9.0", "9.0", "15.0")
        ]

        rows = build_metric_summary(timelines)
        transport = next(
            row for row in rows if row["metric_name"] == "transport_minutes"
        )

        self.assertEqual(transport["median"], "9.0")
        self.assertEqual(transport["p90"], "13.2")


if __name__ == "__main__":
    unittest.main()

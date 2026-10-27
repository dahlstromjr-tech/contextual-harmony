import unittest
from src.python.interceptor import ModelContextProtocolInterceptor

class TestModelContextProtocolInterceptor(unittest.TestCase):
    def setUp(self):
        self.interceptor = ModelContextProtocolInterceptor()

    def test_zone_c_routing_for_mental_health(self):
        context = self.interceptor.map_to_uns("I am feeling anxious today", {"domain": "mental_health"})
        self.assertEqual(context.sensitivity_zone, "Zone_C")
        self.assertTrue(context.metadata["directives"]["sanctuary_mode"])

    def test_zone_a_routing_for_logistics(self):
        context = self.interceptor.map_to_uns("Batching inventory items", {"domain": "logistics"})
        self.assertEqual(context.sensitivity_zone, "Zone_A")
        self.assertTrue(context.metadata["directives"]["autonomous_adaptation"])

    def test_default_zone_b_routing(self):
        context = self.interceptor.map_to_uns("Drafting an email", {"domain": "productivity"})
        self.assertEqual(context.sensitivity_zone, "Zone_B")
        self.assertTrue(context.metadata["directives"]["human_checkpoint"])

if __name__ == "__main__":
    unittest.main()

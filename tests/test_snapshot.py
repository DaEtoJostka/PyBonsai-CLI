from pathlib import Path
import unittest

from pybonsai import AppConfig, TreeType, generate_tree


SNAPSHOT_PATH = (
    Path(__file__).resolve().parent / "snapshots" / "classic_seed_1.txt"
)


def make_seeded_config():
    config = AppConfig()
    config.render.width = 40
    config.render.height = 20
    config.tree.seed = 1
    config.tree.type = TreeType.CLASSIC
    config.user_set_type = True
    return config


class SnapshotTests(unittest.TestCase):
    def test_generate_tree_is_repeatable(self):
        config = make_seeded_config()

        first = generate_tree(config).to_string()
        second = generate_tree(config).to_string()

        self.assertEqual(first, second)

    def test_classic_seed_snapshot(self):
        config = make_seeded_config()
        generated = generate_tree(config).to_string()
        snapshot = SNAPSHOT_PATH.read_text().rstrip("\n")

        self.assertEqual(generated, snapshot)


if __name__ == "__main__":
    unittest.main()

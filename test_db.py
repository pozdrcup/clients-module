# test_db.py - тесты

import unittest
from unittest.mock import patch, MagicMock
import db


class TestClients(unittest.TestCase):

    @patch("db.get_connection")
    def test_add_client(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = (1,)
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.add_client("Иванов И.И.", "+79001234567", "ivanov@mail.ru", "VIP")
        self.assertEqual(result, 1)
        mock_cur.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()

    @patch("db.get_connection")
    def test_get_all_clients(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            (1, "Иванов", "+79001234567", "iv@mail.ru", "2025-01-01", "")
        ]
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.get_all_clients()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Иванов")

    @patch("db.get_connection")
    def test_search(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            (1, "Иванов", "+79001234567", "iv@mail.ru", "2025-01-01", "")
        ]
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.search_clients("Иванов")
        self.assertEqual(len(result), 1)

    @patch("db.get_connection")
    def test_update(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 1
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.update_client(1, "Петров П.П.", "+79009999999", "p@mail.ru", "")
        self.assertTrue(result)

    @patch("db.get_connection")
    def test_delete(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 1
        mock_conn.return_value.cursor.return_value = mock_cur
        self.assertTrue(db.delete_client(1))

    @patch("db.get_connection")
    def test_delete_not_found(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 0
        mock_conn.return_value.cursor.return_value = mock_cur
        self.assertFalse(db.delete_client(999))


class TestOrders(unittest.TestCase):

    @patch("db.get_connection")
    def test_add_order(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = (1,)
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.add_order(1, "Сайт-визитка", 15000.00)
        self.assertEqual(result, 1)

    @patch("db.get_connection")
    def test_get_orders(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            (1, "Сайт-визитка", 15000.00, "2025-03-01", "новый")
        ]
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.get_client_orders(1)
        self.assertEqual(len(result), 1)

    @patch("db.get_connection")
    def test_update_status(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 1
        mock_conn.return_value.cursor.return_value = mock_cur
        self.assertTrue(db.update_order_status(1, "выполнен"))


class TestReports(unittest.TestCase):

    @patch("db.get_connection")
    def test_summary(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchone.side_effect = [(5,), (12,), (75000.00,)]
        mock_conn.return_value.cursor.return_value = mock_cur

        r = db.report_summary()
        self.assertEqual(r["clients"], 5)
        self.assertEqual(r["orders"], 12)
        self.assertEqual(r["total_sum"], 75000.00)

    @patch("db.get_connection")
    def test_by_date(self, mock_conn):
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            (1, "Иванов", "+79001234567", "iv@mail.ru", "2025-01-15")
        ]
        mock_conn.return_value.cursor.return_value = mock_cur

        result = db.report_by_date("2025-01-01", "2025-02-01")
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()

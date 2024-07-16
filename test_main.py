import unittest
from unittest.mock import patch, MagicMock

class TestMain(unittest.TestCase):
    @patch('tkinter.Tk')
    @patch('Window.TkinterApp')
    def test_main_execution(self, mock_tkinter_app, mock_tk):
        with patch('main.tk.Tk', mock_tk):
            import main
            main.main()

            mock_tk.assert_called_once()
            mock_tkinter_app.assert_called_once()
            mock_tk.return_value.protocol.assert_called_once_with("WM_DELETE_WINDOW", mock_tkinter_app.return_value.quit)
            mock_tk.return_value.mainloop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
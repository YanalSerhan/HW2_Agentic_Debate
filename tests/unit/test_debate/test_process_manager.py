from unittest.mock import MagicMock, patch

from debate.constants import AgentRole
from debate.debate.process_manager import ProcessManager


@patch("debate.debate.process_manager.multiprocessing.Process")
def test_process_manager_lifecycle(mock_process_cls):
    mock_process = MagicMock()
    mock_process.is_alive.return_value = True
    mock_process_cls.return_value = mock_process

    mock_father = MagicMock()

    pm = ProcessManager(
        session_id="s1", topic="Topic", config={}, gatekeeper=None,
        father=mock_father, f_to_p=None, p_to_f=None, f_to_c=None, c_to_f=None
    )

    pm.start_processes()
    assert pm.pro_process is mock_process
    assert pm.con_process is mock_process
    assert mock_process.start.call_count == 2
    mock_father.start_watchdog.assert_called_once()

    pm.terminate_processes()
    assert mock_process.terminate.call_count == 2
    assert mock_process.join.call_count == 2
    mock_father.stop_watchdog.assert_called_once()

@patch("debate.debate.process_manager.multiprocessing.Process")
def test_process_manager_restart(mock_process_cls):
    mock_process = MagicMock()
    mock_process.is_alive.return_value = True
    mock_process_cls.return_value = mock_process

    mock_father = MagicMock()

    pm = ProcessManager(
        session_id="s1", topic="Topic", config={}, gatekeeper=None,
        father=mock_father, f_to_p=None, p_to_f=None, f_to_c=None, c_to_f=None
    )

    pm.start_processes()

    res = pm.restart_child(AgentRole.PRO)
    assert res is True
    assert mock_process.terminate.call_count == 1
    assert mock_process.join.call_count == 1
    assert mock_process.start.call_count == 3

    res2 = pm.restart_child(AgentRole.PRO)
    assert res2 is True

    res3 = pm.restart_child(AgentRole.PRO)
    assert res3 is False

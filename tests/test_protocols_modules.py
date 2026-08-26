"""Unit tests for ProtocolManager, Protocol Capabilities, and Module execution."""

from cmeplus.core.results import ResultState
from cmeplus.core.targets import Target
from cmeplus.modules.manager import ModuleManager
from cmeplus.protocols.manager import ProtocolManager
from cmeplus.protocols.mock import MockProtocol
from cmeplus.protocols.smb import SMBProtocol


def test_protocol_manager_registration():
    mgr = ProtocolManager()
    protocols = mgr.list_protocols()
    assert "smb" in protocols
    assert "ldap" in protocols
    assert "winrm" in protocols
    assert "ssh" in protocols
    assert "mock" in protocols

    smb_cls = mgr.get("smb")
    assert smb_cls is SMBProtocol


def test_protocol_capabilities():
    smb_caps = SMBProtocol.capabilities
    assert smb_caps.can_connect is True
    assert smb_caps.can_enum_shares is True
    assert smb_caps.supports_kerberos is True


def test_module_manager_discovery():
    mgr = ModuleManager()
    all_mods = mgr.list_all()
    assert len(all_mods) >= 3
    mod_names = [m.name for m in all_mods]
    assert "shares" in mod_names
    assert "users" in mod_names
    assert "passpol" in mod_names

    smb_mods = mgr.list_for_protocol("smb")
    assert any(m.name == "shares" for m in smb_mods)


def test_mock_protocol_module_execution():
    target = Target(host="192.168.1.10", port=445)
    proto = MockProtocol(target=target)
    conn_res = proto.connect()
    assert conn_res.status == ResultState.SUCCESS

    mod_res = proto.execute_module("shares", {})
    assert mod_res.status == ResultState.SUCCESS
    assert "shares" in mod_res.data
    assert "ADMIN$" in mod_res.data["shares"]

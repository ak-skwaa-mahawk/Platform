import pytest
from vault.client import VaultClient
from vault.fpt_adapter import FPTIPCClientAdapter

def test_vault_client_uds_factory():
    client = VaultClient.from_uds()
    assert isinstance(client, FPTIPCClientAdapter)
    assert client.het_socket_path.endswith("heterosis.sock")
    assert client.fpt_socket_path.endswith("fpt_kernel.sock")

def test_fpt_adapter_keys():
    client = VaultClient.from_uds()
    assert len(client._public_key_hex) == 64  # 32 bytes hex
    assert len(client.latest_egress_receipt) == 64

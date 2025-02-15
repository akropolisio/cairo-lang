import json
from typing import Any, Dict, List, Optional, Union

from services.everest.api.feeder_gateway.feeder_gateway_client import EverestFeederGatewayClient
from starkware.starknet.definitions import fields
from starkware.starknet.services.api.gateway.transaction import InvokeFunction


class FeederGatewayClient(EverestFeederGatewayClient):
    """
    A client class for the StarkNet FeederGateway.
    """

    async def get_contract_addresses(self) -> Dict[str, str]:
        raw_response = await self._send_request(send_method="GET", uri=f"/get_contract_addresses")
        return json.loads(raw_response)

    async def call_contract(
        self, invoke_tx: InvokeFunction, block_id: Optional[int] = None
    ) -> Dict[str, List[str]]:
        raw_response = await self._send_request(
            send_method="POST",
            uri=f"/call_contract?blockId={json.dumps(block_id)}",
            data=invoke_tx.dumps(),
        )
        return json.loads(raw_response)

    async def get_block(self, block_id: Optional[int] = None) -> Dict[str, Any]:
        raw_response = await self._send_request(
            send_method="GET", uri=f"/get_block?blockId={json.dumps(block_id)}"
        )
        return json.loads(raw_response)

    async def get_code(self, contract_address: int, block_id: Optional[int] = None) -> List[str]:
        uri = f"/get_code?contractAddress={hex(contract_address)}&blockId={json.dumps(block_id)}"
        raw_response = await self._send_request(send_method="GET", uri=uri)
        return json.loads(raw_response)

    async def get_storage_at(
        self, contract_address: int, key: int, block_id: Optional[int] = None
    ) -> str:
        uri = (
            f"/get_storage_at?contractAddress={hex(contract_address)}&key={key}&"
            f"blockId={json.dumps(block_id)}"
        )
        raw_response = await self._send_request(send_method="GET", uri=uri)
        return json.loads(raw_response)

    async def get_transaction_status(
        self, tx_hash: Optional[Union[int, str]], tx_id: Optional[int] = None
    ) -> Dict[str, Any]:
        raw_response = await self._send_request(
            send_method="GET",
            uri=f"/get_transaction_status?{tx_identifier(tx_hash=tx_hash, tx_id=tx_id)}",
        )
        return json.loads(raw_response)

    async def get_transaction(
        self, tx_hash: Optional[Union[int, str]], tx_id: Optional[int] = None
    ) -> str:
        raw_response = await self._send_request(
            send_method="GET", uri=f"/get_transaction?{tx_identifier(tx_hash=tx_hash, tx_id=tx_id)}"
        )
        return json.loads(raw_response)


def format_tx_hash(tx_hash: Union[int, str]) -> str:
    if isinstance(tx_hash, int):
        return fields.TransactionHashField.format(tx_hash)

    assert isinstance(tx_hash, str)
    return tx_hash


def tx_identifier(tx_hash: Optional[Union[int, str]], tx_id: Optional[int]) -> str:
    if tx_hash is not None:
        return f"transactionHash={format_tx_hash(tx_hash)}"
    return f"transactionId={json.dumps(tx_id)}"

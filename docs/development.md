# Developer Guide: Extending CrackMapExec+

This guide explains how to add new protocols and modules to CrackMapExec+.

---

## Adding a New Protocol

1. Create a new file in `src/cmeplus/protocols/<protocol_name>.py`.
2. Inherit from `BaseProtocol` and define `ProtocolCapabilities`.
3. Implement `connect()`, `authenticate()`, `enumerate()`, `close()`, and `get_educational_summary()`.
4. Register your class in `src/cmeplus/protocols/manager.py`.

### Example Template

```python
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities
from cmeplus.core.results import Result, ResultState

class MyProtocol(BaseProtocol):
    name = "myproto"
    default_port = 1234
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
    )

    def connect(self) -> Result:
        # Establish socket connection
        self.is_connected = True
        return Result(target=self.target.endpoint, port=self.port, protocol=self.name, status=ResultState.SUCCESS)

    def authenticate(self) -> Result:
        return Result(target=self.target.endpoint, port=self.port, protocol=self.name, status=ResultState.SUCCESS)

    def enumerate(self) -> Result:
        return Result(target=self.target.endpoint, port=self.port, protocol=self.name, status=ResultState.SUCCESS)

    def close(self) -> None:
        self.is_connected = False

    @classmethod
    def get_educational_summary(cls) -> dict:
        return {
            "protocol": "My Custom Protocol",
            "ports": "1234/TCP",
            "purpose": "Educational custom protocol implementation.",
            "common_concepts": ["Concept A", "Concept B"],
            "lab_guidance": "Test only in authorized labs.",
            "video_topic": "myproto",
        }
```

---

## Adding a New Module

1. Create a module class inheriting from `BaseModule` in `src/cmeplus/modules/builtin/<module_name>.py`.
2. Define `ModuleMetadata` with name, supported protocols, description, and options.
3. Implement `run(protocol_instance)`.
4. Register the module in `ModuleManager`.

---

## Running the Test Suite

```bash
pytest -v tests/
ruff check src/ tests/
```

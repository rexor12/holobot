from typing import Any, Type

class ExportMetadata:
    PROPERTY_NAME: str = "di_export_metadatas"

    def __init__(self, contract_type: Type[Any], export_type: Type[Any]) -> None:
        self.contract_type = contract_type
        self.export_type = export_type

    @property
    def contract_type(self) -> Type[Any]:
        return self.__contract_type

    @contract_type.setter
    def contract_type(self, value: Type[Any]) -> None:
        self.__contract_type = value

    @property
    def export_type(self) -> Type[Any]:
        return self.__export_type

    @export_type.setter
    def export_type(self, value: Type[Any]) -> None:
        self.__export_type = value
    
    def __str__(self) -> str:
        return f"<ExportMetadata contract_type={self.contract_type}, export_type={self.export_type}>"

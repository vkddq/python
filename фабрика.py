from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class Report(Document):
    def render(self) -> str:
        return "Рендер звіту (Report)"

class Invoice(Document):
    def render(self) -> str:
        return "Рендер рахунку (Invoice)"

class Contract(Document):
    def render(self) -> str:
        return "Рендер контракту (Contract)"


class NullDocument(Document):
    def render(self) -> str:
        return "Помилка: невідомий формат документа"

class DocumentFactory:
    @staticmethod
    def create(doc_type: str) -> Document:
        if doc_type == 'report':
            return Report()
        if doc_type == 'invoice':
            return Invoice()
        if doc_type == 'contract':
            return Contract()
        
        return NullDocument()


if __name__ == "__main__":
    doc = DocumentFactory.create('invoice')
    print(doc.render())